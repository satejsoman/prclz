import geopandas as gpd 
import pandas as pd 
from shapely.geometry import MultiPolygon, Polygon, MultiLineString
from shapely.ops import cascaded_union
from shapely.wkt import loads 
from pathlib import Path 

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

def load_complexity_files(region: str, gadm: str) -> gpd.GeoDataFrame:
    
    complexity_files = (COMPLEXITY_PATH / region / gadm).iterdir()
    df = pd.concat([pd.read_csv(f) for f in complexity_files])

    gdf = gpd.GeoDataFrame(df)
    gdf['geometry'] = gdf['geometry'].apply(loads)
    gdf.set_geometry('geometry', inplace=True)
    gdf['centroids_multipoint'] = gdf['centroids_multipoint'].apply(loads)
    gdf['gadm'] = gdf['block_id'].apply(get_gadm_from_block)
    gdf['bldg_count'] = gdf['centroids_multipoint'].apply(lambda x: len(x))

    return gdf 

def make_building_summaries(region: str, gadm: str):

    gdf = load_complexity_files(region, gadm)
    summary = summarize_bldg_counts(gdf)
    summary.reset_index(inplace=True)

    save_to = ANALYSIS_PATH / region / gadm 
    if not save_to.exists():
        save_to.mkdir(parents=True)
    summary.to_csv(save_to / "{}_bldgs_per_gadm_summary.csv".format(gadm))



dji_complexity_files = list(COMPLEXITY_PATH.rglob("*complexity*.csv"))
dji_buildings = list(BUILDING_PATH.rglob("*buildings_DJI*.geojson"))
df = pd.concat([pd.read_csv(f) for f in dji_complexity_files])
buildings = pd.concat(gpd.read_file(f) for f in dji_buildings)

gdf = gpd.GeoDataFrame(df)
gdf['geometry'] = gdf['geometry'].apply(loads)
gdf.set_geometry('geometry', inplace=True)
gdf['centroids_multipoint'] = gdf['centroids_multipoint'].apply(loads)
gdf['gadm'] = gdf['block_id'].apply(get_gadm_from_block)
gdf['block_count'] = 1
gdf['bldg_count'] = gdf['centroids_multipoint'].apply(lambda x: len(x))

ax = gdf.plot(column='complexity')
buildings.plot(ax=ax, color='black')