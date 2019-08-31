from typing import List, Union

import geopandas as gpd
from shapely.geometry import MultiPolygon, Polygon, MultiLineString
from shapely.ops import cascaded_union
from shapely.wkt import loads
import pandas as pd
import numpy as np 
import time 

import os 
import matplotlib.pyplot as plt 
import sys 

import argparse

BLOCK_PATH = "../data/blocks"
GEOJSON_PATH = "../data/geojson"
TRANS_TABLE = pd.read_csv('country_codes.csv')
DATA_PATH = "../data"
GADM_PATH = os.path.join(DATA_PATH, "GADM")

def get_percentile(array, pct):
    '''
    Assumes array is sorted
    '''
    i = int(pct * array.shape[0]) -1 
    return array[i]

def sort_fn(fname, gadm_name):

    s = fname.replace("gadm36_", "").replace("_","").replace(".shp","")
    s = s.replace(gadm_name, "")

    return int(s)

def get_min_distance_of_nonmatched(gadm_code):
    '''
    Given a GADM country code, this script returns statistics on the min
    distance from each non-matched building to the nearest GADM
    boundary
    '''
    print("Processing {}".format(gadm_code))
    # Non-matched bldgs
    splitter_output = "splitter_output/buildings"
    files = [x for x in os.listdir(os.path.join(splitter_output, gadm_code)) if "not_matched" in x]

    if len(files) == 0:
        return gadm_code, None, None, None, None 
    f = files[0]
    nonmatched_bldgs = gpd.read_file(os.path.join(splitter_output, gadm_code, f))

    # GADM file
    path = os.path.join(GADM_PATH, gadm_code)
    shp_files = [x for x in os.listdir(path) if ".shp" in x]
    shp_files.sort(key = lambda x: sort_fn(x, gadm_code))
    gadm = gpd.read_file(os.path.join(path, shp_files[-1]))

    # All bounds
    all_bounds = gadm['geometry'].unary_union
    distance = np.array(nonmatched_bldgs['geometry'].distance(all_bounds))
    distance.sort()

    # Some stats
    pct_50 = get_percentile(distance, .50)
    pct_95 = get_percentile(distance, .95)
    pct_100 = get_percentile(distance, 1.00)

    return gadm_code, pct_50, pct_95, pct_100, nonmatched_bldgs.shape[0]

def main():

    splitter_output = "splitter_output/buildings"
    cols = ['gadm_name', 'pct_50', 'pct_95', 'pct_100', 'total_nonmatched_count']

    all_gadm_codes = [x for x in os.listdir(splitter_output) if ".txt" not in x]

    data = []
    for code in all_gadm_codes:
        try:
            d = get_min_distance_of_nonmatched(code)
        except:
            d = gadm_code, None, None, None, None 
        data.append(d)
    #data = [get_min_distance_of_nonmatched(code) for code in all_gadm_codes]

    df_data = pd.DataFrame.from_records(data, columns=cols)

    df_data.to_csv("summary_missing_distances.csv")

if __name__ == "__main__":

    main()