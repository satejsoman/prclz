from typing import Iterable 

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
from .topology import Node, Edge, PlanarGraph
from .utils import edge_list_from_linestrings

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