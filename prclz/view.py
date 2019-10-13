import typing 

import geopandas as gpd
from shapely.geometry import MultiPolygon, Polygon, MultiLineString, Point, LineString
from shapely.ops import cascaded_union
from shapely.wkt import loads
import pandas as pd
import geopandas as gpd 
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

DATA = "../data"
REBLOCK = os.path.join(DATA, "reblock")

# region = "Africa"
# gadm_code = "SLE"
# gadm = "SLE.4.2.1_1"
# example_block = "SLE.4.2.1_1_1241"

# REBLOCK = "../data/reblock/Africa/LBR"

# # (1) Just load our data for one GADM
# print("Begin loading of data")
# blocks = i_topology_utils.csv_to_geo(os.path.join("../data", "blocks", region, gadm_code, "blocks_"+gadm+".csv"))

# # # (2) Now build the parcel graph and prep the buildings
# # # restrict to some example blocks within the GADM
# block = blocks[blocks['block_id']==example_block]

# steiner = gpd.read_file("test_SLE_igraph/steiner_lines.geojson")
# terminal = gpd.read_file("test_SLE_igraph/terminal_points.geojson")

class ReblockPlotter:

    def __init__(self, gadm_list, region, add_buildings=False, add_parcels=False):

        self.gadm_code = gadm_list[0][0:3]
        self.region = region 
        self.gadm_list = gadm_list
        self.gadm_count = len(gadm_list)
        self.add_buildings = add_buildings
        self.add_parcels = add_parcels
        
        for i, gadm in enumerate(self.gadm_list):
            steiner_lines_path = os.path.join(REBLOCK, region, self.gadm_code, "steiner_lines_{}.geojson".format(gadm))
            terminal_points_path = os.path.join(REBLOCK, region, self.gadm_code, "terminal_points_{}.geojson".format(gadm))
            blocks_path = os.path.join(DATA, "blocks", region, self.gadm_code, "blocks_{}.csv".format(gadm))
            buildings_path = os.path.join(DATA, "buildings", region, self.gadm_code, "buildings_{}.geojson".format(gadm))
            parcels_path = os.path.join(DATA, "parcels", region, self.gadm_code, "parcels_{}.geojson".format(gadm))

            if i == 0:
                self.steiner = gpd.read_file(steiner_lines_path)
                self.terminal = gpd.read_file(terminal_points_path)
                self.blocks = i_topology_utils.csv_to_geo(blocks_path)
                self.buildings = gpd.read_file(buildings_path) if self.add_buildings else None 
                self.parcels = gpd.read_file(parcels_path) if self.add_parcels else None 
            else:
                self.steiner = pd.concat([gpd.read_file(steiner_lines_path), self.steiner], axis=0)
                self.terminal = pd.concat([gpd.read_file(terminal_points_path), self.terminal], axis=0)
                self.blocks = pd.concat([i_topology_utils.csv_to_geo(blocks_path), self.blocks], axis=0)
                self.buildings = pd.concat([gpd.read_file(buildings_path), self.buildings], axis=0) if self.add_buildings else None 
                self.parcels = pd.concat([gpd.read_file(parcels_path), self.parcels], axis=0) if self.add_parcels else None 

        self.graph_dict = {}

        self.block_ids = self.blocks['block_id']

    def load_block_graph(self, block_id):
        if isinstance(block_id, int):
            block_id = "{}_{}".format(self.gadm, int)

        graph_path = os.path.join(DATA, "graphs", self.region, self.gadm_code, "{}.igraph".format(block_id))
        return PlanarGraph.load_planar(graph_path)        

    def view_block(self, block_id, add_buildings=None, add_parcels=None, line_types='steiner'):
        '''
        Allows user to visualize reblocking for a single specified block, as determined by the block_id
        Note, if you've imported building and parcels when constructing the viewer, you can choose
        to include/not include them when viewing
        '''
        
        if isinstance(block_id, int):
            block_id = "{}_{}".format(self.gadm, int)

        # Allow user to override and just view without buildings
        add_buildings = self.add_buildings if add_buildings is None else add_buildings
        add_parcels = self.add_parcels if add_parcels is None else add_parcels

        ax = self.blocks[self.blocks['block_id']==block_id].plot(color='black', alpha=0.2)
        self.terminal[self.terminal['block_id']==block_id].plot(color='red', ax=ax)

        if line_types == 'steiner':
            self.steiner[self.steiner['block_id']==block_id].plot(color='red', ax=ax)
        elif line_types == 'all':
            self.graph_dict['block_id'] = self.load_block_graph(block_id)
            lines = convert_to_lines(self.graph_dict['block_id'])
            lines_geo = gpd.GeoSeries(lines)
            lines_geo.plot(color='red', ax=ax)

        if add_buildings:
            self.buildings.plot(color='blue', alpha=0.4, ax=ax)
        if add_parcels:
            self.parcels[self.parcels['block_id']==block_id].plot(color='blue', alpha=0.4, ax=ax)


    def view_all(self, add_buildings=None, add_parcels=None):
        '''
        Calling this will visualize the reblocking for the entire area you've specified in your constructor
        '''

        # Allow user to override and just view without buildings
        add_buildings = self.add_buildings if add_buildings is None else add_buildings
        add_parcels = self.add_parcels if add_parcels is None else add_parcels

        ax = self.blocks.plot(color='black', alpha=0.2)
        self.steiner.plot(color='red', ax=ax)
        self.terminal.plot(color='red', ax=ax)
        if add_buildings:
            self.buildings.plot(color='blue', alpha=0.4, ax=ax)

        if add_parcels:
            self.parcels.plot(color='blue', alpha=0.4, ax=ax)

    def export_parcels(self, output_filename):
        self.parcels.to_file(output_filename, driver='GeoJSON')

    def export_steiner(self, output_filename):
        self.steiner.to_file(output_filename, driver='GeoJSON')



if __name__ == "__main__":
    gadm_list = ['KEN.30.10.1_1',
     'KEN.30.10.2_1',
     'KEN.30.10.3_1',
     'KEN.30.10.4_1',
     'KEN.30.10.5_1',
     'KEN.30.11.2_1']

    region = 'Africa'

    viewer = ReblockPlotter(gadm_list, region, add_parcels=True)

    # This will allow you to view the optimal paths
    # viewer.view_all()
    # plt.show()

    # Now we export to files, assuming we've sanity checked the output and it looks good
    viewer.export_parcels(os.path.join(DATA, 'KEN_parcels.geojson'))
    viewer.export_steiner(os.path.join(DATA, 'KEN_opt_path.geojson'))


