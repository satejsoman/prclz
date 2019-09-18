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

import topology_utils

region = "Africa"
gadm_code = "SLE"
gadm = "SLE.4.2.1_1"
example_blocks = ["SLE.4.2.1_1_1241", "SLE.4.2.1_1_1120", "SLE.4.2.1_1_965"]

def process_block(graph, buildings):

    print("\nGraph pre-adding building nodes:\n", graph, "\n")
    total_blgds = len(buildings)
    for i, bldg_node in enumerate(buildings):
        bldg_node.terminal = True
        graph.add_node_to_closest_edge(bldg_node)
        print("through {} of {} buildings".format(i, total_blgds))

    print("Graph post-adding building nodes:\n", graph)
    print("Performing Steiner Tree approximation...")
    steiner = example_graph.steiner_tree_approx()
    print("DONE!!\n\n")
    return steiner, example_graph 


# (1) Just load our data for one GADM
print("Begin loading of data")
bldgs, blocks, parcels, lines = topology_utils.load_geopandas_files(region, gadm_code, gadm)

# (2) Now build the parcel graph and prep the buildings
blocks = blocks[blocks['block_id'].apply(lambda x: x in example_blocks)]
parcels = parcels[parcels['block_id'].apply(lambda x: x in example_blocks)]
print("Begin calculating of parcel graphs")
graph_parcels = topology_utils.prepare_parcels(bldgs, blocks, parcels)

if not os.path.isdir("test_SLE"):
    os.mkdir("test_SLE")

# (3) We can grab a graph, and just add the corresponding building Nodes
for example_block in example_blocks:
    print("----BEGIN {}----".format(example_block))
    example_graph = graph_parcels[graph_parcels['block_id']==example_block]['planar_graph'].item()
    example_buildings = graph_parcels[graph_parcels['block_id']==example_block]['buildings'].item()

    steiner, reblocked_graph = process_block(example_graph, example_buildings)

    reblocked_graph.save(os.path.join("test_SLE", example_block+".pg"))
    steiner.save(os.path.join("test_SLE", example_graph+"_steiner.pg"))


# print("\nGraph pre-adding building nodes:\n", example_graph, "\n")
# total_blgds = len(example_buildings)
# for i, bldg_node in enumerate(example_buildings):
#     bldg_node.terminal = True
#     example_graph.add_node_to_closest_edge(bldg_node)
#     print("through {} of {} buildings".format(i, total_blgds))

# print("Graph post-adding building nodes:\n", example_graph)
# steiner = example_graph.steiner_tree_approx()