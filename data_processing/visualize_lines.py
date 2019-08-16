from split_building_files import *

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

GEOJSON_PATH = "../data/geojson/Africa"

l = ["congo-democratic-republic_buildings.geojson",
"egypt_buildings.geojson",
"kenya_buildings.geojson",
"malawi_buildings.geojson"]

#l = ["djibouti_lines.geojson"]

if __name__ == "__main__":

    if not os.path.isdir("lines_verification"):
        os.mkdir("lines_verification")

    building_file = l[ int(sys.argv[1]) ]

    print("Calling the script on ", building_file)
    geofabrik_name = building_file.replace("_buildings.geojson", "").replace("_lines.geojson", "")
    gadm_name = geofabrik_to_gadm(geofabrik_name)

    gdf = gpd.read_file(os.path.join(GEOJSON_PATH, "djibouti_lines.geojson"))

    gdf['has_natural'] = gdf['natural'].notnull().map(int)
    gdf['has_highway'] = gdf['highway'].notnull().map(int)
    gdf['has_waterway'] = gdf['waterway'].notnull().map(int)
    gdf['sum_check'] = gdf['has_natural'] + gdf['has_highway'] + gdf['has_waterway']

    # assert (gdf['sum_check']==1).all(), "Sum observations don't have mutually exclusive and complete tags"

    # gdf['flag_int'] = (gdf['has_natural']*NATURAL_TAG 
    #     + gdf['has_highway']*HIGHWAY_TAG + gdf['has_waterway']*WATERWAY_TAG)

    ax = gdf[ gdf.has_natural==1 ].plot(color='green', figsize=(35,35))
    gdf[ gdf.has_highway==1 ].plot(ax=ax, color='black')
    gdf[ gdf.has_waterway==1 ].plot(ax=ax, color='blue')


    #gdf.plot(figsize=(25,25), column='flag_int', legend=True)

    plt.axis('off')
    file_name = "osm_lines_{}.png".format(gadm_name)
    plt.savefig(os.path.join("lines_verification", file_name))