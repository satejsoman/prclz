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
import igraph

import i_topology_utils
from i_topology import *
import time 

region = "Africa"
gadm_code = "SLE"
gadm = "SLE.4.2.1_1"
#example_blocks = ["SLE.4.2.1_1_1241", "SLE.4.2.1_1_1120", "SLE.4.2.1_1_965"]
example_blocks = ["SLE.4.2.1_1_1241"]

# region = "Africa"
# gadm_code = "DJI"
# gadm = "DJI.3.1_1"
# example_blocks = ['DJI.3.1_1_26']

def add_buildings(graph, buildings):

    total_blgds = len(buildings)
    for i, bldg_node in enumerate(buildings):
        graph.add_node_to_closest_edge(bldg_node, terminal=True)
        print("through {} of {} buildings".format(i, total_blgds))

    return graph 

def clean_graph(graph):
    #print("Graph has {} self-loops".format(graph.number_of_selfloops()))
    is_conn = graph.is_connected()
    if is_conn:
        print("Graph is connected")
        return graph 
    else:
        #components = list(nx.connected_component_subgraphs(graph))
        components = graph.components(mode=igraph.WEAK)
        num_components = len(components)
        print("--DISCONNECTED: has {} components".format(num_components))
        comp_sizes = [len(idxs) for idxs in components]
        arg_max = np.argmax(comp_sizes)
        comp_indices = components[arg_max]

        return graph.subgraph(comp_indices)

def do_reblock(graph: PlanarGraph, buildings, verbose=False):
    '''
    Given a graph of the Parcel and the corresponding buildings,
    does the reblocking
    '''

    # Step 1: add the buildings to the PlanarGraph
    start = time.time()
    graph = add_buildings(graph, buildings)
    bldg_time = time.time() - start

    # Step 2: clean the graph if it's disconnected
    graph = clean_graph(graph)

    # Step 3: do the Steiner Tree approx
    start = time.time()
    graph.steiner_tree_approx()
    stiener_time = time.time() - start 

    # Step 4: convert the stiener edges and terminal nodes to linestrings and points, respecitvely
    steiner_lines = graph.get_steiner_linestrings()
    terminal_points = graph.get_terminal_points()

    if verbose:
        return steiner_lines, terminal_points, [bldg_time, stiener_time]
    else:
        return steiner_lines, terminal_points


# (1) Just load our data for one GADM
print("Begin loading of data")
bldgs, blocks, parcels, lines = i_topology_utils.load_geopandas_files(region, gadm_code, gadm)

# (2) Now build the parcel graph and prep the buildings
# restrict to some example blocks within the GADM
blocks = blocks[blocks['block_id'].apply(lambda x: x in example_blocks)]
parcels = parcels[parcels['block_id'].apply(lambda x: x in example_blocks)]
print("Begin calculating of parcel graphs")
graph_parcels = i_topology_utils.prepare_parcels(bldgs, blocks, parcels)

if not os.path.isdir("test_SLE_igraph"):
    os.mkdir("test_SLE_igraph")


# (3) Do the reblocking, by block in the GADM, collecting the optimal paths
steiner_lines_dict = {}
terminal_points_dict = {}
for block in blocks['block_id']:
    print("----BEGIN {}----".format(block))
    example_graph = graph_parcels[graph_parcels['block_id']==block]['planar_graph'].item()
    example_buildings = graph_parcels[graph_parcels['block_id']==block]['buildings'].item()
    example_block = blocks[blocks['block_id']==block]['block_geom'].item()

    i_topology_utils.update_edge_types(example_graph, example_block, check=True)
    BOOM 

    steiner_lines, terminal_points, times = do_reblock(example_graph, example_buildings, verbose=True)
    times.append(steiner_lines)
    steiner_lines_dict[block] = times 
    terminal_points_dict[block] = [terminal_points]

    example_graph.save_planar(os.path.join("test_SLE_igraph", block+".igraph"))

# Now save out everything
print("Stiner dict ")
print(steiner_lines_dict)

print("Termianl poitns dict ")
print(terminal_points_dict)

steiner_df = gpd.GeoDataFrame.from_dict(steiner_lines_dict, orient='index', columns=['bldg_time', 'steiner_time', 'geometry'])
terminal_df = gpd.GeoDataFrame.from_dict(terminal_points_dict, orient='index', columns=['geometry'])
steiner_df.to_file(os.path.join("test_SLE_igraph", "steiner_lines.geojson"), driver='GeoJSON')
terminal_df.to_file(os.path.join("test_SLE_igraph", "terminal_points.geojson"), driver='GeoJSON')
