import numpy as np 
import rasterio 
import rasterio.features
from pathlib import Path 
import geopandas as gpd 
import pandas as pd 
from shapely.geometry import MultiPolygon, Polygon, MultiLineString
from shapely.wkt import loads
import argparse 
import tqdm
import copy 

root = Path('../')
DATA = root / 'data' 
COMPLEXITY = DATA / "complexity"


def load_complexity(region, country_code, f):
    p = COMPLEXITY / region / country_code / f
    df = pd.read_csv(p)
    gdf_complexity = gpd.GeoDataFrame(df[['block_id', 'geometry', 'complexity', 'centroids_multipoint']])
    gdf_complexity['geometry'] = gdf_complexity['geometry'].apply(loads)
    gdf_complexity.geometry.crs = {'init': 'epsg:4326'}  
    gdf_complexity.crs = {'init': 'epsg:4326'}  
    gdf_complexity['bldg_count'] = gdf_complexity['centroids_multipoint'].apply(lambda x: len(x))
    #print(gdf_complexity.crs)
    #gdf_complexity = gdf_complexity.to_crs({'init': 'epsg:3395'})
    gdf_complexity['block_area_km2'] = gdf_complexity['geometry'].to_crs({'init': 'epsg:3395'}).area / (10**6)  
    #gdf_complexity['block_area_km2'] = gdf_complexity['geometry'].to_crs({'init': 'epsg:3395'}).area / (10**6)  
    #gdf_complexity = gdf_complexity.to_crs({'init': 'epsg:4326'})

    #gdf_bldgs = gpd.GeoDataFrame(df[['block_id', 'centroids_multipoint']])
    return gdf_complexity

def add_landscan_data(ls_dataset, gdf_complexity):

    fn = lambda x: rasterio.features.geometry_window(ls_dataset, [x])
    gdf_complexity['windows'] = gdf_complexity['geometry'].apply(fn)

    return gdf_complexity 

def calculate_population_uniform_dist(geom, ls_dataset, window):

    data = ls_dataset.read(1, window=window)
    trans = ls_dataset.window_transform(window)

    geo_series = []
    pop_series = []
    for shape, pop in rasterio.features.shapes(data, transform=trans):
        geo_series.append(Polygon(shape['coordinates'][0]))
        assert shape['type'] == 'Polygon', "ERROR -- not Polygon"
        pop_series.append(pop)
    geo_series = gpd.GeoSeries(geo_series)
    inter_pct = geo_series.intersection(geom).area / geo_series.area 

    avg_pop = (inter_pct.values * np.array(pop_series)).sum()

    #return geo_series, pop_series 
    return avg_pop

def process_gadm_landscan(region, country_code, gadm):

    # region = 'Africa'
    # country_code = 'DJI'
    # country_code = 'SLE'
    # gadm = 'SLE.4.2.1_1'
    # gadm = 'DJI.1.1_1'
    landscan_path = DATA / 'LandScan_Global_2018' / 'raw_tif' / 'ls_2018.tif'

    ls_dataset = rasterio.open(landscan_path)
    f = "complexity_{}.csv".format(gadm)

    # Load the complexity file
    gdf_complexity = load_complexity(region, country_code, f)

    # Add the landscan window for each block's geometry
    gdf_complexity = add_landscan_data(ls_dataset, gdf_complexity)

    # Now calculate the pop estimate for each block
    pop_fn = lambda s: calculate_population_uniform_dist(s['geometry'], ls_dataset, s['windows'])
    gdf_complexity['pop_est'] = gdf_complexity.apply(pop_fn, axis=1)
    gdf_complexity['windows'] = gdf_complexity['windows'].map(lambda x: x.todict())
    gdf_complexity['geometry'] = gdf_complexity['geometry'].map(lambda x: x.wkt)

    f = "complexity_pop_{}.csv".format(gadm)
    output_path = DATA / 'LandScan_Global_2018' / region / country_code
    output_path.mkdir(parents=True, exist_ok=True)
    #gdf_complexity.to_file(output_path / f, driver='GeoJSON')
    gdf_complexity.to_csv(output_path / f)

def process_path_landscan(path_to_complexity_files):

    p = Path(path_to_complexity_files)
    country_code = p.stem 
    region = p.parent.stem
    all_files = list(p.iterdir())
    for full_path in tqdm.tqdm(all_files, total=len(all_files)):
        gadm = full_path.stem.replace('complexity_', '')
        process_gadm_landscan(region, country_code, gadm)

# obs0 = gdf_complexity.iloc[0]
# window = obs0['windows']
# geom = obs0['geometry']   

# geo_series, pop_series = calculate_population(geom, ls_dataset, window)
# df = gpd.GeoDataFrame({'geometry':geo_series, 'pop': pop_series}) 

# ax = df.plot(column=df['pop'])
# # We just need a function to distribute the data pro-rata 
# # based on some intersection


# def main_process_tif_to_geojson():
#     landscan_path = DATA / 'LandScan_Global_2018' / 'ls_2018.tif'

#     dataset = rasterio.open(landscan_path)
#     bounds = dataset.bounds 
#     resolution = 30 / 3600 # resolution of dataset in degrees
#     delta = resolution

#     top = bounds.top 
#     bottom = bounds.bottom 
#     left = bounds.left 
#     right = bounds.right 

#     print("Reading tif file....")
#     mat = dataset.read(1)
#     print("...complete!")

#     x_coords = np.linspace(left, right, dataset.shape[0])
#     y_coords = np.linspace(top, bottom, dataset.shape[1])

#     df_dict = {}
#     df_dict['geometry'] = []
#     df_dict['population'] = []
#     df_dict['grid_idx'] = []



# def make_landscan_gadm_file(region, country_code, gadm, landscan_dataset=None):

#     # Get complexity file
#     f = "complexity_{}.csv".format(gadm)
#     complexity_gdf = load_complexity(region, country_code, f)

#     if landscan_dataset is None:
#         ls_path = DATA / 'LandScan_Global_2018' / 'raw_tif' / 'ls_2018.tif'
#         landscan_dataset = rasterio.open(ls_path)

#     # Get the window in our LandScan dataset that contains the AoI
#     geom = complexity_gdf['geometry']
#     window = rasterio.features.geometry_window(landscan_dataset, geom)



if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='utilities to process LandScan data')
    subparsers = parser.add_subparsers()

    # Args for when you just want a single GADM
    sub_parser_single = subparsers.add_parser('single')
    sub_parser_single.add_argument('region', type=str, help='Geographic region')
    sub_parser_single.add_argument('country_code', type=str, help='3-letter country code')
    sub_parser_single.add_argument('gadm', type=str, help='gadm code')
    sub_parser_single.set_defaults(func=process_gadm_landscan)
    
    # Args for doing a directory
    sub_parser_path = subparsers.add_parser('path')
    sub_parser_path.add_argument('path_to_complexity_files', type=str, help='path to a complexity folder of which to process')
    sub_parser_path.set_defaults(func=process_path_landscan)
    
    args = parser.parse_args()
    d_args = copy.copy(vars(args))
    del d_args['func']
    args.func(**d_args)