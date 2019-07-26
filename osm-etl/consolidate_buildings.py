import argparse
import logging
from logging import info
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon


def to_polygon(geometry): 
    try:
        return Polygon(geometry)
    except ValueError:
        return geometry


def main(polygons_path: Path, linestrings_path: Path, output: Path):
    info("Unifying %s, %s", polygons_path.resolve(), linestrings_path.resolve())
    polygons    = gpd.read_file(str(polygons_path))
    linestrings = gpd.read_file(str(linestrings_path))

    linestrings["geometry"] = linestrings["geometry"].apply(to_polygon)
    concat = pd.concat([polygons, linestrings], sort=True)
    
    info("Saving valid geometries to %s", output.resolve())
    concat[~concat.is_empty].to_file(str(output))


def setup(args=None):
    # logging
    logging.basicConfig(format="%(asctime)s/%(filename)s/%(funcName)s | %(levelname)s - %(message)s", datefmt='%Y-%m-%d %H:%M:%S')
    logging.getLogger().setLevel("INFO")

    # progress bars
    tqdm.pandas()

    # read arguments
    parser = argparse.ArgumentParser(description='Consolidate building footprint geometries.')
    parser.add_argument('--polygons',    required=True, type=Path, help='path to polygons',    dest="polygons_path")
    parser.add_argument('--linestrings', required=True, type=Path, help='path to linestrings', dest="linestrings_path")
    parser.add_argument('--output',      required=True, type=Path, help='path to output')
    
    return parser.parse_args(args)


if __name__ == "__main__":
    main(**vars(setup()))
