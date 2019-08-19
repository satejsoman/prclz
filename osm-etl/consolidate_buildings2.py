import argparse
from typing import List 
import logging
from logging import info
from pathlib import Path

import geopandas as gpd
import pandas as pd
import glob 

from shapely.geometry import Polygon

"""
I've just made a few edits to the arg structure in consolidate_buildings.py
so that it is easier (for me) to run over all the region-specific subfolders
    - Cooper
"""

GEOJSON_PATH = "../data/geojson"

def to_polygon(geometry): 
    try:
        return Polygon(geometry)
    except ValueError:
        return geometry


def process_all(all_polygon_files: List[str], all_buildings_files: List[str]) -> (str, str, str):
    """
    Given a list of all the polygon building files, this uniquely identifies
    a country to process, so then provide the corrresponding 3 args
    for the main function
    """

    all_linestrings_files = [x.replace("polygons", "linestrings") for x in all_polygon_files]
    all_outputs_files = [x.replace("building_polygons", "buildings") for x in all_polygon_files]

    for args in zip(all_polygon_files, all_linestrings_files, all_outputs_files):

    	if os.path.isfile(args[-1]):
    		info("File exists -- skipping: ", args[-1])
    	else:
        	process(*args)


def process(polygons_path: str, linestrings_path: str, output: str):
    info("Unifying %s, %s", polygons_path, linestrings_path)
    polygons    = gpd.read_file(polygons_path)
    linestrings = gpd.read_file(linestrings_path)

    linestrings["geometry"] = linestrings["geometry"].apply(to_polygon)
    concat = pd.concat([polygons, linestrings], sort=True)
    
    info("Saving valid geometries to %s", output)
    concat[~concat.is_empty].to_file(output, driver='GeoJSON')


# def setup(args=None):
#     # logging
#     logging.basicConfig(format="%(asctime)s/%(filename)s/%(funcName)s | %(levelname)s - %(message)s", datefmt='%Y-%m-%d %H:%M:%S')
#     logging.getLogger().setLevel("INFO")

#     # read arguments
#     parser = argparse.ArgumentParser(description='Consolidate building footprint geometries.')
#     parser.add_argument('--polygons',    required=True, type=Path, help='path to polygons',    dest="polygons_path")
#     parser.add_argument('--linestrings', required=True, type=Path, help='path to linestrings', dest="linestrings_path")
#     parser.add_argument('--output',      required=True, type=Path, help='path to output')
    
#     return parser.parse_args(args)


if __name__ == "__main__":

    logging.basicConfig(format="%(asctime)s/%(filename)s/%(funcName)s | %(levelname)s - %(message)s", datefmt='%Y-%m-%d %H:%M:%S')
    logging.getLogger().setLevel("INFO")    

    all_files = glob.glob(GEOJSON_PATH + "/*/*building_polygons.geojson")
    process_all(all_files)

