import geopandas as gpd 
import pandas as pd 
from shapely.geometry import MultiPolygon, Polygon, MultiLineString
from shapely.ops import cascaded_union
from shapely.wkt import loads 
from pathlib import Path 
import argparse
from typing import List 


BLOCK_PATH = Path("../data/blocks")
GEOJSON_PATH = Path("../data/geojson")
BUILDING_PATH = Path("../data/buildings")
COMPLEXITY_PATH = Path("../data/complexity/")
DATA_PATH = Path("../data")
ANALYSIS_PATH = Path("../analysis")

def get_gadm_from_block(block_id):
    return "_".join(block_id.split("_")[0:-1])


def summarize_bldg_counts(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    
    summary = gdf.groupby('gadm')['bldg_count'].describe()
    summary['total_bldgs'] = summary['count']*summary['mean']
    summary.rename(columns={c:"bldg_"+c for c in summary.columns}, inplace=True)
    summary.rename(columns={'bldg_count':'block_count'}, inplace=True)

    return summary 

def load_complexity_files(region: str, gadm: str, gadm_list: List[str] = None) -> gpd.GeoDataFrame:
    
    def check(file_path, gadm_list):
        file_path = str(file_path)
        for gadm in gadm_list:
            if gadm in file_path:
                return True
        return False

    complexity_files = (COMPLEXITY_PATH / region / gadm).iterdir()
    if gadm_list is not None:
        df = pd.concat([pd.read_csv(f) for f in complexity_files if check(f,gadm_list)])
    else:
        df = pd.concat([pd.read_csv(f) for f in complexity_files])

    gdf = gpd.GeoDataFrame(df)
    gdf['geometry'] = gdf['geometry'].apply(loads)
    gdf.set_geometry('geometry', inplace=True)
    gdf['centroids_multipoint'] = gdf['centroids_multipoint'].apply(loads)
    gdf['gadm'] = gdf['block_id'].apply(get_gadm_from_block)
    gdf['bldg_count'] = gdf['centroids_multipoint'].apply(lambda x: len(x))

    return gdf 

# ['bldg_count', 'gadm', 'block_id']

def make_building_summaries_by_gadm(region: str, country_gadm: str):

    print("--Loading data for {}-{}".format(region, country_gadm))
    gdf = load_complexity_files(region, country_gadm)
    print("......complete!\n")

    print("--Begin summarize analysis")
    summary = summarize_bldg_counts(gdf)
    print("......complete!\n")
    summary.reset_index(inplace=True)

    save_to = ANALYSIS_PATH / (str(region)+"by_gadm") 
    if not save_to.exists():
        save_to.mkdir(parents=True)
    summary.to_csv(save_to / "{}_bldgs_per_gadm_summary.csv".format(country_gadm))

def make_building_summaries_by_block(region: str, country_gadm:str, gadm_list:List[str]):

    print("--Loading data for {}-{}".format(region, country_gadm))
    gdf = load_complexity_files(region, country_gadm, gadm_list)[['gadm', 'block_id', 'bldg_count']]
    print("......complete!\n")
    save_to = ANALYSIS_PATH / (str(region)+"by_block")
    if not save_to.exists():
        save_to.mkdir(parents=True)
    gdf.to_csv(save_to / "{}_bldgs_per_block_summary.csv".format(country_gadm))



if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Get summary stats on distribution of buildings over blocks/gadms')
    parser.add_argument('--country', type=str, dest='country_gadm', required=True, help="country gadm code to process")
    parser.add_argument('--region', type=str, required=True, help="region to process")
    parser.add_argument('--gadm', action='append', dest='gadm_list', help='process these gadm at the block level instead')

    args = parser.parse_args()

    if hasattr(args, 'gadm_list'):
        make_building_summaries_by_block(**vars(args))
    else:
        make_building_summaries_by_gadm(**vars(args))

