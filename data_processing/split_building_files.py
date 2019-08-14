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

print("DONE IMPORTING\n")

BLOCK_PATH = "../data/blocks/Africa/"
GEOJSON_PATH = "../data/geojson/Africa"
GADM_GEOJSON_PATH = "../data/geojson_gadm/Africa"
TRANS_TABLE = pd.read_csv('country_codes.csv')


def geofabrik_to_gadm(geofabrik_name):
    country_info = TRANS_TABLE[TRANS_TABLE['geofabrik_name'] == geofabrik_name]

    assert country_info.shape[0] == 1, "geofabrik -> gadm failed, CHECK csv mapping for {}".format(geofabrik_name)

    gadm_name = country_info['gadm_name'].iloc[0]
    return gadm_name


def csv_to_geo(csv_path, add_file_col=False):
    '''
    Loads the csv and returns a GeoDataFrame
    '''

    df = pd.read_csv(csv_path, usecols=['block_id', 'geometry'])

    # Block id should unique identify each block
    assert df['block_id'].is_unique, "Loading {} but block_id is not unique".format(csv_path)

    df.rename(columns={"geometry":"block_geom"}, inplace=True)
    df['block_geom'] = df['block_geom'].apply(loads)

    if add_file_col:
        f = csv_path.split("/")[-1]
        df['gadm_code'] = f.replace("blocks_", "").replace(".csv", "")

    return gpd.GeoDataFrame(df, geometry='block_geom')

def join_block_files(gadm_name: str) -> gpd.GeoDataFrame:

    block_file_path = os.path.join(BLOCK_PATH, gadm_name)
    block_files = os.listdir(block_file_path)

    all_blocks = pd.concat([csv_to_geo(os.path.join(block_file_path, block_file), add_file_col=True) 
        for block_file in block_files])

    all_blocks = gpd.GeoDataFrame(all_blocks, geometry='block_geom')

    return all_blocks


def split_files_alt(building_file: str, trans_table: pd.DataFrame, return_all_blocks=False):
    '''
    Given a country buildings.geojson file string,
    it distributes those buildings according to the
    GADM boundaries and block file
    '''

    geofabrik_name = building_file.replace("_buildings.geojson", "").replace("_lines.geojson", "")
    gadm_name = geofabrik_to_gadm(geofabrik_name)
    
    input_type = "lines" if "lines" in building_file else "buildings"

    # Get the corresponding block file (and check that it exists)
    block_file_path = os.path.join(BLOCK_PATH, gadm_name)

    # Check that the block folder exists
    if not os.path.isdir(block_file_path):
        print("WARNING - country {} / {} does not have a block folder".format(geofabrik_name, gadm_name))
        return None, "no_block_folder" 

    # Check that the block folder actually has block files in it
    block_files = os.listdir(block_file_path)

    if len(block_files) == 0:
        print("WARNING - country {} / {} has a block file path but has no block files in it".format(geofabrik_name, gadm_name))
        return None, "block_folder_empty" 

    all_blocks = join_block_files(gadm_name)
    all_blocks.set_index('block_id', inplace=True)
    assert all_blocks.index.is_unique, "Setting index=block_id but not unique"

    # Get buildings file
    try:
        buildings = gpd.read_file(os.path.join(GEOJSON_PATH, building_file))
    except:
        print("WARNING - country {} / {} could not load GeoJSON file".format(geofabrik_name, gadm_name))
        return None, "load_geojson_error"

    # Apply convex hull transform to our buildings
    if input_type == "buildings":
        buildings['geometry'] = buildings['geometry'].convex_hull

    cols = [c for c in buildings.columns]
    cols.append('gadm_code')
    buildings['match_count'] = 0

    print("Processing a {} file type of country {}\n".format(input_type, geofabrik_name))

    output_path = os.path.join(GADM_GEOJSON_PATH, gadm_name)
    if not os.path.isdir(output_path):
        os.mkdir(output_path)

    # PRESERVED
    # # Identify those buildings that sjoin via intersect with our block
    # buildings = gpd.sjoin(buildings, all_blocks, how='left', op='intersects')
    # #buildings = gpd.sjoin(buildings, all_blocks, how='left', op='within')
    # buildings['match_count'] = pd.notnull(buildings['index_right'])
    # buildings.merge(all_blocks[['gadm_code']], left_on='index_right', right_index=True)

    # Identify those buildings that sjoin via intersect with our block
    buildings['bldg_centroid'] = buildings['geometry'].centroid 
    buildings.set_geometry('bldg_centroid', inplace=True)

    # Check that we are not missing any centroids or buildings
    assert not (buildings['geometry'].isna().any()), "building geometry is missing"
    assert not (buildings['bldg_centroid'].isna().any()), "bldg_centroid is missing"

    #buildings = gpd.sjoin(buildings, all_blocks, how='left', op='intersects')
    buildings = gpd.sjoin(buildings, all_blocks, how='left', op='within')
    print(buildings.columns)
    assert 'gadm_code' in list(buildings.columns)
    assert isinstance(buildings, gpd.GeoDataFrame), "No longer GeoDataFrame (1)"
    buildings.set_geometry('geometry', inplace=True)
    #buildings.drop(columns=['bldg_centroid'], inplace=True)
    buildings['match_count'] = pd.notnull(buildings['index_right'])
    #buildings.merge(all_blocks[['gadm_code']], left_on='index_right', right_index=True)

    # Now, distribute and save
    all_gadm_codes = buildings['gadm_code'].unique()
    for code in all_gadm_codes:

        # Do nothing for those unmatched (but will note those that are not matched)
        if pd.notna(code):
            # print(code)

            buildings_in_gadm = buildings[ buildings['gadm_code']==code ][cols]
            f = "buildings_" + code + ".geojson"

            if os.path.isfile(os.path.join(output_path, f)):
                os.remove(os.path.join(output_path, f))

            if buildings_in_gadm.shape[0] > 0:
                #print(buildings_in_gadm.shape)
                buildings_in_gadm.to_file(os.path.join(output_path, f), driver='GeoJSON')

            # print("GADM code {} contains {} {}".format(code, buildings_in_gadm.shape[0], input_type))

    buildings['match_count'] = buildings['match_count'].apply(int)

    # print(buildings['match_count'].value_counts(dropna=False, normalize=True))
    # print()

    if return_all_blocks:
        return buildings, "DONE", all_blocks
    else:
        return buildings, "DONE"


def check_building_file_already_processed(gadm_name):
    '''
    Returns True if the gamd_name has already been split out
    Returns False if it needs to be done
    '''

    p = os.path.join(GADM_GEOJSON_PATH, gadm_name)
    return os.path.isdir(p)

def map_matching_results(buildings_output, all_blocks, file_name):

    nonmatched_pct = (1 - buildings_output.match_count.mean()) * 100
    nonmatched_count = nonmatched_pct * buildings_output.shape[0]

    buildings_output.set_geometry('bldg_centroid', inplace=True)
    ax = buildings_output.plot(column='match_count', figsize=(25,25))
    all_blocks.plot(ax=ax, color='blue', alpha=0.5)
    plt.axis('off')
    plt.title("Nonmatched count = {} pct = {}".format(int(nonmatched_count), nonmatched_pct))
    plt.savefig(file_name)


if __name__ == "__main__":

    start = time.time()

    if not os.path.isdir("building_split_qc"):
        os.mkdir("building_split_qc")

    building_file = sys.argv[1].split("/")[-1]
    geofabrik_name = building_file.replace("_buildings.geojson", "").replace("_lines.geojson", "")
    gadm_name = geofabrik_to_gadm(geofabrik_name)

    # Check first if we've already processed the files
    already_processed = check_building_file_already_processed(gadm_name)

    if already_processed:
        print("Country {} | {} has already been processed -- SKIPPING".format(geofabrik_name, gadm_name))

    else:
        buildings, details = split_files_alt(building_file, TRANS_TABLE)

        # Was a success
        if buildings is not None:
            not_matched_buildings = buildings[buildings['match_count'] == 0]

            qc_path = os.path.join("building_split_qc", building_file.replace("buildings", "not_matched_buildings"))
            print(not_matched_buildings.shape)
            print()

            if os.path.isfile(qc_path):
                os.remove(qc_path)

            if not_matched_buildings.shape[0] != 0:
                not_matched_buildings.to_file(qc_path, driver='GeoJSON')
        else:
            error_summary = open("building_split_qc/error_summary{}.txt".format(gadm_name), 'w')
            error_summary.write(building_file + "  |  " + details + "\n")

        print("Processing {} | {} takes {} seconds".format(geofabrik_name, gadm_name, time.time()-start))

