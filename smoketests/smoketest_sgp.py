import argparse
import json
import logging
from itertools import cycle
from logging import info
from pathlib import Path
from typing import Optional

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import shapely.wkt
from joblib import Parallel, delayed
from networkx.readwrite import json_graph
from shapely.geometry import *

from prclz.complexity import *
from prclz.plotting import *


def read_file(path, **kwargs):
    """ ensures geometry set correctly when reading from csv
    otherwise, pd.BlockManager malformed when using gpd.read_file(*) """
    if not path.endswith(".csv"):
        return gpd.read_file(path)
    raw = pd.read_csv(path, **kwargs)
    raw["geometry"] = raw["geometry"].apply(shapely.wkt.loads)
    return gpd.GeoDataFrame(raw, geometry="geometry")


def filter_nodes_by_geometry(graph: PlanarGraph, block: Polygon):
    exterior_nodes = [node for node in graph.nodes if not block.contains(Point((node.x, node.y)))]
    graph.remove_nodes_from(exterior_nodes)
    return graph

sgp = read_file('scratch/SGP.1_1_blocks.csv')
all_buildings = gpd.read_file('scratch/msb_all_buildings_xpl.geojson')


pt0 = Point((103.82731318473816, 1.300566552144707))
pt1 = Point((103.7952983379364, 1.2829542804966265))
pt2 = Point((103.81898760795593, 1.2577530759913325))
pt3 = Point((103.84716153144836, 1.3130302171075672))
pt4 = Point((103.81192803382874, 1.3321975390815042)) #pan island expwy
pt = pt3

block_df = sgp[sgp.contains(pt)]
block = block_df.iloc[0].geometry

buildings = all_buildings[all_buildings.within(block)]

centroids = [(c.x, c.y) for c in buildings.centroid]

boundary_points = list(block.exterior.coords)
boundary_set = set(boundary_points)

# get internal parcels from the voronoi decomposition of space, given building centroids
intersected_polygons = [
    (Point(anchor), Polygon(vs).buffer(0).intersection(block)) 
    for (anchor, vs) in pytess.voronoi(centroids) 
    if (anchor and anchor not in boundary_set and len(vs) > 2)]

# simplify geometry when multiple areas intersect original block
simplified_polygons = [
    polygon if polygon.type == "Polygon" else next((segment for segment in polygon if segment.contains(anchor)), None)
    for (anchor, polygon) in intersected_polygons]

s0 = PlanarGraph.from_polygons([polygon for polygon in simplified_polygons if polygon])
s1 = s0.weak_dual()
s2 = s1.weak_dual()


# ax = plt.gca()
# buildings.plot(ax=plt.gca())
# plot_polygons([block], zorder=-10, facecolors=cycle(["black"]))
# plot_polygons(simplified_polygons, zorder=-5, facecolors=cycle(["black"]), alpha=0.2)# buildings.plot(ax=plt.gca())
# s0.plot(node_size=9, ax=ax, node_color="red")
# s1.plot(node_size=7, ax=ax, node_color="green",   edge_color="grey")
# s2.plot(node_size=5, ax=ax, node_color="red", edge_color="#dedede")
# plt.show()


def vis(pt):
    print("Zooming to selected block.")
    block_df = sgp[sgp.contains(pt)]
    block = block_df.iloc[0].geometry

    print("Getting building footprints.")
    buildings = all_buildings[all_buildings.within(block)]

    centroids = [(c.x, c.y) for c in buildings.centroid]

    boundary_points = list(block.exterior.coords)
    boundary_set = set(boundary_points)

    
    print("Generating parcels.")
    # get internal parcels from the voronoi decomposition of space, given building centroids
    intersected_polygons = [
        (Point(anchor), Polygon(vs).buffer(0).intersection(block)) 
        for (anchor, vs) in pytess.voronoi(centroids) 
        if (anchor and anchor not in boundary_set and len(vs) > 2)]

    print("Re-intersecting Voronoi decomposition.")
    # simplify geometry when multiple areas intersect original block
    simplified_polygons = [
        polygon if polygon.type == "Polygon" else next((segment for segment in polygon if segment.contains(anchor)), None)
        for (anchor, polygon) in intersected_polygons]

    print("Generating S₀.")
    s0 = PlanarGraph.from_polygons([polygon for polygon in simplified_polygons if polygon])
    print("Calculating weak dual sequence.")
    s1 = s0.weak_dual()
    s2 = s1.weak_dual()
    s3 = s2.weak_dual()
    s4 = s3.weak_dual()


    ax = plt.gca()
    buildings.plot(ax=plt.gca(), color="#dedede", edgecolor="white")
    plot_polygons([block], zorder=-10, facecolors=cycle(["black"]), alpha=0.3)
    plot_polygons(simplified_polygons, zorder=-5, facecolors=cycle(["black"]), alpha=0.1)# buildings.plot(ax=plt.gca())
    # s0.plot(node_size=9, ax=ax, node_color="red")
    s1.plot(node_size=7, width=2, ax=ax, node_color="purple", edge_color="purple")
    s2.plot(node_size=5, width=2, ax=ax, node_color="red",    edge_color="red")
    s3.plot(node_size=3, width=1, ax=ax, node_color="orange", edge_color="orange")
    s4.plot(node_size=1, width=1, ax=ax, node_color="yellow", edge_color="yellow")
    plt.subplots_adjust(left=0, bottom=0, right=1, top=1)
    plt.show()