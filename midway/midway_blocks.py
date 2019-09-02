import argparse
import datetime
import logging
from logging import error, info, warning
from pathlib import Path
from typing import List, Union

import geopandas as gpd
from joblib import Parallel, delayed
from shapely.geometry import MultiLineString, MultiPolygon, Polygon

from prclz.blocks.methods import BufferedLineDifference


def get_gadm_level_column(gadm: gpd.GeoDataFrame, level: int) -> str:
    gadm_level_column = "GID_{}".format(level)
    while gadm_level_column not in gadm.columns and level > 0:
        warning("GID column for GADM level %s not found, trying with level %s", level, level-1)
        level -= 1
        gadm_level_column = "GID_{}".format(level)
    info("Using GID column for GADM level %s", level)
    return gadm_level_column, level

def extract(index: str, geometry: Union[Polygon, MultiPolygon], linestrings: gpd.GeoDataFrame, output_dir: Path, overwrite: bool, timestamp: str) -> None:
    logging.basicConfig(format="%(asctime)s/%(filename)s/%(funcName)s | %(levelname)s - %(message)s", datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)
    logger = logging.getLogger()
    logger.addHandler(logging.FileHandler(output_dir/(index + "_" + timestamp + ".log")))

    try: 
        filename = output_dir/("blocks_{}.csv".format(index))
        if (not filename.exists()) or (filename.exists() and overwrite):
            # minimize synchronization barrier by constructing a new extractor
            block_polygons = BufferedLineDifference().extract(geometry, linestrings.unary_union)
            blocks = gpd.GeoDataFrame(
                [(index + "_" + str(i), polygon) for (i, polygon) in enumerate(block_polygons)], 
                columns=["block_id", "geometry"])
            blocks.set_index("block_id")
            blocks.to_csv(filename)
            logger.info("Serialized blocks from %s to %s", index, filename)
        else:
            logger.info("Skipping %s (file %s exists and no overwrite flag given)", index, filename)
    except Exception as e:
        logger.error("%s while processing %s: %s", type(e).__name__, index, e)
        with open(output_dir/("error_{}".format(index)), 'a') as error_file:
            print(e, file=error_file)

def main(gadm_path, linestrings_path, output_dir, level, parallelism, overwrite):
    timestamp = datetime.datetime.now().isoformat()
    logger = logging.getLogger()
    logger.addHandler(logging.FileHandler(output_dir/(timestamp + "_main.log")))

    info("Reading geospatial data from files.")
    gadm              = gpd.read_file(str(gadm_path))
    linestrings       = gpd.read_file(str(linestrings_path))

    info("Setting up indices.")
    gamd_column, level = get_gadm_level_column(gadm, level)
    gadm               = gadm.set_index(gamd_column, level)

    info("Overlaying GADM boundaries on linestrings.")
    overlay = gpd.sjoin(gadm, linestrings, how="left", op="intersects")\
                 .groupby(lambda idx: idx)["index_right"]\
                 .agg(list)

    info("Aggregating linestrings by GADM-%s delineation.", level)
    gadm_aggregation = gadm.join(overlay)[["geometry", "index_right"]]\
                           .rename({"index_right": "linestring_index"}, axis=1)

    extractor = BufferedLineDifference()
    info("Extracting blocks for each delineation using method: %s.", extractor)
    Parallel(n_jobs=parallelism, verbose=100)(
        delayed(extract)(index, geometry, linestrings.iloc[ls_idx], output_dir, overwrite, timestamp) 
        for (index, geometry, ls_idx) in gadm_aggregation.itertuples())

    info("Done.")


def setup(args=None):
    # logging
    logging.basicConfig(format="%(asctime)s/%(filename)s/%(funcName)s | %(levelname)s - %(message)s", datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)

    # read arguments
    parser = argparse.ArgumentParser(description='Run parcelization workflow on midway2.')
    parser.add_argument('--gadm',        required=True, type=Path, help='path to GADM file',   dest="gadm_path")
    parser.add_argument('--linestrings', required=True, type=Path, help='path to linestrings', dest="linestrings_path")
    parser.add_argument('--output',      required=True, type=Path, help='path to  output',     dest="output_dir")
    parser.add_argument('--level',       default=5,     type=int,  help='GADM level to use')
    parser.add_argument('--parallelism', default=4,     type=int,  help='number of cores to use')
    parser.add_argument('--overwrite',   default=False, type=bool, help='whether to overwrite existing block files')

    return parser.parse_args(args)


if __name__ == "__main__":
    main(**vars(setup()))
