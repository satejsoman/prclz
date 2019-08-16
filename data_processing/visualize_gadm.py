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

GADM_PATH = "../data/GADM"


l = ["COD", "KEN", "MWI", "EGY"]

def sort_fn(fname, gadm_name):

    s = fname.replace("gadm36_", "").replace("_","").replace(".shp","")
    s = s.replace(gadm_name, "")

    return int(s)


if __name__ == "__main__":

    if not os.path.isdir("raw_gadm"):
        os.mkdir("raw_gadm")

    gadm_name = l[ int(sys.argv[1]) ]

    print("Calling the script on ", gadm_name)

    path = os.path.join(GADM_PATH, gadm_name)

    shp_files = [x for x in os.listdir(path) if ".shp" in x]
    shp_files.sort(key = lambda x: sort_fn(x, gadm_name))

    shp_file_first = gpd.read_file(os.path.join(path, shp_files[0]))
    shp_file_last = gpd.read_file(os.path.join(path, shp_files[-1]))


    ax = shp_file_first.plot(color='blue', alpha=0.25, figsize=(25,25))
    shp_file_last.plot(ax=ax, edgecolor='black', facecolor=None )
    plt.axis('off')

    f = "gadm_{}.png".format(gadm_name)

    plt.savefig(os.path.join("raw_gadm", f), bbox_inches='tight', pad_inches=0)