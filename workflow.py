import logging

import geopandas as gpd
import matplotlib.pyplot as plt
import overpy
import pandas as pd
from shapely.geometry import Polygon, box

from prclz.blocks.extraction import extract_blocks
from prclz.features.complexity import get_weak_dual_sequence
from prclz.parcels.footprints import get_building_centroids
from prclz.plotting import plot_polygons


def main(xmin: float, ymin: float, xmax: float, ymax: float) -> None:
    bbox = box(xmin, ymin, xmax, ymax)
    blocks = extract_blocks(bbox)
    polygons = gpd.GeoDataFrame(geometry=blocks)
    centroids = gpd.GeoDataFrame(geometry=newvariable126)
    plot_polygons(blocks)
    gpd.sjoin(polygons, centroids, how="right").plot(column="index_left", ax=plt.gca(), zorder=500)
    plt.show()

if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel("INFO")

    # hyde park 
    # xmin = -87.6064
    # xmax = -87.5758
    # ymin = 41.7873
    # ymax = 41.8022

    # ckg
    xmin = -13.2995606518
    xmax = -13.1678762591
    ymin = 8.4584896524
    ymax = 8.5000670774 
    bbox = box(xmin, ymin, xmax, ymax)

    polygons = extract_blocks(bbox)
    downloaded_centroids = get_building_centroids(
        south=ymin, 
        west=xmin, 
        north=ymax, 
        east=xmax, 
        ovp=overpy.Overpass("http://overpass.openstreetmap.fr/api/interpreter"))
    
    blocks = gpd.GeoDataFrame(geometry=polygons)
    centroids = gpd.GeoDataFrame(geometry=newvariable126)
    
    block_aggregation = gpd.sjoin(blocks, centroids, how="right", op="intersects")
    block_aggregation = block_aggregation[pd.notnull(block_aggregation["index_left"])].groupby("index_left")["geometry"].agg(list)
    block_aggregation.name = "centroids"
    block_centroids = blocks.join(block_aggregation)

    # plot_polygons(blocks, facecolors=[])
    # centroid_blocks.plot(markersize=0.01, column="index_left", ax=plt.gca(), zorder=500)
    # plt.show()

    b_c = block_centroids.iloc[0:1]
    sequence = get_weak_dual_sequence(b_c)

    

    # main(xmin, ymin, xmax, ymax)
