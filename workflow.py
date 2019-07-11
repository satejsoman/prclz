import logging

import geopandas as gpd
import matplotlib.pyplot as plt
import overpy
import pandas as pd
from mpl_toolkits.axes_grid1 import make_axes_locatable
from shapely.geometry import Polygon, box

from prclz.blocks.extraction import extract_blocks
from prclz.complexity import get_complexity, get_weak_dual_sequence
from prclz.parcels import get_building_centroids
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
    logging.basicConfig(format="%(asctime)s/%(levelname)s - %(message)s", datefmt='%Y-%m-%d %H:%M:%S')
    logging.getLogger().setLevel("INFO")

    # hyde park 
    # xmin = -87.7764
    # xmax = -87.5758
    # ymin = 41.7873
    # ymax = 41.8022
    xmin = -87.7596
    xmax = -87.5758
    ymin = 41.7684
    ymax = 41.8022

    # south chicago 
    # xmin = -87.719650268555
    # xmax = -87.558288574219
    # ymin = 41.768495030303
    # ymax = 41.892310594158

    # freetown/ckg
    # ymin = 8.4676606359473
    # xmin = -13.266763687134
    # ymax = 8.4968634271965
    # xmax = -13.231616020203

    # freetown
    # xmin = -13.2995606518
    # xmax = -13.1678762591
    # ymin = 8.4584896524
    # ymax = 8.5000670774 

    #chicago 
    # ymin = 41.737503724226 
    # ymax = 41.935487296653 
    # xmax = -87.758445739746 
    # xmin = -87.51537322998

    bbox = box(xmin, ymin, xmax, ymax)

    polygons = extract_blocks(bbox)
    downloaded_centroids = get_building_centroids(
        south=ymin, 
        west=xmin, 
        north=ymax, 
        east=xmax)
    
    blocks = gpd.GeoDataFrame(geometry=polygons)
    centroids = gpd.GeoDataFrame(geometry=downloaded_centroids)
    
    block_aggregation = gpd.sjoin(blocks, centroids, how="right", op="intersects")
    block_aggregation = block_aggregation[pd.notnull(block_aggregation["index_left"])].groupby("index_left")["geometry"].agg(list)
    block_aggregation.name = "centroids"
    block_centroids = blocks.join(block_aggregation)
    block_centroids = block_centroids[pd.notnull(block_centroids["centroids"])]

    block_centroids["weak_duals"] = block_centroids.apply(get_weak_dual_sequence, axis=1)
    block_centroids["complexity"] = block_centroids["weak_duals"].apply(get_complexity)
    
    fig, ax = plt.subplots(1, 1)
    divider = make_axes_locatable(ax)
    block_centroids.plot(column='complexity', ax=ax, legend=True)
    plt.autoscale()
    plt.show()

    # plot_polygons(blocks, facecolors=[])
    # centroid_blocks.plot(markersize=0.01, column="index_left", ax=plt.gca(), zorder=500)
    # plt.show()

    # bc = block_centroids[11:12].copy()
    # bc.apply(get_weak_dual_sequence, axis=1) 
    # sequence = bc.apply(get_weak_dual_sequence, axis=1).iloc[0]

    # plt.figure()
    # bc.plot(ax=plt.gca())
    # for  ((i, g), color) in zip(enumerate(sequence), 'krgby'): 
    #     g.plot(ax=plt.gca(), node_color=color, node_size=5*(i+1), width=0.1, edge_color=color) 
    # plt.autoscale()
    # plt.show()

    # main(xmin, ymin, xmax, ymax)
