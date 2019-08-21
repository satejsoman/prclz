import argparse
from typing import List 
import logging
from logging import info
from pathlib import Path

import geopandas as gpd
import pandas as pd
import glob 
import os

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


def process_all(all_polygon_files: List[str], replace: bool) -> (str, str, str):
    """
    Given a list of all the polygon building files, this uniquely identifies
    a country to process, so then provide the corrresponding 3 args
    for the main function
    """

    all_linestrings_files = [x.replace("polygons", "linestrings") for x in all_polygon_files]
    all_outputs_files = [x.replace("building_polygons", "buildings") for x in all_polygon_files]

    country_count = len(all_linestrings_files)

    for i, args in enumerate(zip(all_polygon_files, all_linestrings_files, all_outputs_files)):

        if os.path.isfile(args[-1]):
            print("File exists -- skipping: ", args[-1])
        else:
            print("Processing {}/{} -- file: {}".format(i, country_count, args[0]))
            process(*args)


def process(polygons_path: str, linestrings_path: str, output: str):
    #info("Unifying %s, %s", polygons_path, linestrings_path)
    polygons    = gpd.read_file(polygons_path)
    polygons_count = polygons.shape[0]
    polygons_null = polygons['geometry'].isna()
    polygons = polygons[ polygons['geometry'].notnull() ].explode()
    
    linestrings = gpd.read_file(linestrings_path)
    linestrings["geometry"] = linestrings["geometry"].apply(to_polygon)
    linestrings_count = linestrings.shape[0]
    linestrings_null = linestrings['geometry'].isna()
    linestrings = linestrings[ linestrings['geometry'].notnull() ].explode()

    concat = pd.concat([polygons, linestrings], sort=True)
    
    #info("Saving valid geometries to %s", output)
    concat[~concat.is_empty].to_file(output, driver='GeoJSON')

    print("\tDropping {}/{} and {}/{} original polygon and linestrings".format(polygons_null.sum(),
                    polygons_count, linestrings_null.sum(), linestrings_count))


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

    parser = argparse.ArgumentParser(description="Consolidate all building footprint geometries across all countries")
    parser.add_argument('--country', required=True, 
          help='Which country, or All, to process. One of [All, Africa, Asia, Australia-Oceania, Central-America, Europe, North-America, South-America]')
    parser.add_argument('--replace', help="if file already processed, replace and update", action="store_true")

    args = parser.parse_args()    

    # NOTE: the all_files is hardcoded, as currently we process the entire directory
    if args.country == 'All':
        all_files = glob.glob(GEOJSON_PATH + "/*/*building_polygons.geojson")
    else:
        all_files = glob.glob(GEOJSON_PATH + "/{}/*building_polygons.geojson".format(args.country))
    process_all(all_files, replace=args.replace)

