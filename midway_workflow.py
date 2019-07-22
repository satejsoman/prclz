import argparse
import logging
from logging import info, warn 
from pathlib import Path

import geopandas as gpd
import pandas as pd
from tqdm import tqdm

from prclz.blocks.methods import BufferedLineDifference
from prclz.complexity import get_complexity, get_weak_dual_sequence


def save_to(df, dst):
    if dst.endswith(".json"):
        df.to_json(dst)
    else:
        df.to_csv(dst)

def get_gadm_level_column(gadm: gpd.GeoDataFrame, level: int) -> str:
    gadm_level_column = "GID_{}".format(level)
    while gadm_level_column not in gadm.columns and level > 0:
        warn("GID column for GADM level %s not found, trying with level %s", level, level-1)
        level -= 1
        gadm_level_column = "GID_{}".format(level)
    info("Using GID column for GADM level %s", level)
    return gadm_level_column


def main(gadm_path, linestrings_path, buildings_path, building_polygons_path, blocks, complexity, level):
    info("Reading geospatial data from files")
    gadm              = gpd.read_file(gadm_path)
    linestrings       = gpd.read_file(linestrings_path)
    buildings         = gpd.read_file(buildings_path)
    building_polygons = gpd.read_file(building_polygons_path)
    blocks_dst        = blocks
    complexity_dst    = complexity

    info("Setting up indices.")
    gadm_level_column = get_gadm_level_column(gadm, level)
    gadm              = gadm.set_index(gadm_level_column)
    gadm_idx          = gadm.sindex
    linestrings_idx   = linestrings.sindex

    info("Aggregating linestrings by GADM-%s delineation.", level)
    gadm_aggregation =\
        gadm.join(
            gpd.sjoin(gadm, linestrings, how="left", op="intersects")\
               .groupby(lambda idx: idx)["index_right"]\
               .agg(list)
        )[["geometry", "index_right"]]\
        .rename({"index_right" : "linestring_index"}, axis=1)

    extractor = BufferedLineDifference()
    info("Extracting blocks for each delineation using method: %s", extractor)
    blocks = gadm_aggregation.progress_apply(
        lambda row: extractor.extract(row["geometry"], linestrings["geometry"].iloc[row["linestring_index"]].unary_union), 
        axis=1)
    
    info("Serializing blocks to %s", blocks_destination)
    save_to(blocks, blocks_destination)

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
    parser.add_argument('--blocks',            help='path to blocks output',        type=Path)
    parser.add_argument('--complexity',        help='path to complexity output',    type=Path)
    parser.add_argument('--level',             help='GADM level to use for delineation', type=int, default=3)

    return parser.parse_args(args)

if __name__ == "__main__":
    main(**vars(setup()))
