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

    if not os.path.isdir("gadm_map_verification"):
        os.mkdir("gadm_map_verification")

    building_file = l[ int(sys.argv[1]) ]

    print("Calling the script on ", building_file)

    geofabrik_name = building_file.replace("_buildings.geojson", "").replace("_lines.geojson", "")
    gadm_name = geofabrik_to_gadm(geofabrik_name)

    all_blocks = join_block_files(gadm_name)

    all_blocks.plot(color='blue', alpha=0.5)

    plt.axis('off')
    file_name = "gadm_blocks_{}.png".format(gadm_name)
    plt.savefig(os.path.join("gadm_map_verification", file_name))

