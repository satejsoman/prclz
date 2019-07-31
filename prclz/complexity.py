from typing import Sequence

import geopandas as gpd
import pytess
from shapely.geometry import Polygon

from .topology import PlanarGraph


def get_s0_approximation(block, centroids) -> PlanarGraph:
    """ approximates the initial connectivity graph by partitioning 
    the block into a voronoi decomposition and feeds those faces into
    a planar graph """
    
    # short circuit degenerate graphs
    if len(centroids) < 3:
        return PlanarGraph()

    # get the voronoi decomposition of space, given building centroids
    boundary_points = list(block.exterior.coords)
    boundary_set = set(boundary_points)
    vertices = [vs for (anchor, vs) in pytess.voronoi(centroids + boundary_points) if (anchor and anchor not in boundary_set)]
    return PlanarGraph.from_polygons([Polygon(vs) for vs in vertices if len(vs) > 2])

def get_weak_dual_sequence_for_dataframe(
    gdf: gpd.GeoDataFrame, 
    polygon_column: str = "geometry", 
    centroid_column: str = "centroids"
) -> Sequence[PlanarGraph]:
    s_vector = [get_s0_approximation(gdf[polygon_column], [(p.x, p.y) for p in gdf[centroid_column]])]
    while s_vector[-1].number_of_nodes() > 2:
        s_vector.append(s_vector[-1].weak_dual())
    return s_vector

def get_weak_dual_sequence(block, centroids) -> Sequence[PlanarGraph]:
    s_vector = [get_s0_approximation(block, [(c.x, c.y) for c in centroids])]
    while s_vector[-1].number_of_nodes() > 2:
        s_vector.append(s_vector[-1].weak_dual())
    return s_vector

def get_complexity(sequence: Sequence[PlanarGraph]) -> int:
    if not sequence:
        return 0
    return len(sequence) if sequence[-1].number_of_nodes() > 0 else len(sequence) - 1
