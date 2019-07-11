from typing import Sequence

import geopandas as gpd
import pytess
from shapely.geometry import Polygon

from prclz.topology.planar import PlanarGraph


def get_s0_approximation(block, centroids) -> PlanarGraph:
    """ approximates the initial connectivity graph by partitioning 
    the block into a voronoi decomposition and feeds those faces into
    a planar graph """

    # get the voronoi decomposition of space, given building centroids
    vertices = [vs for (anchor, vs) in pytess.voronoi(centroids + list(block.exterior.coords)) if anchor]
    polygons = list(map(Polygon, vertices))
    return PlanarGraph.from_polygons(polygons)

def get_weak_dual_sequence(
    gdf: gpd.GeoDataFrame, 
    polygon_column: str = "geometry", 
    centroid_column: str = "centroids"
) -> Sequence[PlanarGraph]:
    s_vector = [get_s0_approximation(gdf.iloc[0][polygon_column], [(p.x, p.y) for p in gdf.iloc[0]["centroids"]])]
    while s_vector[-1].number_of_nodes() > 2:
        s_vector.append(s_vector[-1].weak_dual())
    return s_vector
    

# building, boundary = get_test_building(), get_test    _boundary()
# * = get_test_*() 
