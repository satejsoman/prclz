from typing import Sequence, Tuple, Union

import geopandas as gpd
import pytess
from shapely.geometry import MultiPolygon, Point, Polygon

from .topology import PlanarGraph


def get_s0_approximation(block: Polygon, centroids: Sequence[Tuple[float, float]]) -> PlanarGraph:
    """ approximates the initial connectivity graph by partitioning 
    the block into a voronoi decomposition and feeds those faces into
    a planar graph """

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
    return PlanarGraph.from_polygons([polygon for polygon in simplified_polygons if polygon])

def get_weak_dual_sequence_for_dataframe(
    gdf: gpd.GeoDataFrame, 
    polygon_column: str = "geometry", 
    centroid_column: str = "centroids"
) -> Sequence[PlanarGraph]:
    s_vector = [get_s0_approximation(gdf[polygon_column], [(p.x, p.y) for p in gdf[centroid_column]])]
    while s_vector[-1].number_of_nodes() > 2:
        s_vector.append(s_vector[-1].weak_dual())
    return s_vector

def get_weak_dual_sequence(block: Polygon, centroids: Sequence[Point]) -> Sequence[PlanarGraph]:
    s_vector = [get_s0_approximation(block, [(c.x, c.y) for c in centroids])]
    while s_vector[-1].number_of_nodes() > 0:
        s_vector.append(s_vector[-1].weak_dual())
    s_vector.pop() # last graph has no nodes
    return s_vector

def get_complexity(sequence: Sequence[PlanarGraph]) -> int:
    return len(sequence) - 1 if sequence else 0
