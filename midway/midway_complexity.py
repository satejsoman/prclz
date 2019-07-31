import argparse
import json
import logging
from logging import info, warning
from pathlib import Path
from typing import List, Optional, Union

import geopandas as gpd
import pandas as pd
import shapely.wkt
from joblib import Parallel, delayed
from networkx.readwrite import json_graph
from shapely.geometry import MultiPolygon, Polygon

from prclz.blocks.methods import BufferedLineDifference
from prclz.complexity import get_complexity, get_weak_dual_sequence


def weak_dual_sequence_to_json_string(weak_duals):
    return json.dumps(list(map(json_graph.node_link_data, weak_duals)), default=lambda _:_.__dict__)

def read_file(path, **kwargs):
    """ ensures geometry set correctly when reading from csv
    otherwise, pd.BlockManager malformed when using gpd.read_file(*) """
    if not path.endswith(".csv"):
        return gpd.read_file(path, **kwargs)
    raw = pd.read_csv(path, **kwargs)
    raw["geometry"] = raw["geometry"].apply(shapely.wkt.loads)
    return gpd.GeoDataFrame(raw, geometry="geometry")

def main(blocks_path: Path, buildings_path: Path, complexity_output: Path, graph_output: Optional[Path], parallelism: int):
    info("Reading geospatial data from files.")
    blocks    = read_file(str(blocks_path), index_col="block_id", usecols=["block_id", "geometry"], low_memory=False)
    buildings = read_file(str(buildings_path), low_memory=False)
    
    buildings["geometry"] = buildings.centroid

    info("Aggregating buildings by street block.")
    block_aggregation = gpd.sjoin(blocks, buildings, how="right", op="intersects")
    block_aggregation = block_aggregation[pd.notnull(block_aggregation["index_left"])].groupby("index_left")["geometry"].agg(list)
    block_aggregation.name = "centroids"
    block_buildings = blocks.join(block_aggregation)
    block_buildings = block_buildings[pd.notnull(block_buildings["centroids"])]

    info("Generating weak dual sequences.")
    block_buildings["weak_duals"] = Parallel(n_jobs=parallelism, verbose=50)(delayed(get_weak_dual_sequence)(block, centroids) for (block, centroids) in block_buildings[["geometry", "centroids"]].itertuples(index=False))
    
    info("Calculating block complexity.")
    block_buildings["complexity"] = Parallel(n_jobs=parallelism, verbose=50)(delayed(get_complexity)(s_vector) for s_vector in block_buildings["weak_duals"])

    info("Serializing block complexity calculations to %s", complexity_output)
    block_buildings["centroids"] = Parallel(n_jobs=parallelism, verbose=50)(delayed(shapely.geometry.MultiPoint)(centroids) for centroids in block_buildings["centroids"])
    main.df = block_buildings
    block_buildings[['geometry', 'complexity', 'centroids']].to_csv(complexity_output)
    if graph_output:
        info("Serializing graph sequences to %s", graph_output)
        block_buildings["weak_duals"] = Parallel(n_jobs=parallelism, verbose=50)(delayed(weak_dual_sequence_to_json_string)(sequence) for sequence in block_buildings["weak_duals"])
        block_buildings[['weak_duals']].to_csv(complexity_output)

def setup(args=None):
    # logging
    logging.basicConfig(format="%(asctime)s/%(filename)s/%(funcName)s | %(levelname)s - %(message)s", datefmt='%Y-%m-%d %H:%M:%S')
    logging.getLogger().setLevel("INFO")

    # read arguments
    parser = argparse.ArgumentParser(description='Run parcelization workflow on midway2.')
    parser.add_argument('--blocks',      required=True,  type=Path, help='path to blocks',      dest="blocks_path")
    parser.add_argument('--buildings',   required=True,  type=Path, help='path to buildings',   dest="buildings_path")
    parser.add_argument('--output',      required=True,  type=Path, help='path to output',      dest="complexity_output")
    parser.add_argument('--graphs',      required=False, type=Path, help='path to save graphs', dest="graph_output")
    parser.add_argument('--parallelism', default=4,      type=int,  help='number of cores to use')

    return parser.parse_args(args)


if __name__ == "__main__":
    main(**vars(setup()))
