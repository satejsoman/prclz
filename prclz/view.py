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

    def __init__(self, gadm, region, add_buildings=False, add_parcels=False):

        self.gadm_code = gadm[0:3]
        self.region = region 
        self.gadm = gadm
        self.add_buildings = add_buildings
        self.add_parcels = add_parcels
        
        steiner_lines_path = os.path.join(REBLOCK, region, self.gadm_code, "steiner_lines_{}.geojson".format(gadm))
        terminal_points_path = os.path.join(REBLOCK, region, self.gadm_code, "terminal_points_{}.geojson".format(gadm))
        blocks_path = os.path.join(DATA, "blocks", region, self.gadm_code, "blocks_{}.csv".format(gadm))
        buildings_path = os.path.join(DATA, "buildings", region, self.gadm_code, "buildings_{}.geojson".format(gadm))
        parcels_path = os.path.join(DATA, "parcels", region, self.gadm_code, "parcels_{}.geojson".format(gadm))

        self.steiner = gpd.read_file(steiner_lines_path)
        self.terminal = gpd.read_file(terminal_points_path)
        self.blocks = i_topology_utils.csv_to_geo(blocks_path)
        self.buildings = gpd.read_file(buildings_path) if self.add_buildings else None 
        self.parcels = gpd.read_file(parcels_path) if self.add_parcels else None 
        self.graph_dict = {}

        self.block_ids = self.blocks['block_id']

    def load_block_graph(self, block_id):
        if isinstance(block_id, int):
            block_id = "{}_{}".format(self.gadm, int)

        graph_path = os.path.join(DATA, "graphs", self.region, self.gadm_code, "{}.igraph".format(block_id))
        return PlanarGraph.load_planar(graph_path)        

    def view_block(self, block_id, add_buildings=None, add_parcels=None, line_types='steiner'):
        
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

#viewer = ReblockPlotter('LBR.7.4.1_1', 'Africa')


