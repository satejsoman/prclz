import numpy as np 
import rasterio 
from pathlib import Path 
import geopandas as gpd 
import pandas as pd 
from shapely.geometry import MultiPolygon, Polygon, MultiLineString
from shapely.wkt import loads
import argparse 
import tqdm

root = Path('../')
DATA = root / 'data' 
COMPLEXITY = DATA / "complexity"


def load_complexity(region, country_code, f):
    p = COMPLEXITY / region / country_code / f
    df = pd.read_csv(p)
    gdf_complexity = gpd.GeoDataFrame(df[['block_id', 'geometry', 'complexity', 'centroids_multipoint']])
    gdf_complexity['geometry'] = gdf_complexity['geometry'].apply(loads)
    gdf_complexity['bldg_count'] = gdf_complexity['centroids_multipoint'].apply(lambda x: len(x))
    gdf_complexity['block_area'] = gdf_complexity['geometry'].area 

    #gdf_bldgs = gpd.GeoDataFrame(df[['block_id', 'centroids_multipoint']])
    return gdf_complexity

def add_landscan_data(ls_dataset, gdf_complexity):

    fn = lambda x: rasterio.features.geometry_window(ls_dataset, [x])
    gdf_complexity['windows'] = gdf_complexity['geometry'].apply(fn)

    return gdf_complexity 

def calculate_population(geom, ls_dataset, window):

    data = ls_dataset.read(1, window=window)


region = 'Africa'
country_code = 'SLE'
gadm = 'SLE.4.2.1_1'
landscan_path = DATA / 'LandScan_Global_2018' / 'raw_tif' / 'ls_2018.tif'

ls_dataset = rasterio.open(landscan_path)
f = "complexity_{}.csv".format(gadm)
gdf_complexity = load_complexity(region, country_code, f)
gdf_complexity = add_landscan_data(ls_dataset, gdf_complexity)

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
    print("...complete!")

    x_coords = np.linspace(left, right, dataset.shape[0])
    y_coords = np.linspace(top, bottom, dataset.shape[1])

    df_dict = {}
    df_dict['geometry'] = []
    df_dict['population'] = []
    df_dict['grid_idx'] = []



def make_landscan_gadm_file(region, country_code, gadm, landscan_dataset=None):

    # Get complexity file
    f = "complexity_{}.csv".format(gadm)
    complexity_gdf = load_complexity(region, country_code, f)

    if landscan_dataset is None:
        ls_path = DATA / 'LandScan_Global_2018' / 'raw_tif' / 'ls_2018.tif'
        landscan_dataset = rasterio.open(ls_path)

    # Get the window in our LandScan dataset that contains the AoI
    geom = complexity_gdf['geometry']
    window = rasterio.features.geometry_window(landscan_dataset, geom)



# if __name__ == "__main__":

#     parser = argparse.ArgumentParser(description='utilities to process LandScan data')
#     subparsers = parser.add_subparsers()

#     parser_from_tif = subparsers.add_parser('from_tif', help='Convert the .tif to geojson')
#     parser_from_tif.set_defaults(func = main_process_tif_to_geojson)

#     args = parser.parse_args()
#     args.func()