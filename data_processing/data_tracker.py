import os 
import pandas as pd 
import geopandas as gpd 

import argparse

BLOCK_PATH = "../data/blocks"
GEOJSON_PATH = "../data/geojson"
BUILDINGS_PATH = "../data/buildings"
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

# def get_all_gadm_blocks(gadm_name: str, region: str) -> set:
#     '''
#     For the given country, checks in /blocks/{region}/{gadm_name}
#     and returns a set of all the gadms
#     '''
#     region = region.title()
#     path = os.path.join(BLOCK_PATH, region, gadm_name)
#     if not os.path.isdir(path):
#         return set()
#     else:
#         return set(x.replace(".csv","").replace("blocks_","") for x in os.listdir(path) if "error" not in x)

# def get_all_gadm_buildings(gadm_name: str, region: str) -> set:
#     '''
#     For the given country, checks in /buildings/{region}/{gadm_name}
#     and returns a set of all the gadms
#     '''
#     region = region.title()
#     path = os.path.join(BUILDINGS_PATH, region, gadm_name)
#     if not os.path.isdir(path):
#         return set()
#     else:
#         return set(x.replace(".csv","").replace("blocks_","") for x in os.listdir(path) if "error" not in x)

def get_all_gadm_files_at(root_location: str, gadm_name:str, region: str) -> set:
    '''
    For the given country, checks in data/{root_location}/{region}/{gadm_name}
    and returns a set of all the gadms
    '''
    region = region.title()
    path = os.path.join(root_location, region, gadm_name)
    if not os.path.isdir(path):
        return set()
    else:
        return set(x.replace(".csv","").replace("blocks_","").replace("buildings_", "").replace(".geojson","") 
            for x in os.listdir(path) if "error" not in x)



def do_blocks_gadm_check(row: pd.Series) -> (int, str):
    '''
    row is a series which has keys 'gadm_name', 'region'
    Returns a check of:
      - (int) How many total GADM's are there
      - (int) How many GADM's are not included in the Blocks
      - (str) Which GADM's are missing
    '''
    gadm_name = row['gadm_name']
    region = row['geofabrik_region']
    print("Doing GADM check on : ", gadm_name)

    if pd.isnull(gadm_name):
        return None, None, None 

    if gadm_name == "ZAF":
        return None, None, None 

    all_gadms = get_all_gadms(gadm_name)
    all_gadms_in_blocks = get_all_gadm_files_at(BLOCK_PATH, gadm_name, region)

    missing = all_gadms - all_gadms_in_blocks
    missing_count = len(missing)
    missing_str = "; ".join([str(x) for x in missing])

    return len(all_gadms), missing_count, missing_str 

def do_buildings_gadm_check(row: pd.Series) -> (int, float, float, str):
    '''
    row is a series which has keys 'gadm_name', 'region'    
    Returns a check of:
      - (int) How many GADM's are not included in the Buildings (excluding GADM's known to contain 0 buildings)
      - (float) What % of the GADM's are found to contain 0 buildings
      - (float) What % of buildings are unmatched to a GADM
      - (str) Which GADM's are not included in the Buildings (excluding GADM's known to contain 0 buildings)
    '''
    gadm_name = row['gadm_name']
    region = row['geofabrik_region']
    print("Doing Buildings check on : ", gadm_name)

    if pd.isnull(gadm_name):
        return None, None, None, None  

    if gadm_name == "ZAF":
        return None, None, None, None  

    all_gadms = get_all_gadms(gadm_name)
    all_gadms_in_buildings = get_all_gadm_files_at(BUILDINGS_PATH, gadm_name, region)

    summary_file = os.path.join("splitter_output", "buildings", gadm_name, "matching_counts_summary.csv")
    if not os.path.isfile(summary_file):
        return None, None, None, None 

    match_counts = pd.read_csv(os.path.join("splitter_output", "buildings", gadm_name, "matching_counts_summary.csv"))
    match_counts['is_unmatched'] = match_counts['gadm_code']=='NO_GADM_DISTRICT'
    gadms_w_zero_buildings = match_counts[ (match_counts['match_count']==0) & (~match_counts['is_unmatched']) ]['gadm_code']

    # The GADMs listed in the buildings summary should be the complete set of GADMs
    qc_gadm_set = set(match_counts[ ~match_counts['is_unmatched'] ]['gadm_code'])
    #assert all_gadms == qc_gadm_set, "Total GADM={} | splitter summ.={}".format(len(all_gadms), len(qc_gadm_set))

    # Identify gadm's that are not in the buildings folder AND have not been identified as having zero matches
    missing = all_gadms - all_gadms_in_buildings - set(gadms_w_zero_buildings)
    missing_count = len(missing)
    missing_str = "; ".join([str(x) for x in missing])

    # Some additional QC summary stats
    # (1) What % of the GADM's have NO buildings in them
    pct_gadm_w_zero_bldgs = len(gadms_w_zero_buildings) / match_counts[ ~match_counts['is_unmatched']].shape[0]

    # (2) What % of the buildings are NOT matched to a GADM
    not_matched_summary = match_counts.groupby('is_unmatched').sum()['match_count']
    pct_bldgs_not_matched = not_matched_summary.loc[True] / not_matched_summary.sum()

    return missing_count, pct_gadm_w_zero_bldgs, pct_bldgs_not_matched, missing_str 

def update_data_tracker(tt):
    '''
    Add data tracking of intermediate analyses to our original 
    csv listing all countries
    '''

    # Add checks of the GADMs in the data/blocks
    gadm_check_cols = ['total_gadm_count', 'missing_gadm_block_count', 'missing_gadm_block']
    tt[gadm_check_cols] = tt.apply(do_blocks_gadm_check, axis=1, result_type='expand')

    # Add checks of the GADMs in the data/buildings
    buildings_check_cols = ['missing_gadm_bldg_count', 'pct_gadm_no_bldg', 'pct_bldg_unmatched', 'missing_gadm_bldg']
    tt[buildings_check_cols] = tt.apply(do_buildings_gadm_check, axis=1, result_type='expand')

if __name__ == "__main__":

    update_data_tracker(TRANS_TABLE)
    TRANS_TABLE.to_csv("country_codes_tracker.csv")
