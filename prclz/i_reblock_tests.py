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

BLOCKS_TO_DO = gpd.read_file(os.path.join(ROOT, "reblock_sle_lbr_hti.geojson"))


def add_buildings_slow(graph, buildings):

    total_blgds = len(buildings)
    print("\t\tbuildings....")
    for i, bldg_node in enumerate(buildings):
        print("{}/{}".format(i, total_blgds))
        graph.add_node_to_closest_edge(bldg_node, terminal=True, fast=False)

    return graph

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
        return graph, 1
    else:
        #components = list(nx.connected_component_subgraphs(graph))
        components = graph.components(mode=igraph.WEAK)
        num_components = len(components)
        print("--DISCONNECTED: has {} components".format(num_components))
        comp_sizes = [len(idxs) for idxs in components]
        arg_max = np.argmax(comp_sizes)
        comp_indices = components[arg_max]

        return graph.subgraph(comp_indices), num_components

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

    # if verbose:
    #     return steiner_lines, terminal_points, [bldg_time, stiener_time, num_components]
    # else:
    #     return steiner_lines, terminal_points

def check_consistent(lines: MultiLineString, block: Polygon):

    line_coord_set = set()
    for l in lines:
        for coord in l.coords:
            line_coord_set.add(coord)
    # Now check
    total = 0
    within = 0
    for coord in block.exterior.coords:
        b = 1 if coord in line_coord_set else 0
        total += 1
        within += b 
    print("{}/{} block coords are in the linestring coords".format(within, total))

def debug(region, gadm_code, gadm):
    
    # (1) Just load our data for one GADM
    print("Begin loading of data--{}-{}".format(region, gadm))
    bldgs, blocks, parcels, lines = i_topology_utils.load_geopandas_files(region, gadm_code, gadm) 

    blocks = blocks[blocks['block_id']=='KEN.30.10.1_1_1']
    parcels = parcels[parcels['block_id']=='KEN.30.10.1_1_1']
    lines = lines[lines['block_id']=='KEN.30.10.1_1_1']

    # (2) Now build the parcel graph and prep the buildings
    print("Begin calculating of parcel graphs--{}-{}".format(region, gadm))
    graph_parcels = i_topology_utils.prepare_parcels(bldgs, blocks, parcels)    

    return bldgs, blocks, parcels, graph_parcels, lines 

def reblock_gadm(region, gadm_code, gadm, chunk, total_chunks):
    '''
    Does reblocking for an entire GADM boundary
    '''

    # (1) Just load our data for one GADM
    print("Begin loading of data--{}-{}".format(region, gadm))
    #bldgs, blocks, parcels, lines = i_topology_utils.load_geopandas_files(region, gadm_code, gadm) 
    bldgs, blocks, parcels, _ = i_topology_utils.load_geopandas_files(region, gadm_code, gadm) 

    LIMIT = True
    if LIMIT:
        print("\n\nLimit blocks to specified...")
        print("PRE-LIMIT: Block count = {} | Parcel count = {}".format(blocks.shape[0], parcels.shape[0]))
        blocks_to_do = set(b for b in BLOCKS_TO_DO['block_id'] if gadm_code in b)
        fn = lambda x: x in blocks_to_do
        block_keep = blocks['block_id'].apply(fn)    
        parcels_keep = parcels['block_id'].apply(fn) 

        blocks = blocks[block_keep]
        parcels = parcels[parcels_keep]   


    # (1-a) 
    if chunk is not None:
        print("\n\nBegin chunking...")
        print("PRE: Block count = {} | Parcel count = {}".format(blocks.shape[0], parcels.shape[0]))
        # Sort blocks
        blocks.sort_values('block_id', ascending=False, inplace=True)
        cur_blocks = []
        for i, block_id in enumerate(blocks['block_id']):
            assignment = i % total_chunks
            if assignment == chunk:
                cur_blocks.append(block_id)
        #print("Processing {} of {} total blocks".format(len(cur_blocks), blocks['block_id']))

        fn = lambda x: x in cur_blocks
        block_keep = blocks['block_id'].apply(fn)    
        parcels_keep = parcels['block_id'].apply(fn) 

        blocks = blocks[block_keep]
        parcels = parcels[parcels_keep]   

        print("POST: Block count = {} | Parcel count = {}".format(blocks.shape[0], parcels.shape[0]))

    #### REMOVE THIS -- just for testing
    # bl = "SLE.4.2.1_1_1241"
    # blocks = blocks[blocks['block_id'] == bl]
    # parcels = parcels[parcels['block_id'] == bl]
    ####################################

    # (2) Now build the parcel graph and prep the buildings
    print("Begin calculating of parcel graphs--{}-{}".format(region, gadm))
    graph_parcels = i_topology_utils.prepare_parcels(bldgs, blocks, parcels)    

    # (3) Just set up some paths
    if chunk is not None:
        reblock_path = os.path.join(DATA, "reblock", region, gadm_code+"-{}".format(chunk))
    else:
        reblock_path = os.path.join(DATA, "reblock", region, gadm_code)
    if not os.path.isdir(reblock_path):
        os.makedirs(reblock_path)
    graph_path = os.path.join(DATA, "graphs", region, gadm_code)
    if not os.path.isdir(graph_path):
        os.makedirs(graph_path)
    print(reblock_path)

    # (4) Do the reblocking, by block in the GADM, collecting the optimal paths
    steiner_lines_dict = {}
    terminal_points_dict = {}
    summary_dict = {}
    print("Begin calculating of parcel graphs--{}-{}".format(region, gadm))
    for block in blocks['block_id']:
        example_graph = graph_parcels[graph_parcels['block_id']==block]['planar_graph'].item()
        example_buildings = graph_parcels[graph_parcels['block_id']==block]['buildings'].item()
        example_block = blocks[blocks['block_id']==block]['block_geom'].item()
        #example_lines = lines[lines['block_id']==block]

        print("Block = {} | buildings len = {}".format(block, len(example_buildings)))
        if len(example_buildings) <= 1:
            continue

        # One wonky block in KEN, just skip for now, doesn't seem to be systematic
        if block == 'KEN.30.11.2_1_437':
            continue

        # Update edge types -- first check if the linestrings have natural/waterway or if they're all highways
        # This is WIP
        #if np.all(example_lines['highway']!=""):
        if 1:
            missing, total_block_coords = i_topology_utils.update_edge_types(example_graph, example_block, check=True)
        else:
            lines_pgraph = i_topology_utils.create_lines_graph(example_lines)
            missing, total_block_coords = i_topology_utils.update_edge_types(example_graph, example_block, check=True, lines_pgraph=lines_pgraph)

        # Do reblocking 
        try:
            #steiner_lines, terminal_points, summary = do_reblock(example_graph, example_buildings, verbose=True)
            new_steiner, existing_steiner, terminal_points, summary = do_reblock(example_graph, example_buildings, verbose=True)
        except:
            new_steiner = None 
            existing_steiner = None 
            terminal_points = None 
            summary = [None, None, None]
        
        # Collect and store the summary info from reblocking
        summary = summary + [len(example_buildings), total_block_coords, missing, block]
        summary_columns = ['bldg_time', 'steiner_time', 'num_graph_comps'] + ['bldg_count', 'num_block_coords', 'num_block_coords_unmatched', 'block']

        summary_dict[block] = summary 
        steiner_lines_dict[block+'new_steiner'] = [new_steiner, block, 'new_steiner'] 
        steiner_lines_dict[block+'existing_steiner'] = [existing_steiner, block, 'existing_steiner'] 
        terminal_points_dict[block] = [terminal_points, block]

        if chunk is not None:
            dict_block = {}
            if len(existing_steiner) != 0:
                dict_block[block+'existing_steiner'] = [existing_steiner, block, 'existing_steiner']
            if len(new_steiner) != 0:
                dict_block[block+'new_steiner'] = [new_steiner, block, 'new_steiner'] 
            #dict_block[block+'new_steiner'] = [new_steiner, block, 'new_steiner'] 
            #dict_block[block+'existing_steiner'] = [existing_steiner, block, 'existing_steiner'] 
            block_df = gpd.GeoDataFrame.from_dict(dict_block, orient='index', columns=['geometry', 'block_id', 'steiner_type'])
            # print("\n\nHERE")
            # print(block_df.columns)
            # print(block_df.geometry)
            # print("\nPrinting types")
            # for g in block_df.geometry:
            #     print(type(g))
            block_df.to_file(os.path.join(reblock_path, "{}_steiner_lines_{}.geojson".format(block_id, gadm)), driver='GeoJSON')


        example_graph.save_planar(os.path.join(graph_path, block+".igraph"))

    # Now save out everything
    steiner_df = gpd.GeoDataFrame.from_dict(steiner_lines_dict, orient='index', columns=['geometry', 'block_id', 'steiner_type'])
    # print("\n\nHERE")
    # print(steiner_df.columns)
    # for g in steiner_df.geometry:
    #     print(type(g))

    terminal_df = gpd.GeoDataFrame.from_dict(terminal_points_dict, orient='index', columns=['geometry', 'block_id'])
    summary_df = pd.DataFrame.from_dict(summary_dict, orient='index', columns=summary_columns)

    steiner_df.to_file(os.path.join(reblock_path, "steiner_lines_{}.geojson".format(gadm)), driver='GeoJSON')
    terminal_df.to_file(os.path.join(reblock_path, "terminal_points_{}.geojson".format(gadm)), driver='GeoJSON')
    summary_df.to_csv(os.path.join(reblock_path, "reblock_summary_{}.csv".format(gadm)))

def main(file_path:str, replace, chunk=None, total_chunks=None ):
    
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
    region = TRANS_TABLE[TRANS_TABLE['gadm_name']==gadm_code]['geofabrik_region'].iloc[0].title()

    print("region = {}".format(region))
    print("gadm_code = {}".format(gadm_code))
    print("gadm = {}".format(gadm))
   
    reblock_gadm(region, gadm_code, gadm, chunk, total_chunks )

def convert_to_gpd(g):

    if 'edge_type' not in g.es.attributes():
        g.es['edge_type'] = None 

    edge_geom = [LineString(g.edge_to_coords(e)) for e in g.es]
    edge_types = g.es['edge_type']

    df = pd.DataFrame(data={'geometry':edge_geom, 'edge_type': edge_types})
    return gpd.GeoDataFrame(df)

def plot_types(g):

    edge_color_map = {None: 'red', 'waterway': 'blue', 
                      'highway': 'black', 'natural': 'green', 'gadm_boundary': 'orange'}
    ax = g[g['edge_type'].isna()].plot(color='red')

    for t in g.edge_type.unique():
        d = g[g['edge_type'] == t]
        if d.shape[0] > 0:
            d.plot(ax=ax, color=edge_color_map[t])


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", help="path to a GADM-specific parcels or blocks file", type=str)
    parser.add_argument("--replace", help="default behavior is to skip if the GADM has been processed. Adding this option replaces the files",
                         action="store_true")
    parser.add_argument("--total_chunks", help="break into this many sub-pieces", type=int, default=None)
    parser.add_argument("--chunk_num", help="chunk id", type=int, default=None)
    
    args = parser.parse_args()

    if args.total_chunks is not None and args.chunk_num is None:
        for cur_chunk in range(args.total_chunks):
            main(file_path = args.file_path, replace=args.replace, chunk=cur_chunk, total_chunks=args.total_chunks)
    elif args.total_chunks is not None and args.chunk_num is not None:
        main(file_path = args.file_path, replace=args.replace, chunk=args.chunk_num, total_chunks=args.total_chunks)
    else:
        main(file_path = args.file_path, replace=args.replace)

    # region = 'Africa'
    # gadm_code = 'KEN'
    # gadm = 'KEN.30.10.1_1'

    # bldgs, blocks, parcels, graph_parcels, lines = debug(region, gadm_code, gadm)
    # g = graph_parcels['planar_graph'].iloc[0]
    # block = blocks['block_geom'].iloc[0]

    # #g_pre = convert_to_gpd(g)

    # lines_pgraph = i_topology_utils.create_lines_graph(lines)
    # missing, total = i_topology_utils.update_edge_types(g, block, True, lines_pgraph)
        
    #plot_post = plot_edge_type(g, 'post_update_edge.png')
    # g_lines = g.get_linestrings()  
    # parcel = gpd.GeoSeries(graph_parcels['parcel_geometry'].iloc[0])   
    # g_lines_geo = gpd.GeoSeries(g_lines)

    # ax = parcel.plot(color='blue', alpha=0.5)
    # g_lines_geo.plot(color='blue', alpha=0.5, ax=ax)
    # plt.show()