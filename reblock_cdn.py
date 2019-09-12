import typing 

import geopandas as gpd
from shapely.geometry import MultiPolygon, Polygon, MultiLineString, Point, LineString
from shapely.ops import cascaded_union
from shapely.wkt import loads
import pandas as pd
import numpy as np 
import time 

import os 
import matplotlib.pyplot as plt 
import sys 

import argparse

# DEFINE GLOBAL PATHS
ROOT = "."
DATA_PATH = os.path.join(ROOT, "data")

BLOCK_PATH = os.path.join(DATA_PATH, "blocks")
BLDGS_PATH = os.path.join(DATA_PATH, "buildings")
PARCELS_PATH = os.path.join(DATA_PATH, "parcels")

# some test params
region = "Africa"
gadm_code = "SLE"
gadm = "SLE.2.2.5_1"

from prclz.topology import Node, Edge, PlanarGraph

### HELPER FUNCTIONS TO CONVERT shapely geometries INTO CLASSES USED
### IN topology.py
def linestring_to_planar_graph(inestring: LineString) -> PlanarGraph:
    '''
    Helper function to convert a single Shapely linestring
    to a PlanarGraph
    '''

    # linestring -> List[Nodes]
    nodes = [Node(p) for p in linestring.coords]

    # List[Nodes] -> List[Edges]
    nodes.append(nodes[0])
    edges = []
    for i, n in enumerate(nodes):
        if i==0:
            continue
        else:
            edges.append(Edge((n, nodes[i-1])))

    # List[Edges] -> PlanarGraph
    pgraph = PlanarGraph.from_edges(edges)

    return pgraph 

def multilinestring_to_planar_graph(multilinestring: MultiLineString) -> PlanarGraph:
    '''
    Helper function to convert a Shapely multilinestring
    to a PlanarGraph
    '''

    pgraph = PlanarGraph()

    for linestring in multilinestring:
        # linestring -> List[Nodes]
        nodes = [Node(p) for p in linestring.coords]

        # List[Nodes] -> List[Edges]
        nodes.append(nodes[0])
        for i, n in enumerate(nodes):
            if i==0:
                continue
            else:
                pgraph.add_edge(Edge((n, nodes[i-1])))

    return pgraph

def point_to_node(point: Point) -> Node:
    '''
    Helper function to convert shapely.Point -> Node
    '''
    return Node(point.coords[0])
######## END OF CONVERSION HELPERS to topology.py

def csv_to_geo(csv_path, add_file_col=False):
    '''
    Loads the csv and returns a GeoDataFrame
    '''

    df = pd.read_csv(csv_path, usecols=['block_id', 'geometry'])

    # Block id should unique identify each block
    assert df['block_id'].is_unique, "Loading {} but block_id is not unique".format(csv_path)

    df.rename(columns={"geometry":"block_geom"}, inplace=True)
    df['block_geom'] = df['block_geom'].apply(loads)

    if add_file_col:
        f = csv_path.split("/")[-1]
        df['gadm_code'] = f.replace("blocks_", "").replace(".csv", "")

    return gpd.GeoDataFrame(df, geometry='block_geom')

def load_geopandas_files(region: str, gadm_code: str, 
                         gadm: str) -> (gpd.GeoDataFrame, gpd.GeoDataFrame, gpd.GeoDataFrame):

    bldgs_path = os.path.join(BLDGS_PATH, region, gadm_code, "buildings_{}.geojson".format(gadm))
    parcels_path = os.path.join(PARCELS_PATH, region, gadm_code, "parcels_{}.geojson".format(gadm))
    blocks_path = os.path.join(BLOCK_PATH, region, gadm_code, "blocks_{}.csv".format(gadm))

    bldgs = gpd.read_file(bldgs_path)
    blocks = csv_to_geo(blocks_path)
    parcels = gpd.read_file(parcels_path)

    return bldgs, blocks, parcels 

def prepare_parcels(bldgs: gpd.GeoDataFrame, blocks: gpd.GeoDataFrame, 
                                               parcels: gpd.GeoDataFrame) -> pd.DataFrame:
    '''
    For a single GADM, this script (1) creates the PlanarGraph associated
    with each respective parcel and (2) maps all buildings to their corresponding
    parcel. The buildings are converted to centroids and then to Node types so
    they can just be added to the PlanarGraph
    '''

    # Convert buildings to centroids
    bldgs['centroids'] = bldgs['geometry'].centroid
    bldgs.set_geometry('centroids', inplace=True)

    # We want to map each building to a given block to then map the buildings to a parcel
    bldgs = gpd.sjoin(bldgs, blocks, how='left', op='within')
    bldgs.drop(columns=['index_right'], inplace=True)

    # Now, join the parcels with the buildings
    parcels = parcels.merge(bldgs[['block_id', 'centroids']], how='left', on='block_id')
    parcels.rename(columns={'geometry':'parcel_geometry', 'centroids':'buildings'}, inplace=True)

    # Now collapse on the block and clean
    parcels = parcels.groupby('block_id').agg(list)
    parcels['parcel_geometry'] = parcels['parcel_geometry'].apply(lambda x: x[0])
    parcels['buildings'] = parcels['buildings'].apply(lambda x: [] if x==[np.nan] else x)

    # Checks
    assert blocks.shape[0] == parcels.shape[0]  # We should maintain block count
    parcels['buildings_count'] = parcels['buildings'].apply(lambda x: len(x))
    assert parcels['buildings_count'].sum() == bldgs.shape[0]  # We should maintain bldgs count

    parcels.reset_index(inplace=True)

    # Now, create the graph for each parcel
    parcels['planar_graph'] = parcels['parcel_geometry'].apply(multilinestring_to_planar_graph)

    # And convert the buildings from shapely.Points -> topology.Nodes
    parcels['buildings'] = parcels['buildings'].apply(lambda x: [point_to_node(p) for p in x])

    return parcels 

# Just load our data for one GADM in Sierra Leone
bldgs, blocks, parcels = load_geopandas_files(region, gadm_code, gadm)

# Now build the parcel graph and prep the buildings
graph_parcels = prepare_parcels(bldgs, blocks, parcels)

# We can grab a graph, and just add the corresponding building Nodes
example_graph = graph_parcels.iloc[3]['planar_graph']
example_buildings = graph_parcels.iloc[3]['buildings']

print("\nGraph pre-adding building nodes:\n", example_graph, "\n")
total_blgds = len(example_buildings)
for i, bldg_node in enumerate(example_buildings):
    bldg_node.terminal = True
    example_graph.add_node_to_closest_edge(bldg_node)
    print("through {} of {} buildings".format(i, total_blgds))

print("Graph post-adding building nodes:\n", example_graph)
steiner = example_graph.steiner_tree_approx()
example_graph.plot_reblock()

# We just need to adjust the building centroid, but Geoefs function doesn't work for me

import osmnx as ox 
import networkx as nx 
def test_osmnx():
    graph = nx.Graph()
    graph.add_edge((0,1), (0,0))

    geo, u, v, = ox.utils.get_nearest_edge(graph, (0.5,0.5))