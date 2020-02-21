import typing
from typing import List, Tuple  

from pathlib import Path 
import geopandas as gpd
from shapely.geometry import MultiPolygon, Polygon, MultiLineString, Point, LineString
from shapely.ops import cascaded_union, polygonize
from shapely.wkt import loads, dumps
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

def get_optimal_path(graph: PlanarGraph, buildings: List[Tuple], simplify: bool=False, verbose: bool=False):
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

    node_count_pre = len(graph.vs)
    edge_count_pre = len(graph.es)

    # Step 3: do the Steiner Tree approx
    if simplify:
        start = time.time()
        graph.simplify()
        simplify_time = time.time() - start 
        node_count_post = len(graph.vs)
        edge_count_post = len(graph.es)
    else:
        simplify_time = 0
        node_count_post = node_count_pre 
        edge_count_post = edge_count_pre
        
    start = time.time()
    graph.steiner_tree_approx()
    steiner_time = time.time() - start 

    # Step 4: convert the stiener edges and terminal nodes to linestrings and points, respecitvely
    #steiner_lines = graph.get_steiner_linestrings()
    new_steiner, existing_steiner = graph.get_steiner_linestrings()
    terminal_points = graph.get_terminal_points()
        # summary_columns = [      'bldg_time',       'simplify_time',     'steiner_time', 'num_graph_comps',  
        #                     'node_count_pre',     'node_count_post',   'edge_count_pre', 'edge_count_post',
        #                         'bldg_count',    'num_block_coords', 'num_block_coords_unmatched',  'block']

    if verbose:
        summary = [bldg_time, simplify_time, steiner_time, num_components, node_count_pre, node_count_post, edge_count_pre, edge_count_post]
        return new_steiner, existing_steiner, terminal_points, summary 
    else:
        return new_steiner, existing_steiner, terminal_points

class CheckPointer:
    '''
    Small container class which handles saving of work, checking if
    prior work exists, etc
    '''

    def __init__(self, region: str, gadm: str, gadm_code: str, drop_already_completed: bool, digital_globe_data:bool):

        reblock_stub = "dg_reblock" if digital_globe_data else "reblock"

        self.reblock_path = os.path.join(DATA, reblock_stub, region, gadm_code)
        if not os.path.exists(self.reblock_path):
            os.makedirs(self.reblock_path)
        self.summary_path = os.path.join(self.reblock_path, "reblock_summary_{}.csv".format(gadm))
        self.steiner_path = os.path.join(self.reblock_path, "steiner_lines_{}.csv".format(gadm))
        self.terminal_path = os.path.join(self.reblock_path, "terminal_points_{}.csv".format(gadm))

        self.prior_work_exists = (os.path.exists(self.summary_path)) and drop_already_completed

        self.summary_dict, self.steiner_lines_dict, self.terminal_points_dict = self.load_dicts()
        self.completed = set(self.summary_dict.keys())
        if self.prior_work_exists:
            print("--Loading {} previously computed results".format(len(self.completed)))

    def update(self, block_id, new_steiner, existing_steiner, terminal_points, summary):
        new_steiner = new_steiner if new_steiner is None else dumps(new_steiner)
        existing_steiner = existing_steiner if existing_steiner is None else dumps(existing_steiner)
        terminal_points = terminal_points if terminal_points is None else dumps(terminal_points)    
        
        self.summary_dict[block_id] = summary 
        self.terminal_points_dict[block_id] = [terminal_points, block_id]
        self.steiner_lines_dict[block_id+'new_steiner'] = [new_steiner, block_id, 'new_steiner', block_id+'new_steiner'] 
        self.steiner_lines_dict[block_id+'existing_steiner'] = [existing_steiner, block_id, 'existing_steiner', block_id+'existing_steiner'] 

    def load_dicts(self):
        if self.prior_work_exists:
            summary_records = pd.read_csv(self.summary_path).drop(['Unnamed: 0'], axis=1).to_dict('records')
            summary_dict = {d['block']:list(d.values()) for d in summary_records}

            steiner_records = pd.read_csv(self.steiner_path).drop(['Unnamed: 0'], axis=1).to_dict('records')
            steiner_dict = {d['block_w_type']:list(d.values()) for d in steiner_records}

            terminal_points_records = pd.read_csv(self.terminal_path).drop(['Unnamed: 0'], axis=1).to_dict('records')
            terminal_points_dict = {d['block']:list(d.values()) for d in terminal_points_records}
            return summary_dict, steiner_dict, terminal_points_dict
        else:
            return {}, {}, {}

    def save(self):
        summary_columns = [      'bldg_time',       'simplify_time',     'steiner_time', 'num_graph_comps',  
                            'node_count_pre',     'node_count_post',   'edge_count_pre', 'edge_count_post',
                                'bldg_count',    'num_block_coords', 'num_block_coords_unmatched',  'block']

        steiner_columns = ['geometry', 'block', 'line_type', 'block_w_type']
        terminal_columns = ['geometry', 'block']

        summary_df = pd.DataFrame.from_dict(self.summary_dict, orient='index', columns=summary_columns)
        steiner_df = pd.DataFrame.from_dict(self.steiner_lines_dict, orient='index', columns=steiner_columns)
        terminal_df = pd.DataFrame.from_dict(self.terminal_points_dict, orient='index', columns=terminal_columns)

        summary_df.to_csv(self.summary_path)
        steiner_df.to_csv(self.steiner_path)
        terminal_df.to_csv(self.terminal_path)


def drop_buildings_intersecting_block(parcel_geom, building_list, block_geom, block_id):
    '''
    If a parcel shares a boundary with the block, then it already has access 
    and doesn't need to be included. So, polygonize the parcels and intersect 
    the parcel polygons with the boundary of the block, thus allowing reblocking
    to focus only on the interior parcels without access.
    '''

    # Converts the parcels to polygons
    parcel_geom_df = gpd.GeoDataFrame({'geometry': list(polygonize(parcel_geom))})
    parcel_geom_df = parcel_geom_df.explode()
    parcel_geom_df.reset_index(inplace=True, drop=True)

    # Make a dataframe of building points
    building_geom_df = gpd.GeoDataFrame({'geometry': [MultiPoint(building_list)]})
    building_geom_df = building_geom_df.explode()
    building_geom_df.reset_index(inplace=True, drop=True)
    building_geom_df.reset_index(inplace=True)
    building_geom_df.rename(columns={'index': 'building_id'}, inplace=True)

    # Figure out which building is in each parcel
    m = gpd.sjoin(parcel_geom_df, building_geom_df, how='left') 
    has_building = m['building_id'].notna()

    if has_building.sum() != building_geom_df.shape[0]:
        print("Check map_points_to_parcel sjoin for block: {}".format(block_id))
        print("buildings = {} but matched = {}".format(building_geom_df.shape[0], has_building.sum()))
    m_has_building = m.loc[has_building]
    m_has_building = m_has_building.rename(columns={'geometry':'parcel_geom'})
    m_has_building = m_has_building.merge(building_geom_df, how='left', on='building_id')

    # Now check which parcel geoms intersect with the block
    block_boundary = block_geom.boundary 

    fn = lambda geom: geom.intersects(block_boundary)

    # And now return just the buildings that DO NOT have parcels on the border
    m_has_building['parcel_intersects_block'] = m_has_building['parcel_geom'].apply(fn)

    #print(m_has_building)

    reblock_buildings = m_has_building[~m_has_building['parcel_intersects_block']]['geometry'].apply(lambda g: g.coords[0])
    return list(reblock_buildings.values)

# new_points = []
# for i, row in m_has_building.iterrows():
#     pgeom = row['parcel_geom']
#     ngeom = row['geometry']
#     closest = get_closest_point(pgeom, ngeom, block_buffer)
#     #closest = get_closest_point(pgeom, ngeom, block_points_set)
#     new_points.append(closest)

# # For QC
# new_geom = [Point(x) for x in new_points]
# new_buildings = gpd.GeoDataFrame({'geometry': new_geom})
# ax = orig_parcel_geom_df.plot(color='blue', alpha=.3)
# block_buffer_geom_df = gpd.GeoDataFrame({'geometry': [block_buffer]})
# block_buffer_geom_df.plot(color='blue', alpha=1, ax=ax)
# building_geom_df.plot(color='black', ax=ax)
# new_buildings.plot(color='red', ax=ax)
# plt.show()


def reblock_gadm(region, gadm_code, gadm, simplify, block_list=None, only_block_list=False, 
                 drop_already_completed=True, digital_globe_data=False, mins_threshold=np.inf):
    '''
    Does reblocking for an entire GADM boundary
    '''
    block_list = [] if block_list is None else block_list

    # (1) Just load our data for one GADM
    
    if digital_globe_data:
        print("Begin loading of Digital Globe data--{}-{}".format(region, gadm))
        parcels, buildings, blocks = i_topology_utils.load_reblock_inputs_dg(region, gadm_code, gadm)         
    else:
        print("Begin loading of data--{}-{}".format(region, gadm))
        parcels, buildings, blocks = i_topology_utils.load_reblock_inputs(region, gadm_code, gadm) 

    buildings['in_target'] = buildings['block_id'].apply(lambda x: x not in block_list)
    buildings.sort_values(by=['in_target', 'building_count'], inplace=True)

    checkpoint_every = 1

    # (2) Create a checkpointer which will handle saving and restoring of past work
    checkpointer = CheckPointer(region, gadm, gadm_code, drop_already_completed, digital_globe_data)
    possible_buildings = buildings['block_id'].values[0:len(block_list)] if only_block_list else buildings['block_id']
    all_blocks = [b for b in possible_buildings if b not in checkpointer.completed]

    print("\nBegin looping")
    i = 0
    elapsed_time_mins = -np.inf 
    # (4) Loop and process one block at-a-time
    for block_id in tqdm.tqdm(all_blocks, total=len(all_blocks)):

        # If most recent block took over our minute cutoff, break and finish
        if elapsed_time_mins > mins_threshold:
            print("Took {} mins and threshold is {} mins -- ending gadm at {}".format(elapsed_time_mins, mins_threshold, block_id))
            checkpointer.save()
            break 

        parcel_geom = parcels[parcels['block_id']==block_id]['geometry'].iloc[0]
        building_list = buildings[buildings['block_id']==block_id]['buildings'].iloc[0]
        block_geom = blocks[blocks['block_id']==block_id]['geometry'].iloc[0]

        ## UPDATES: drop buildings that intersect with the block border -- they have access
        if len(building_list) <= 1:
            continue 

        # Approx time of completion of block
        start_time = time.time()
        building_list = drop_buildings_intersecting_block(parcel_geom, building_list, block_geom, block_id)

        ## And explicitly add a dummy building outside of the block which will force Steiner Alg
        #      to connect to the outside road network
        bounding_rect = block_geom.minimum_rotated_rectangle
        convex_hull = block_geom.convex_hull
        outside_block = bounding_rect.difference(convex_hull)
        outside_building_point = outside_block.representative_point()
        building_list.append(outside_building_point.coords[0])

        if len(building_list) <= 1:
            continue 

        # (1) Convert parcel geometry to planar graph
        planar_graph = PlanarGraph.multilinestring_to_planar_graph(parcel_geom)

        # (2) Update the edge types based on the block graph
        missing, total_block_coords = i_topology_utils.update_edge_types(planar_graph, block_geom, check=True)

        # (3) Do reblocking 
        try:
            new_steiner, existing_steiner, terminal_points, summary = get_optimal_path(planar_graph, building_list, simplify=simplify, verbose=True)
        except:
            new_steiner = None 
            existing_steiner = None 
            terminal_points = None 
            summary = [None, None, None, None, None, None, None, None]

        elapsed_time_mins = (start_time - time.time())/60

        # Collect and store the summary info from reblocking
        summary = summary + [len(building_list), total_block_coords, missing, block_id]
        checkpointer.update(block_id, new_steiner, existing_steiner, terminal_points, summary)

        # Save out on first iteration and on checkpoint iterations
        if (i == 0) or (i % checkpoint_every == 0):
            checkpointer.save()

             
        i += 1


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Do reblocking on a GADM')
    parser.add_argument('--region', type=str, required=True, help="region to process")
    parser.add_argument('--gadm_code', type=str, required=True, help="3-digit country gadm code to process")
    parser.add_argument('--gadm', help='process this gadm, if not supplied will process all GADMs', default=None)
    parser.add_argument('--simplify', help='boolean to simplify the graph or not', action='store_true')
    parser.add_argument('--blocks', dest='block_list', help='prioritize these block ids', nargs='*', type=str)
    parser.add_argument('--only_block_list', help='limit reblocking to specified blocks', action='store_true')
    parser.add_argument('--dg', dest='digital_globe_data', help='adding flag indicates to use DG data', action='store_true')
    parser.add_argument('--from_dir', help='process all the gadms in this directory', type=str, default=None)
    parser.add_argument('--mins_threshold', help='will break if block takes more than this num of mins', type=int)
    
    args = parser.parse_args()
    args_dict = vars(args)
    from_dir = args_dict.pop('from_dir')
    if from_dir is not None:
        # Then process all GADMs
        dir_path = Path(from_dir) 
        all_gadms = [f.stem.replace("buildings_", "").replace("parcels_", "") for f in dir_path.iterdir()]
        for gadm in all_gadms:
            args_dict['gadm'] = gadm 
            print("Beginning reblock for {}-{}".format(args_dict['region'],  args_dict['gadm']))
            reblock_gadm(**args_dict)
    else:   
        print("Beginning reblock for {}-{}".format(args_dict['region'], args_dict['gadm']))
        reblock_gadm(**args_dict)


#     'Monrovia': ['LBR.11.2.1_1_2563', 'LBR.11.2.1_1_282', 'LBR.11.2.1_1_1360', 'LBR.11.2.1_1_271'],
