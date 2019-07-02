from typing import Union, Mapping, Callable

import networkx
import osmnx as ox
from shapely.geometry import (LineString, MultiLineString, MultiPolygon,
                              Polygon, mapping)
from shapely.ops import polygonize

BlockExtractionMethod = Callable[[Polygon, MultiLineString], MultiPolygon]

def edge_to_geometry(nodes: Mapping, edge: Mapping) -> LineString:
    if "geometry" in edge.keys():
        return edge["geometry"]
    src = nodes[edge["source"]]
    tgt = nodes[edge["target"]]
    return LineString([(src["x"], src["y"]), (tgt["x"], tgt["y"])])

def linestrings_from_network(graph: networkx.Graph) -> MultiLineString:
    json_graph = networkx.readwrite.json_graph.node_link_data(graph)
    nodes = {node["id"]: node for node in json_graph["nodes"]}
    edges = json_graph["links"]
    return MultiLineString([edge_to_geometry(nodes, edge) for edge in edges])

def extract_blocks(
        area: Union[Polygon, MultiPolygon], 
        buffer_radius: float, 
        extract: Union[BlockExtractionMethod, None] = None
    ) -> MultiPolygon:
    if extract is None:
        extract = buffered_linestring_difference()
    

# these could potentially be instances of a BlockExtractionMethod, which in turn would 
# bean AbstractBaseClass, but readability is too low to justify that approach

def buffered_linestring_difference(epsilon: float = 0.000005) -> BlockExtractionMethod:
    # https://gis.stackexchange.com/a/58674
    # suggest epsilon of 0.0001 for generating graphics, and 0.00005 to generate shapefiles
    def extract(region: Polygon, linestrings: MultiLineString) -> MultiPolygon:
        return region.difference(linestrings.buffer(epsilon)) 
    return extract

def intersection_polygonize() -> BlockExtractionMethod:
    def extract(region: Polygon, linestrings: MultiLineString) -> MultiPolygon:
        # add the region boundary as an additional constraint 
        constrained_linestrings = linestrings + [region.exterior] 
        return MultiPolygon(list(polygonize(constrained_linestrings)))
    return extract
