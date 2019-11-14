import typing
from typing import List, Tuple  

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
import tqdm 

ROOT = "../"
DATA = os.path.join(ROOT, "data")
TRANS_TABLE = pd.read_csv(os.path.join(ROOT, "data_processing", 'country_codes.csv'))


def add_buildings(graph: PlanarGraph, buildings: List[Tuple]):

    total_blgds = len(buildings)
    #print("\t\tbuildings....")
    for i, bldg_node in enumerate(buildings):
        graph.add_node_to_closest_edge(bldg_node, terminal=True)

    if total_blgds > 0:
        graph.cleanup_linestring_attr()
    return graph 

def clean_graph(graph):
    is_conn = graph.is_connected()
    if is_conn:
        #print("Graph is connected")
        return graph, 1
    else:
        components = graph.components(mode=igraph.WEAK)
        num_components = len(components)
        #print("--DISCONNECTED: has {} components".format(num_components))
        comp_sizes = [len(idxs) for idxs in components]
        arg_max = np.argmax(comp_sizes)
        comp_indices = components[arg_max]

        return graph.subgraph(comp_indices), num_components

def do_reblock(graph: PlanarGraph, buildings: List[Tuple], verbose: bool=False):
    '''
    Given a graph of the Parcel and the corresponding list of buildings (expressed as a list of tuple pairs),
    does the reblocking
    '''

    # Step 1: add the buildings to the PlanarGraph
    start = time.time()
    graph = add_buildings(graph, buildings)
    bldg_time = time.time() - start

    # Step 2: clean the graph if it's disconnected
    graph, num_components = clean_graph(graph)

    # Step 3: do the Steiner Tree approx
    start = time.time()
    graph.steiner_tree_approx()
    stiener_time = time.time() - start 

    # Step 4: convert the stiener edges and terminal nodes to linestrings and points, respecitvely
    #steiner_lines = graph.get_steiner_linestrings()
    new_steiner, existing_steiner = graph.get_steiner_linestrings()
    terminal_points = graph.get_terminal_points()

    if verbose:
        return new_steiner, existing_steiner, terminal_points, [bldg_time, stiener_time, num_components]
    else:
        return new_steiner, existing_steiner, terminal_points

def reblock_gadm(region, gadm_code, gadm, drop_already_completed=True):
    '''
    Does reblocking for an entire GADM boundary
    '''

    # (1) Just load our data for one GADM
    print("Begin loading of data--{}-{}".format(region, gadm))
    parcels, buildings, blocks = i_topology_utils.load_reblock_inputs(region, gadm_code, gadm) 

    buildings.sort_values(by=['building_count'], inplace=True)
    all_blocks = buildings['block_id']

    checkpoint_every = 1
    summary_dict = {}
    steiner_lines_dict = {}
    terminal_points_dict = {}

    # Paths
    reblock_path = os.path.join(DATA, "reblock", region, gadm_code)
    if not os.path.isdir(reblock_path):
        os.makedirs(reblock_path)

    summary_path = os.path.join(reblock_path, "reblock_summary_{}.csv".format(gadm))
    steiner_path = os.path.join(reblock_path, "steiner_lines_{}.geojson".format(gadm))
    terminal_path = os.path.join(reblock_path, "terminal_points_{}.geojson".format(gadm))
    if os.path.exists(summary_path) and drop_already_completed:
        # Drop those we've already done
        prior_work_exists = True
        pre_shape = buildings.shape[0]
        already_done = pd.read_csv(summary_path).rename(columns={'Unnamed: 0':'block_id'}) 
        already_done = already_done[['block_id']]
        buildings = buildings.merge(right=already_done, how='left', on='block_id', indicator=True)
        keep = buildings['_merge'] == 'left_only'
        buildings = buildings[keep]
        new_shape = buildings.shape[0]
        print("Shape {}->{} [lost {} blocks".format(pre_shape, new_shape, pre_shape-new_shape))
        all_blocks = buildings['block_id']
         
    else:
        prior_work_exists = False

    print("\nBegin looping")
    for i, block_id in tqdm.tqdm(enumerate(all_blocks), total=len(all_blocks)):

        parcel_geom = parcels[parcels['block_id']==block_id]['geometry'].iloc[0]
        building_list = buildings[buildings['block_id']==block_id]['buildings'].iloc[0]
        block_geom = blocks[blocks['block_id']==block_id]['geometry'].iloc[0]

        if len(building_list) <= 1:
            continue 

        # (1) Convert parcel geometry to planar graph
        planar_graph = PlanarGraph.multilinestring_to_planar_graph(parcel_geom)

        # (2) Update the edge types based on the block graph
        missing, total_block_coords = i_topology_utils.update_edge_types(planar_graph, block_geom, check=True)

        # (3) Do reblocking 
        try:
            new_steiner, existing_steiner, terminal_points, summary = do_reblock(planar_graph, building_list, verbose=True)
        except:
            new_steiner = None 
            existing_steiner = None 
            terminal_points = None 
            summary = [None, None, None]

        # Collect and store the summary info from reblocking
        summary = summary + [len(building_list), total_block_coords, missing, block_id]
        summary_columns = ['bldg_time', 'steiner_time', 'num_graph_comps'] + ['bldg_count', 'num_block_coords', 'num_block_coords_unmatched', 'block']

        summary_dict[block_id] = summary 
        steiner_lines_dict[block_id+'new_steiner'] = [new_steiner, block_id, 'new_steiner'] 
        steiner_lines_dict[block_id+'existing_steiner'] = [existing_steiner, block_id, 'existing_steiner'] 
        terminal_points_dict[block_id] = [terminal_points, block_id]

        # Save out on first iteration and on checkpoint iterations
        if (i == 0) or (i % checkpoint_every == 0):
            steiner_df = gpd.GeoDataFrame.from_dict(steiner_lines_dict, orient='index', columns=['geometry', 'block_id', 'steiner_type'])
            terminal_df = gpd.GeoDataFrame.from_dict(terminal_points_dict, orient='index', columns=['geometry', 'block_id'])
            summary_df = pd.DataFrame.from_dict(summary_dict, orient='index', columns=summary_columns)

            if i == 0 and prior_work_exists:
                print("ALERT -- loading earlier work and appending new work to this before resaving")
                # Load and append to earlier work
                prior_steiner_df = gpd.read_file(steiner_path)
                prior_terminal_df = gpd.read_file(terminal_path)
                summary_df = pd.read_csv(summary_path)

                steiner_df = pd.concat([prior_steiner_df, steiner_df])
                terminal_df = pd.concat([prior_terminal_df, steiner_df])
                summary_df = pd.concat([prior_summary_df, steiner_df])

            steiner_df.to_file(steiner_path, driver='GeoJSON')
            terminal_df.to_file(terminal_path, driver='GeoJSON')
            summary_df.to_csv(summary_path)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Do reblocking on a GADM')
    parser.add_argument('--region', type=str, required=True, help="region to process")
    parser.add_argument('--gadm_code', type=str, required=True, help="3-digit country gadm code to process")
    parser.add_argument('--gadm', help='process this gadm')

    args = parser.parse_args()
   
    reblock_gadm(**vars(args))


