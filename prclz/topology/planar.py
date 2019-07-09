from itertools import chain, combinations
from typing import List, Sequence
from functools import reduce
from collections import defaultdict

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from shapely.geometry import LineString, Point, Polygon
import shapely.geos

from prclz.plotting import plot_polygons

""" implementation of planar graph embedding using GDAL (via shapely) to determine face/vertex adjancency """

class Node(Point):
    """ two-dimensional point container """
    def __hash__(self):
        return hash(tuple(map(lambda _:_[0], self.xy)))

    def __repr__(self):
        return "Node({}, {})".format(self.x, self.y)

    def  __str__(self):
        return self.__repr__()

class Edge(LineString):
    """ undirected edge, with flags to indicate if the edge in on the interior, a road, or a barrier """
    def __init__(self, nodes: Sequence[Node]):
        # nodes = sorted(nodes, lambda p: (p.x, p.y))
        self.nodes = nodes
        self.interior = False
        self.road = False
        self.barrier = False
        super().__init__(coordinates=nodes)

    def length(self):
        return self.nodes[0].distance(self.nodes[1])

    def __str__(self):
        return "Edge(({}, {})-({}, {}))".format(self.nodes[0].x, self.nodes[0].y, self.nodes[1].x, self.nodes[1].y)

    def __repr__(self):
        return "Edge(({}, {})-({}, {}))".format(self.nodes[0].x, self.nodes[0].y, self.nodes[1].x, self.nodes[1].y)
    
    def __hash__(self):
        return sum(map(hash, self.nodes[:2]))

class Face(Polygon):
    """ polygon defined by edges """

    def __init__(self, shell=None, holes=None, edges=None):
        self.edges = edges
        super().__init__(shell=shell, holes=holes)

class PlanarGraph(nx.Graph):
    def __init__(self, name: str = "S", dual_order: int = 0, incoming_graph_data=None, **attr):
        attr["name"] = name
        attr["dual_order"] = dual_order
        super().__init__(incoming_graph_data=incoming_graph_data, **attr)

    def  __repr__(self):
        return "{}{}".format(self.name, self.graph["dual_order"])

    def  __str__(self):
        return self.__repr__()

    def add_edge(self, edge: Edge, weight=None):
        assert isinstance(edge, Edge)
        super().add_edge(edge.nodes[0], edge.nodes[1], planar_edge=edge, weight=weight if weight else edge.length()) 

    def trace_faces(self):
        cycles = nx.algorithms.cycles.minimum_cycle_basis(self)
        faces = [
            Face(
                shell = [(n.x, n.y) for n in sorted(cycle, key=lambda node, first=cycle[0]: np.arctan2(node.x - first.x, node.y - first.y))], 
                edges = [Edge((cycle[i], cycle[(i + 1) % len(cycle)])) for i in range(len(cycle))])
            for cycle in cycles
        ]
        return [face.convex_hull if not face.is_valid else face for face in faces]

    def weak_dual(self):
        dual = PlanarGraph(name = self.name, dual_order = self.graph['dual_order'] + 1)

        if self.number_of_nodes() < 2: 
            return dual 
        
        inner_facelist = self.trace_faces()
        
        if len(inner_facelist) == 1:
            dual.add_node(inner_facelist[0].centroid)
        else: 
            for (face1, face2) in combinations(inner_facelist, 2):
                try: 
                    intersection = face1.intersection(face2)
                except shapely.geos.TopologicalError:
                    intersection = face1.convex_hull.intersection(face2.convex_hull)
                if intersection.geom_type == "LineString":
                    dual.add_edge(Edge((Node(face1.centroid.x, face1.centroid.y), Node(face2.centroid.x, face2.centroid.y))))

        return dual 

    def plot(self, **kwargs):
        plt.axes().set_aspect(aspect=1)
        plt.axis('off')
        edge_kwargs = kwargs.copy()
        nlocs = {node: (node.x, node.y) for node in self.nodes}
        edge_kwargs['label'] = "_nolegend"
        edge_kwargs['pos'] = nlocs
        nx.draw_networkx_edges(self, **edge_kwargs)
        node_kwargs = kwargs.copy()
        node_kwargs['label'] = self.name
        node_kwargs['pos'] = nlocs
        nodes = nx.draw_networkx_nodes(self, **node_kwargs)
        nodes.set_edgecolor('None')