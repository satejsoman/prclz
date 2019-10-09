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

ROOT = "../"
DATA = os.path.join(ROOT, "data")
TRANS_TABLE = pd.read_csv(os.path.join(ROOT, "data_processing", 'country_codes.csv'))


def add_buildings(graph, buildings):

    total_blgds = len(buildings)
    print("\t\tbuildings....")
    for i, bldg_node in enumerate(buildings):
        graph.add_node_to_closest_edge(bldg_node, terminal=True)

    if total_blgds > 0:
        graph.cleanup_linestring_attr()
    return graph 

def clean_graph(graph):
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

def reblock_gadm(region, gadm_code, gadm):
    '''
    Does reblocking for an entire GADM boundary
    '''

    # (1) Just load our data for one GADM
    print("Begin loading of data--{}-{}".format(region, gadm))
    bldgs, blocks, parcels, lines = i_topology_utils.load_geopandas_files(region, gadm_code, gadm) 

    #### REMOVE THIS -- just for testing
    # bl = "SLE.4.2.1_1_1241"
    # blocks = blocks[blocks['block_id'] == bl]
    # parcels = parcels[parcels['block_id'] == bl]
    ####################################

    # (2) Now build the parcel graph and prep the buildings
    print("Begin calculating of parcel graphs--{}-{}".format(region, gadm))
    graph_parcels = i_topology_utils.prepare_parcels(bldgs, blocks, parcels)    

    # (3) Just set up some paths
    reblock_path = os.path.join(DATA, "reblock", region, gadm_code)
    if not os.path.isdir(reblock_path):
        os.makedirs(reblock_path)
    graph_path = os.path.join(DATA, "graphs", region, gadm_code)
    if not os.path.isdir(graph_path):
        os.makedirs(graph_path)


    # (4) Do the reblocking, by block in the GADM, collecting the optimal paths
    steiner_lines_dict = {}
    terminal_points_dict = {}
    print("Begin calculating of parcel graphs--{}-{}".format(region, gadm))
    for block in blocks['block_id']:
        example_graph = graph_parcels[graph_parcels['block_id']==block]['planar_graph'].item()
        example_buildings = graph_parcels[graph_parcels['block_id']==block]['buildings'].item()
        example_block = blocks[blocks['block_id']==block]['block_geom'].item()

        print("Block = {} | buildings len = {}".format(block, len(example_buildings)))
        if len(example_buildings) <= 1:
            continue

        i_topology_utils.update_edge_types(example_graph, example_block, check=True) 

        steiner_lines, terminal_points, times = do_reblock(example_graph, example_buildings, verbose=True)
        times.append(steiner_lines)
        times.append(block)
        steiner_lines_dict[block] = times 
        terminal_points_dict[block] = [terminal_points, block]

        example_graph.save_planar(os.path.join(graph_path, block+".igraph"))

    # Now save out everything
    steiner_df = gpd.GeoDataFrame.from_dict(steiner_lines_dict, orient='index', columns=['bldg_time', 'steiner_time', 'geometry', 'block_id'])
    terminal_df = gpd.GeoDataFrame.from_dict(terminal_points_dict, orient='index', columns=['geometry', 'block_id'])

    steiner_df.to_file(os.path.join(reblock_path, "steiner_lines_{}.geojson".format(gadm)), driver='GeoJSON')
    terminal_df.to_file(os.path.join(reblock_path, "terminal_points_{}.geojson".format(gadm)), driver='GeoJSON')

def main(file_path:str, replace):
    
    # (1) Get the GADM code
    f = file_path.split("/")[-1]
    gadm_split = f.split("_")
    if len(gadm_split) == 3:
        gadm = gadm_split[1] + "_1"
    elif len(gadm_split) == 2:
        gadm = gadm_split[0] + "_1"
    else:
        print("Check input!")

    gadm_code = gadm[0:3]
    region = TRANS_TABLE[TRANS_TABLE['gadm_name']==gadm_code]['region'].iloc[0]

    print("region = {}".format(region))
    print("gadm_code = {}".format(gadm_code))
    print("gadm = {}".format(gadm))
   
    reblock_gadm(region, gadm_code, gadm )

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", help="path to a GADM-specific parcels or blocks file", type=str)
    parser.add_argument("--replace", help="default behavior is to skip if the GADM has been processed. Adding this option replaces the files",
                         action="store_true")
    
    args = parser.parse_args()
    main(file_path = args.file_path, replace=args.replace)



