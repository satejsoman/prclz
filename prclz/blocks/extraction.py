from typing import Callable, Mapping, Union

import networkx
import osmnx as ox
from shapely.geometry import (LineString, MultiLineString, MultiPolygon,
                              Polygon, mapping)
from shapely.ops import polygonize
from .commons import BlockExtractionMethod
from .methods import DEFAULT_EXTRACTION_METHOD


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


def extract_blocks(area: Union[Polygon, MultiPolygon],
                   buffer_radius: float,
                   extract: BlockExtractionMethod = DEFAULT_EXTRACTION_METHOD)\
        -> MultiPolygon:
    pass
