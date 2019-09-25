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
import time 

region = "Africa"
gadm_code = "SLE"
gadm = "SLE.4.2.1_1"
#example_blocks = ["SLE.4.2.1_1_1241", "SLE.4.2.1_1_1120", "SLE.4.2.1_1_965"]
example_blocks = ["SLE.4.2.1_1_1241"]

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

        return components[arg_max]


# (1) Just load our data for one GADM
print("Begin loading of data")
bldgs, blocks, parcels, lines = i_topology_utils.load_geopandas_files(region, gadm_code, gadm)

# (2) Now build the parcel graph and prep the buildings
blocks = blocks[blocks['block_id'].apply(lambda x: x in example_blocks)]
parcels = parcels[parcels['block_id'].apply(lambda x: x in example_blocks)]
print("Begin calculating of parcel graphs")
graph_parcels = i_topology_utils.prepare_parcels(bldgs, blocks, parcels)

if not os.path.isdir("test_SLE_igraph"):
    os.mkdir("test_SLE_igraph")


# (3) We can grab a graph, and just add the corresponding building Nodes
for example_block in example_blocks:
    print("----BEGIN {}----".format(example_block))
    example_graph = graph_parcels[graph_parcels['block_id']==example_block]['planar_graph'].item()
    example_buildings = graph_parcels[graph_parcels['block_id']==example_block]['buildings'].item()

    t = time.time()
    example_graph = add_buildings(example_graph, example_buildings)
    print("\t\tbuildings take = {} secs".format(time.time()-t))
    
    example_graph = clean_graph(example_graph)

    t = time.time()
    print("Performing Steiner Tree approximation...")
    example_graph.steiner_tree_approx()
    print("DONE!!\n\n")    
    print("\t\tsteiner approx take = {} secs".format(time.time()-t))

    example_graph.save_planar(os.path.join("test_SLE_igraph", example_block+".igraph"))
