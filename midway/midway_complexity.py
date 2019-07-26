import argparse
import logging
from logging import info, warning
from pathlib import Path
from typing import List, Union

import geopandas as gpd
from joblib import Parallel, delayed
from shapely.geometry import MultiPolygon, Polygon
import shapely.wkt
import pandas as pd

from prclz.blocks.methods import BufferedLineDifference
from prclz.complexity import get_weak_dual_sequence, get_complexity

def read_from_csv(path):
    """ ensures geometry set correctly when reading from csv
    otherwise, pd.BlockManager malformed when using gpd.read_file(*) """
    raw = pd.read_csv(path, index_col="block_id", usecols=["block_id", "geometry"])
    raw["geometry"] = raw["geometry"].apply(shapely.wkt.loads)
    return gpd.GeoDataFrame(raw, geometry="geometry")

def main(blocks_path: Path, buildings_path: Path):
    info("Reading geospatial data from files.")
    blocks    = read_from_csv(str(blocks_path))
    buildings = gpd.read_file(str(buildings_path))
    
    centroids = buildings.centroid

    info("Aggregating buildings by street block.")
    block_aggregation = gpd.sjoin(blocks, centroids, how="right", op="intersects")
    block_aggregation = block_aggregation[pd.notnull(block_aggregation["index_left"])].groupby("index_left")["geometry"].agg(list)
    block_aggregation.name = "centroids"
    block_centroids = blocks.join(block_aggregation)
    block_centroids = block_centroids[pd.notnull(block_centroids["centroids"])]

    info("Generating weak dual sequences.")
    block_centroids["weak_duals"] = block_centroids.progress_apply(get_weak_dual_sequence, axis=1)
    
    info("Calculating block complexity.")
    block_centroids["complexity"] = block_centroids["weak_duals"].progress_apply(get_complexity)

    info("Serializing block complexity calculations to %s", complexity_destination)
    save_to(block_centroids, complexity_destination)

def setup(args=None):
    # logging
    logging.basicConfig(format="%(asctime)s/%(filename)s/%(funcName)s | %(levelname)s - %(message)s", datefmt='%Y-%m-%d %H:%M:%S')
    logging.getLogger().setLevel("INFO")

    # read arguments
    parser = argparse.ArgumentParser(description='Run parcelization workflow on midway2.')
    parser.add_argument('--blocks',      required=True, type=Path, help='path to blocks',    dest="blocks_path")
    parser.add_argument('--buildings',   required=True, type=Path, help='path to buildings', dest="buildings_path")
    parser.add_argument('--output',      required=True, type=Path, help='path to output',    dest="output_dir")
    parser.add_argument('--parallelism', default=4,     type=int,  help='number of cores to use')

    return parser.parse_args(args)


if __name__ == "__main__":
    main(**vars(setup()))
