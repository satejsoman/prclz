from itertools import chain, combinations
from typing import List, Sequence

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from shapely.geometry import LineString, Point, Polygon

from prclz.plotting import plot_polygons


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
    
    def __hash__(self):
        return hash(self.nodes[0]) + hash(self.nodes[1])

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

    ## weak dual calculation functions    
    def trace_faces(self):
        cycles = nx.algorithms.cycles.cycle_basis(self)
        return [Face(shell=[(n.x, n.y) for n in cycle], edges=self.edges(cycle)) for cycle in cycles]

    def weak_dual(self):
        dual = PlanarGraph(name = self.name, dual_order = self.graph['dual_order'] + 1)

        if self.number_of_nodes() < 2: 
            return dual 

        inner_facelist = self.trace_faces()
        
        if len(inner_facelist) == 1:
            dual.add_node(inner_facelist[0].centroid)
        else:
            for c in combinations(inner_facelist, 2):
                c0 = [e for e in c[0].edges]
                c1 = [e for e in c[1].edges]
                if len(set(c0).intersection(c1)) > 0:
                    n1 = Node(c[0].centroid.x, c[0].centroid.y)
                    n2 = Node(c[1].centroid.x, c[1].centroid.y)
                    dual.add_edge(Edge((n1, n2)))

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
