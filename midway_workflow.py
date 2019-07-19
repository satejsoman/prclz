import argparse
import logging
from pathlib import Path
from itertools import islice

import geopandas as gpd
import matplotlib.pyplot as plt
import overpy
import pandas as pd
from shapely.geometry import Polygon, box
from tqdm import tqdm

from prclz.blocks.methods import BufferedLineDifference
from prclz.complexity import get_complexity, get_weak_dual_sequence
from prclz.plotting import plot_polygons

def run_block_extraction(extractor, linestrings, gadm_index_aggregate):
    return 
gadm_aggregation.progress_apply(
    lambda row: extractor.extract(
        gadm_index_aggregate["geometry"], 
        linestrings["geometry"].iloc[gadm_index_aggregate["index_right"]].unary_union), 
    axis=1)
# run_block_extraction(extractor, linestrings, gadm_agg)


def main(gadm_path, linestrings_path, buildings_path, building_polygons_path, limit_path):
    logging.info("Reading geospatial data from files")
    gadm              = gpd.read_file(gadm_path)
    linestrings       = gpd.read_file(linestrings_path)
    buildings         = gpd.read_file(buildings_path)
    building_polygons = gpd.read_file(building_polygons_path)
    limit             = gpd.read_file(limit_path)

    logging.info("Setting up indices.")
    gadm            = gadm.set_index("GID_3")
    gadm_idx        = gadm.sindex
    linestrings_idx = linestrings.sindex

    logging.info("Aggregating linestrings by GADM-3 delineation.")
    gadm_aggregation =\
        gadm.join(
            gpd.sjoin(gadm, linestrings, how="left", op="intersects")\
                .groupby(lambda idx: idx)["index_right"]\
                .agg(list)
        )[["geometry", "index_right"]]\
        .rename({"index_right" : "linestring_index"}, axis=1)

    extractor = BufferedLineDifference()
    logging.info("Extracting blocks for each delineation using method: %s", extractor)
    blocks = gadm_aggregation.progress_apply(
        lambda row: extractor.extract(row["geometry"], linestrings["geometry"].iloc[row["linestring_index"]].unary_union), 
        axis=1)

    logging.info("Aggregating buildings by street block.")
    block_aggregation = gpd.sjoin(blocks, centroids, how="right", op="intersects")
    block_aggregation = block_aggregation[pd.notnull(block_aggregation["index_left"])].groupby("index_left")["geometry"].agg(list)
    block_aggregation.name = "centroids"
    block_centroids = blocks.join(block_aggregation)
    block_centroids = block_centroids[pd.notnull(block_centroids["centroids"])]

    logging.info("Calculating block complexity.")
    block_centroids["weak_duals"] = block_centroids.progress_apply(get_weak_dual_sequence, axis=1)
    block_centroids["complexity"] = block_centroids["weak_duals"].progress_apply(get_complexity)

    

def setup(args=None):
    # logging
    logging.basicConfig(format="%(asctime)s/%(levelname)s - %(message)s", datefmt='%Y-%m-%d %H:%M:%S')
    logging.getLogger().setLevel("INFO")

    # progress bars
    tqdm.pandas()

    # read arguments
    parser = argparse.ArgumentParser(description='Run parcelization workflow on midway2.')
    parser.add_argument('--gadm',              help='path to GADM file',            type=Path)
    parser.add_argument('--linestrings',       help='path to linestrings',          type=Path)
    parser.add_argument('--buildings',         help='path to building linestrings', type=Path)
    parser.add_argument('--building_polygons', help='path to building polygons',    type=Path)

    return parser.parse_args(args)

if __name__ == "__main__":
    main(**vars(setup()))
