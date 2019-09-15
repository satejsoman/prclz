from typing import List, Union

import geopandas as gpd
from shapely.geometry import MultiPolygon, Polygon, MultiLineString
from shapely.ops import cascaded_union
from shapely.wkt import loads
import pandas as pd
import time 

import os 
import matplotlib.pyplot as plt 
import sys 

import argparse

BLOCK_PATH = "../data/blocks"
GEOJSON_PATH = "../data/geojson"
TRANS_TABLE = pd.read_csv('country_codes.csv')
DATA_PATH = "../data"

from split_geojson import join_block_files

EPS = 1e-5

def split_lines_by_gadm(country_code:str, region:str, block_file_path:str, linestring_path:str):
    '''
    '''

    blocks = join_block_files(block_file_path)
    lines = gpd.read_file(linestring_path)

    # For whatever reason the sjoin is always NaN for everything on just the lines
    #   so do this hacky workaround
    lines['dilated_geom'] = lines.buffer(EPS)
    lines.set_geometry('dilated_geom', inplace=True)
    merged = gpd.sjoin(lines, blocks, how='left', op='intersects') 
    merged.set_geometry('geometry', inplace=True)
    merged.drop(columns=['dilated_geom', 'index_right'], inplace=True)

    # Save out
    all_gadms = merged['gadm_code'].unique()
    outpath = os.path.join(DATA_PATH, "lines", region, country_code)
    for gadm in all_gadms:

        merged_gadm = merged[merged['gadm_code']==gadm]
        if merged_gadm.shape[0] > 0:
            f = "lines_{}.geojson".format(gadm)

            if os.path.isfile(os.path.join(outpath, f)):
                os.remove(os.path.join(outpath, f))
            merged_gadm.to_file(os.path.join(outpath, f), driver='GeoJSON')
        print("--gadm {} contains {} lines--complete".format(gadm, merged_gadm.shape[0]))



if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument("country_code", help="path to a country-specific *buildings.geojson or *lines.geojson file", type=str)
    parser.add_argument("region", help="if the geojson file corresponds to 2 countries, you can specify the unique GADM code", type=str)
    parser.add_argument("block_file_path", help="default behavior is to skip if the country has been processed. Adding this option replaces the files", type=str)
    parser.add_argument("linestring_path", help="default behavior is to skip if the country has been processed. Adding this option replaces the files", type=str)

    args = parser.parse_args()

    # Make file paths
    if not os.path.isdir(os.path.join(DATA_PATH, "lines", region)):
        os.mkdir(os.path.join(DATA_PATH, "lines", region))
    if not os.path.isdir(os.path.join(DATA_PATH, "lines", region, country_code)):
        os.mkdir(os.path.join(DATA_PATH, "lines", region, country_code))
        

    split_lines_by_gadm(args.country_code, args.region, args.block_file_path, args.linestring_path)
