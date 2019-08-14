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


l = ["congo-democratic-republic_buildings.geojson",
"egypt_buildings.geojson",
"kenya_buildings.geojson",
"malawi_buildings.geojson"]


if __name__ == "__main__":

    building_file = l[ int(sys.argv[1]) ]

    print("Calling the script on ", building_file)

    geofabrik_name = building_file.replace("_buildings.geojson", "").replace("_lines.geojson", "")
    gadm_name = geofabrik_to_gadm(geofabrik_name)

    buildings_output, details, all_blocks = split_files_alt(building_file, TRANS_TABLE, return_all_blocks=True)

    file_name = gadm_name + "_nonmatched_map.jpg"

    map_matching_results(buildings_output, all_blocks, file_name)







