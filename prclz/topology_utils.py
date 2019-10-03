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
from topology import Node, Edge, PlanarGraph

# DEFINE GLOBAL PATHS
ROOT = "../"
DATA_PATH = os.path.join(ROOT, "data")

BLOCK_PATH = os.path.join(DATA_PATH, "blocks")
BLDGS_PATH = os.path.join(DATA_PATH, "buildings")
PARCELS_PATH = os.path.join(DATA_PATH, "parcels")
LINES_PATH = os.path.join(DATA_PATH, "lines")

# some test params
# region = "Africa"
# gadm_code = "SLE"
# gadm = "SLE.2.2.5_1"
# region = "Africa"
# gadm_code = "DJI"
# gadm = "DJI.3.1_1"
# example_block = 'DJI.3.1_1_26'


### HELPER FUNCTIONS TO CONVERT shapely geometries INTO CLASSES USED
### IN topology.py
def linestring_to_planar_graph(linestring: LineString, append_connection=True) -> PlanarGraph:
    '''
    Helper function to convert a single Shapely linestring
    to a PlanarGraph
    '''

    # linestring -> List[Nodes]
    nodes = [Node(p) for p in linestring.coords]

    # List[Nodes] -> List[Edges]
    if append_connection:
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
    lines_path = os.path.join(LINES_PATH, region, gadm_code, "lines_{}.geojson".format(gadm))
    parcels_path = os.path.join(PARCELS_PATH, region, gadm_code, "parcels_{}.geojson".format(gadm))
    blocks_path = os.path.join(BLOCK_PATH, region, gadm_code, "blocks_{}.csv".format(gadm))

    bldgs = gpd.read_file(bldgs_path)
    blocks = csv_to_geo(blocks_path)
    parcels = gpd.read_file(parcels_path)
    lines = gpd.read_file(lines_path)

    return bldgs, blocks, parcels, lines

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
    #assert parcels['buildings_count'].sum() == bldgs.shape[0]  # We should maintain bldgs count

    parcels.reset_index(inplace=True)

    # Now, create the graph for each parcel
    parcels['planar_graph'] = parcels['parcel_geometry'].apply(multilinestring_to_planar_graph)

    # And convert the buildings from shapely.Points -> topology.Nodes
    parcels['buildings'] = parcels['buildings'].apply(lambda x: [point_to_node(p) for p in x])

    return parcels 


def edge_list_from_linestrings(lines_df):
    '''
    Extract the geometry from 
    '''
    all_edges = []
    lines_df_geom = lines_df.geometry 
    for l in lines_df_geom:
        l_graph = linestring_to_planar_graph(l, False)
        #l_graph_edges = [Edge(e) for e in l_graph.edges]
        l_graph_edges = [e for e in l_graph.edges]
        all_edges.extend(l_graph_edges)
    return all_edges


def update_graph_with_edge_type(graph, lines:gpd.GeoDataFrame):
    '''
    Split the lines DataFrame into lists of edges of type 'waterway', 'highway', 
    and 'natural'. Then loop over the graph's edges and update the weights 
    and the edge_type accordingly
    '''

    waterway_edges = edge_list_from_linestrings(lines[lines['waterway'].notna()])
    natural_edges = edge_list_from_linestrings(lines[lines['natural'].notna()])
    highway_edges = edge_list_from_linestrings(lines[lines['highway'].notna()])

    for u, v, edge_data in graph.edges(data=True):
        edge_tuple = (u,v)
        if edge_tuple in waterway_edges:
            edge_data['weight'] = 999
            edge_data['edge_type'] = "waterway"     
        elif edge_tuple in natural_edges:
            edge_data['weight'] = 999
            edge_data['edge_type'] = "natural" 
        elif edge_tuple in highway_edges:
            edge_data['weight'] = 0
            edge_data['edge_type'] = "highway" 
        else:
            edge_data['edge_type'] = "parcel"



if __name__ == "__main__":

    #########################################
    waterway_edges = edge_list_from_linestrings(example_lines[example_lines['waterway'].notna()])
    natural_edges = edge_list_from_linestrings(example_lines[example_lines['natural'].notna()])
    highway_edges = edge_list_from_linestrings(example_lines[example_lines['highway'].notna()])

    for u, v, edge_data in example_graph.edges(data=True):
        edge_tuple = (u,v)
        if edge_tuple in waterway_edges:
            edge_data['weight'] = 999
            edge_data['edge_type'] = "waterway"     
        elif edge_tuple in natural_edges:
            edge_data['weight'] = 999
            edge_data['edge_type'] = "natural" 
        elif edge_tuple in highway_edges:
            edge_data['weight'] = 0
            edge_data['edge_type'] = "highway" 
        else:
            edge_data['edge_type'] = "parcel"

    #########################################



    # (1) Just load our data for one GADM
    bldgs, blocks, parcels, lines = load_geopandas_files(region, gadm_code, gadm)

    # (2) Now build the parcel graph and prep the buildings
    graph_parcels = prepare_parcels(bldgs, blocks, parcels)

    # (3) We can grab a graph, and just add the corresponding building Nodes
    example_graph = graph_parcels[graph_parcels['block_id']==example_block]['planar_graph'].item()
    example_buildings = graph_parcels[graph_parcels['block_id']==example_block]['buildings'].item()

    print("\nGraph pre-adding building nodes:\n", example_graph, "\n")
    total_blgds = len(example_buildings)
    for i, bldg_node in enumerate(example_buildings):
        bldg_node.terminal = True
        example_graph.add_node_to_closest_edge(bldg_node)
        print("through {} of {} buildings".format(i, total_blgds))

    print("Graph post-adding building nodes:\n", example_graph)

    # (4) Now we take out example graph and update the weights on those edges
    example_lines = lines[lines['block_id']==example_block]
    #update_graph_with_edge_type(example_graph, example_lines)
     
    #steiner = example_graph.steiner_tree_approx()
    #example_graph.plot_reblock()

    # Graph snippet
    ax = parcels[parcels['block_id']==block_id].plot(color='blue', alpha=0.5)
    lines[(lines['block_id']==block_id)&lines['waterway'].notna()].plot(ax=ax, color='blue')
    lines[(lines['block_id']==block_id)&lines['highway'].notna()].plot(ax=ax, color='black')
    lines[(lines['block_id']==block_id)&lines['natural'].notna()].plot(ax=ax, color='green')

    fig, axes = plt.subplots(nrows=1, ncols=2)

    # Plot the lines
    lines[(lines['block_id']==block_id)&lines['waterway'].notna()].plot(ax=axes[0], color='blue')
    lines[(lines['block_id']==block_id)&lines['highway'].notna()].plot(ax=axes[1], color='black')
    lines[(lines['block_id']==block_id)&lines['natural'].notna()].plot(ax=axes[0], color='green')

    # Plot the resulting block
    #blocks[blocks['block_id']==block_id].plot(ax=axes[1], color='black')

    # Plot the resulting parcel
    parcels[parcels['block_id']==block_id].plot(ax=axes[1], color='black')


    waterway_edges = edge_list_from_linestrings(lines[(lines['block_id']==block_id)&lines['waterway'].notna()])
    natural_edges = edge_list_from_linestrings(lines[(lines['block_id']==block_id)&lines['natural'].notna()])
    highway_edges = edge_list_from_linestrings(lines[(lines['block_id']==block_id)&lines['highway'].notna()])