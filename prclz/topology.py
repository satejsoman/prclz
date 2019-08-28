from itertools import chain, combinations, product
from typing import Sequence

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import shapely.geos
from shapely.geometry import Polygon, LineString

""" implementation of planar graph """


class Node:
    """ two-dimensional point container """

    def __init__(self, coordinates, name=None):
        assert len(coordinates) == 2, "input coordinates must be of length 2"
        self.x, self.y = coordinates
        self.coordinates = (self.x, self.y)
        self.road = False
        self.interior = False
        self.barrier = False
        self.name = name

    def __repr__(self):
        return self.name if self.name else "Node(%.2f,%.2f)" % (self.x, self.y)

    def __eq__(self, other):
        return self.coordinates == other.coordinates

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        return self.coordinates < other.coordinates

    def __hash__(self):
        return hash(self.coordinates)

    def distance(self, other):
        return np.linalg.norm((self.x - other.x, self.y - other.y))


class Edge:
    """ undirected edge as a tuple of nodes,
    with flags to indicate if the edge ios interior, road, or barrier """

    def __init__(self, nodes: Sequence[Node]):
        # nodes = sorted(nodes, lambda p: (p.x, p.y))
        self.nodes = nodes
        self.interior = False
        self.road = False
        self.barrier = False

    def length(self):
        return self.nodes[0].distance(self.nodes[1])

    def __str__(self):
        return "Edge(({}, {}), ({}, {}))".format(
            self.nodes[0].x, self.nodes[0].y, self.nodes[1].x, self.nodes[1].y
        )

    def __repr__(self):
        return "Edge(({}, {}), ({}, {}))".format(
            self.nodes[0].x, self.nodes[0].y, self.nodes[1].x, self.nodes[1].y
        )

    def __eq__(self, other):
        return (
            self.nodes[0] == other.nodes[0] and
            self.nodes[1] == other.nodes[1]) or (
            self.nodes[0] == other.nodes[1] and
            self.nodes[1] == other.nodes[0])

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.nodes)


class Face:
    """ polygon defined by edges """

    def __init__(self, edges):
        # determine representation of edges: Edge class or tuple?
        if len(edges) > 0 and type(edges[0]) != tuple:
            node_set = set(chain.from_iterable(edge.nodes for edge in edges))
            self.edges = set(edges)
            self.ordered_edges = edges
        else:
            node_set = set(chain.from_iterable(edges))
            planar_edges = list(map(Edge, edges))
            self.edges = set(planar_edges)
            self.ordered_edges = planar_edges
        self.nodes = list(sorted(node_set))
        self.name = ".".join(map(str, self.nodes))

    def area(self):
        return 0.5*abs(sum(e.nodes[0].x*e.nodes[1].y -
                       e.nodes[1].x*e.nodes[0].y for e in self.ordered_edges))

    def centroid(self):
        """finds the centroid of a MyFace, based on the shoelace method
        e.g. http://en.wikipedia.org/wiki/Shoelace_formula and
        http://en.wikipedia.org/wiki/Centroid#Centroid_of_polygon
        The method relies on properly ordered edges. """

        a = 0.5*(sum(e.nodes[0].x*e.nodes[1].y - e.nodes[1].x*e.nodes[0].y
                 for e in self.ordered_edges))
        if abs(a) < 0.01:
            cx = np.mean([n.x for n in self.nodes])
            cy = np.mean([n.y for n in self.nodes])
        else:
            cx = (1/(6*a))*sum([(e.nodes[0].x + e.nodes[1].x) *
                               (e.nodes[0].x*e.nodes[1].y -
                               e.nodes[1].x*e.nodes[0].y)
                               for e in self.ordered_edges])
            cy = (1/(6*a))*sum([(e.nodes[0].y + e.nodes[1].y) *
                               (e.nodes[0].x*e.nodes[1].y -
                               e.nodes[1].x*e.nodes[0].y)
                               for e in self.ordered_edges])

        return Node((cx, cy))

    def __len__(self):
        return len(self.edges)


class PlanarGraph(nx.Graph):
    def __init__(
        self, name: str = "S", dual_order: int = 0, incoming_graph_data=None, **attr
    ):
        attr["name"] = name
        attr["dual_order"] = dual_order
        super().__init__(incoming_graph_data=incoming_graph_data, **attr)

    @staticmethod
    def from_edges(edges, name="S"):
        graph = PlanarGraph(name=name)
        for edge in edges:
            graph.add_edge(edge)
        return graph

    @staticmethod
    def from_polygons(polygons: Sequence[Polygon], name="S"):
        nodes = dict()
        faces = []
        for polygon in polygons:
            polygon_nodes = []
            for node in map(Node, polygon.exterior.coords):
                if node not in nodes:
                    polygon_nodes.append(node)
                    nodes[node] = node
                else:
                    polygon_nodes.append(nodes[node])
                edges = [tuple(polygon_nodes[i:i+2]) for i in range(len(polygon_nodes)-1)]
                faces.append(Face(edges))

        graph = PlanarGraph(name=name)

        for edge in chain.from_iterable(face.edges for face in faces):
            graph.add_edge(Edge(edge.nodes))

        return graph

    def __repr__(self):
        return "{}{} with {} nodes".format(
            self.name, self.graph["dual_order"], self.number_of_nodes()
        )

    def __str__(self):
        return self.__repr__()

    def add_edge(self, edge: Edge, weight=None):
        assert isinstance(edge, Edge)
        super().add_edge(
            edge.nodes[0],
            edge.nodes[1],
            planar_edge=edge,
            weight=weight if weight else edge.length(),
        )

    def get_embedding(self):
        return {
            node: sorted(
                self.neighbors(node),
                key=lambda neighbor, node=node: np.arctan2(
                    neighbor.x - node.x,
                    neighbor.y - node.y)
            ) for node in self.nodes()
        }

    def trace_faces(self):
        """Algorithm from SAGE"""
        if len(self.nodes()) < 2:
            return []

        embedding = self.get_embedding()
        edgeset = set(chain.from_iterable([
            [(edge[0], edge[1]), (edge[1], edge[0])]
            for edge in self.edges()
        ]))

        # begin face tracing
        faces = []
        face = [edgeset.pop()]
        while edgeset:
            neighbors = embedding[face[-1][-1]]
            next_node = neighbors[(neighbors.index(face[-1][-2])+1) %
                                  (len(neighbors))]
            candidate_edge = (face[-1][-1], next_node)
            if candidate_edge == face[0]:
                faces.append(face)
                face = [edgeset.pop()]
            else:
                face.append(candidate_edge)
                edgeset.remove(candidate_edge)
        # append any faces under construction when edgeset exhausted
        if len(face) > 0:
            faces.append(face)

        # remove the outer "sphere" face
        facelist = sorted(faces, key=len)
        self.outerface = Face(facelist[-1])
        self.outerface.edges = [self[e[1]][e[0]]["planar_edge"]
                                for e in facelist[-1]]
        inner_facelist = []
        for face in facelist[:-1]:
            iface = Face(face)
            iface.edges = [self[e[1]][e[0]]["planar_edge"] for e in face]
            inner_facelist.append(iface)

        return inner_facelist

    def weak_dual(self):
        dual = PlanarGraph(
            name=self.name,
            dual_order=self.graph["dual_order"] + 1)

        if self.number_of_nodes() < 2:
            return dual

        inner_facelist = self.trace_faces()

        if len(inner_facelist) == 1:
            dual.add_node(inner_facelist[0].centroid())
        else:
            for (face1, face2) in combinations(inner_facelist, 2):
                edges1 = [e for e in face1.edges if not e.road]
                edges2 = [e for e in face2.edges if not e.road]

                linestrings1 = [LineString([(e.nodes[0].x, e.nodes[0].y), (e.nodes[1].x, e.nodes[1].y)]) for e in edges1]
                linestrings2 = [LineString([(e.nodes[0].x, e.nodes[0].y), (e.nodes[1].x, e.nodes[1].y)]) for e in edges2]

                if len(set(edges1).intersection(edges2)) > 0 or any((e1.intersects(e2) and e1.touches(e2) and e1.intersection(e2).type != "Point") for (e1, e2) in product(linestrings1, linestrings2)):
                    dual.add_edge(Edge((face1.centroid(), face2.centroid())))

        return dual

    def plot(self, **kwargs):
        plt.axes().set_aspect(aspect=1)
        plt.axis("off")
        edge_kwargs = kwargs.copy()
        nlocs = {node: (node.x, node.y) for node in self.nodes}
        edge_kwargs["label"] = "_nolegend"
        edge_kwargs["pos"] = nlocs
        nx.draw_networkx_edges(self, **edge_kwargs)
        node_kwargs = kwargs.copy()
        node_kwargs["label"] = self.name
        node_kwargs["pos"] = nlocs
        nodes = nx.draw_networkx_nodes(self, **node_kwargs)
        if nodes:
            nodes.set_edgecolor("None")
