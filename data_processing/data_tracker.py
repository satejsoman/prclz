import os 
import pandas as pd 
import geopandas as gpd 

import argparse

BLOCK_PATH = "../data/blocks"
GEOJSON_PATH = "../data/geojson"
GADM_GEOJSON_PATH = "../data/geojson_gadm"
GADM_PATH = "../data/GADM"
TRANS_TABLE = pd.read_csv('country_codes.csv')


def get_all_gadms(gadm_name: str) -> set:
    '''
    Just a helper to return the highest resolution
    GADM boundary geoDataFrame
    '''

    get_level_fn = lambda f: int(f.replace(".shp", "").split("_")[-1])

    files = [x for x in os.listdir(os.path.join(GADM_PATH, gadm_name)) if ".shp" in x]
    files.sort(key = get_level_fn)

    gdf = gpd.read_file(os.path.join(GADM_PATH, gadm_name, files[-1]))
    i = get_level_fn(files[-1])

    all_gadms = gdf[ "GID_{}".format(i) ]

    return set(all_gadms)

def get_all_gadm_blocks(gadm_name: str, region: str) -> set:
    '''
    For the given country, checks in /blocks/{region}/{gadm_name}
    and returns a set of all the gadms
    '''
    region = region.title()
    path = os.path.join(BLOCK_PATH, region, gadm_name)
    if not os.path.isdir(path):
        return set()
    else:
        return set(x.replace(".csv","").replace("blocks_","") for x in os.listdir(path))

def do_gadm_check(row: pd.Series) -> (int, str):
    '''
    row is a series which has keys 'gadm_name', 'region'
    '''
    gadm_name = row['gadm_name']
    region = row['geofabrik_region']

    all_gadms = get_all_gadms(gadm_name)
    all_gadms_in_blocks = get_all_gadm_blocks(gadm_name, region)

    missing = all_gadms - all_gadms_in_blocks
    missing_count = len(missing)
    missing_str = "; ".join([str(x) for x in missing])

    return len(all_gadms), missing_count, missing_str 

def update_data_tracker(tt):
    '''
    Add data tracking of intermediate analyses to our original 
    csv listing all countries
    '''

    gadm_check_cols = ['total_gadm_count', 'missing_gadm_block_count', 'missing_gadm_block']
    tt[gadm_check_cols] = tt.apply(do_gadm_check, axis=1, result_type='expand')


if __name__ == "__main__":

    update_data_tracker(TRANS_TABLE)
    TRANS_TABLE.to_csv("country_codes_tracker.csv")