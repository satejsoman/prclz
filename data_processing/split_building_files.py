from typing import List, Union

import geopandas as gpd
from shapely.geometry import MultiPolygon, Polygon, MultiLineString
from shapely.ops import cascaded_union
from shapely.wkt import loads
import pandas as pd

import os 
import matplotlib.pyplot as plt 

BLOCK_PATH = "../data/blocks/Africa/"
GEOJSON_PATH = "../data/geojson/Africa"
GADM_GEOJSON_PATH = "../data/geojson_gadm/Africa"
TRANS_TABLE = pd.read_csv('country_codes.csv')

def csv_to_geo(csv_path):
    '''
    Loads the csv and returns a GeoDataFrame
    '''

    df = pd.read_csv(csv_path, usecols=['block_id', 'geometry'])
    df.rename(columns={"geometry":"block_geom"}, inplace=True)
    df['block_geom'] = df['block_geom'].apply(loads)

    return gpd.GeoDataFrame(df, geometry='block_geom')

def split_files(building_file, trans_table: pd.DataFrame):
    '''
    Given a country buildings.geojson file string,
    it distributes those buildings according to the
    GADM boundaries and block file
    '''

    input_type = "lines" if "lines" in building_file else "buildings"

    # Get buildings file
    buildings = gpd.read_file(os.path.join(GEOJSON_PATH, building_file))

    # Apply convex hull transform to our buildings
    if input_type == "buildings":
        buildings['geometry'] = buildings['geometry'].convex_hull

    cols = [c for c in buildings.columns]
    buildings['match_count'] = 0

    geofabrik_name = building_file.replace("_buildings.geojson", "").replace("_lines.geojson", "")
    country_info = trans_table[trans_table['geofabrik_name'] == geofabrik_name]
    gadm_name = country_info['gadm_name'].item()
    
    print("Processing a {} file type of country {}".format(input_type, geofabrik_name))

    block_file_path = os.path.join(BLOCK_PATH, gadm_name)

    # Check that the block file exists
    if not os.path.isdir(block_file_path):
        print("WARNING - country {} / {} does not have a block file".format(geofabrik_name, gadm_name))
        return buildings 

    block_files = os.listdir(block_file_path)

    output_path = os.path.join(GADM_GEOJSON_PATH, gadm_name)
    if not os.path.isdir(output_path):
        os.mkdir(output_path)

    for block_file in block_files:

        blocks = csv_to_geo(os.path.join(block_file_path, block_file))

        # Identify those buildings that sjoin via intersect with our block
        split_buildings = gpd.sjoin(buildings, blocks, how='left', op='intersects')
        has_match = pd.notnull(split_buildings['index_right'])

        # Limit to those buildings that intersect in some way with our blocks
        buildings_in_block = split_buildings[cols][has_match]

        # Save that out
        f = block_file.replace("blocks", input_type).replace(".csv", ".geojson")

        if os.path.isfile(os.path.join(output_path, f)):
            os.remove(os.path.join(output_path, f))

        if buildings_in_block.shape[0] > 0:
            #print(buildings_in_block.shape)
            buildings_in_block.to_file(os.path.join(output_path, f), driver='GeoJSON')

        b = block_file.replace(".csv","").replace("blocks_", "")
        print("Block {} contains {} {}".format(b, has_match.sum(), input_type))

        # Record how many matches we see for each building
        ids = buildings_in_block[['osm_id']].drop_duplicates()
        ids['matched_flag'] = 1
        buildings = buildings.merge(ids, how='left', on='osm_id')
        buildings['matched_flag'] = buildings['matched_flag'].fillna(0)
        buildings['match_count'] = buildings['match_count'] + buildings['matched_flag']
        buildings.drop(columns=['matched_flag'], inplace=True)

    print(buildings['match_count'].value_counts(dropna=False, normalize=True))

    return buildings  


# building_file = "djibouti_buildings.geojson" 
# line_file = "djibouti_lines.geojson"

#buildings = split_files(building_file, trans_table) 
#lines = split_files(line_file, trans_table)

# To plot 
# ax = blocks.plot(alpha=0.5, color='blue')
# buildings.plot(ax=ax, color='red')

def process_all_files():
    '''
    '''

    if not os.path.isdir("building_split_qc"):
        os.mkdir("building_split_qc")

    country_files = os.listdir(GEOJSON_PATH)

    for f in country_files:
        print(f)
        if "buildings" in f:
            buildings = split_files(f, TRANS_TABLE)

            not_matched_buildings = buildings[buildings['match_count'] == 0]

            qc_path = os.path.join("building_split_qc", f.replace("buildings", "not_matched_buildings"))
   
            if os.path.isfile(qc_path):
                os.remove(qc_path)

                if not_matched_buildings.shape[0] != 0:
                    not_matched_buildings.to_file(qc_path, driver='GeoJSON')

if __name__ == "__main__":
    process_all_files()