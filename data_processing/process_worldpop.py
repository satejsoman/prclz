import numpy as np 
import rasterio 
from pathlib import Path 
import geopandas as gpd 
import pandas as pd 
from shapely.geometry import MultiPolygon, Polygon, MultiLineString
import argparse 

root = Path('../')
DATA = root / 'data' 
COMPLEXITY = DATA / "complexity"


def load_complexity(region, country_code, f):
    p = COMPLEXITY / region / country_code / f
    df = pd.read_csv(f)
    gdf_complexity = gpd.GeoDataFrame(df[['block_id', 'geometry', 'complexity', 'centroids_multipoint']])
    gdf_complexity['geometry'] = gdf_complexity['geometry'].apply(loads)
    gdf_complexity['bldg_count'] = gdf_complexity['centroids_multipoint'].apply(lambda x: len(x))
    gdf_complexity['block_area'] = gdf['geometry'].area 

    #gdf_bldgs = gpd.GeoDataFrame(df[['block_id', 'centroids_multipoint']])
    return gdf_complexity


def main_process_tif_to_geojson():
    landscan_path = DATA / 'LandScan_Global_2018' / 'ls_2018.tif'

    dataset = rasterio.open(landscan_path)
    bounds = dataset.bounds 
    resolution = 30 / 3600 # resolution of dataset in degrees
    delta = resolution

    top = bounds.top 
    bottom = bounds.bottom 
    left = bounds.left 
    right = bounds.right 

    print("Reading tif file....")
    mat = dataset.read(1)
    df_dict = {}
    df_dict['geometry'] = []
    df_dict['population'] = []
    df_dict['grid_idx'] = []
    for i, row in enumerate(mat):
        for j, val in enumerate(row):
            cur_top = top + delta * i 
            cur_left = left + delta * j
            cur_bottom = top + delta * (i+1)
            cur_right = left + delta * (j+1)

            # Make the polygon based on the top, left, bottom, right
            poly = Polygon([(cur_top, cur_left), (cur_top, cur_right),
                            (cur_bottom, cur_right), (cur_bottom, cur_left)])
            # Make the observation in the df_dict
            df_dict['geometry'].append(poly)
            df_dict['population'].append(val)
            df_dict['grid_idx'].append((i,j))

            if (i,j) == (0,0):
                print("Begin at {}, {}".format(cur_top, cur_left))
    print("End at {}, {}".format(cur_bottom, cur_right))

    # Now make the geopandas object
    df = pd.DataFrame.from_dict(df_dict)

    # Save 
    df.to_csv(data / "worldpop.csv")

def sjoin_complexity_landscan(complexity_df, ls_df):
    '''
    Inputs:
        complexity_df (gpd.GeoDataFrame)
        ls_df (gpd.GeoDataFrame)
    '''

    joined = gpd.sjoin(complexity_df, ls_df[['geometry', 'grid_idx']], how='left', op='intersects')
    joined = joined.merge(ls_df, how='left', on='grid_idx')

    return joined 



# gdf_complexity = load_complexity('Africa', 'DJI', 'complexity_DJI.1.1_1.csv')
# ls_path = DATA / 'LandScan_Global_2018' / 'ls_2018.tif'
# ls_df = gpd.read_file(ls_path)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='utilities to process LandScan data')
    subparsers = parser.add_subparsers()

    parser_from_tif = subparsers.add_parser('from_tif', help='Convert the .tif to geojson')
    parser_from_tif.set_defaults(func = main_process_tif_to_geojson)

    args = parser.parse_args()
    args.func()