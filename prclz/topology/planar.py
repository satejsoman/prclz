from itertools import chain, combinations
from typing import List, Optional, Sequence

import networkx
import numpy as np
from shapely.geometry import LineString, Point, Polygon


class Node(Point):
    def __hash__(self):
        return hash(tuple(map(lambda _:_[0], self.xy)))

class Edge(LineString):
    """ undirected edge, with flags to indicate if the edge in on the interior, a road, or a barrier """
    def __init__(self, nodes: Sequence[Node]):
        # since the edge is undirected, sort input points to speed up edge uniqueness calculations
        nodes = sorted(nodes, key=lambda n: n.x)
        self.nodes = nodes
        self.interior = False
        self.road = False
        self.barrier = False
        super().__init__(coordinates=nodes)

    def __len__(self):
        return self.nodes[0].distance(self.nodes[1])
    
    def __hash__(self):
        pass

class Face(Polygon):
    """ polygon defined by edges """

class Graph(networkx.Graph):
    def __init__(self, name: Optional[str] = "S", degree: int = 0, incoming_graph_data=None, **attr):
        self.name = name 
        self.degree = degree
        super().__init__(incoming_graph_data=incoming_graph_data, **attr)

    def add_edge(self, edge: Edge, weight=None):
        assert isinstance(edge, Edge)
        super().add_edge(edge.nodes[0], edge.nodes[1], spatial_edge=edge, weight=weight if weight else len(edge))

    ## weak dual calculation functions
    def get_embedding(self):
        return {
            node: sorted(
                self[node], # get neighbors from adjacency dictionary  
                key = lambda other, node=node: np.arctan2(other.x - node.x, other.y - node.y))
            for node in self.nodes
        }

    def trace_faces(self):
        """ algorithm for face-tracing taken from SAGE """
        if len(self.nodes) < 2: 
            return []

        embedding = self.get_embedding()

        # ensure we have unique edges by eliminating (b, a) if we've already seen (a, b)
        edgeset = set(chain.from_iterable([(edge[0], edge[1]), (edge[1], edge[0])] for edge in self.edges))

        # trace faces
        faces : List[Face] = []

        face = [edgeset.pop()]
        while edgeset:
            neighbors = embedding[face[-1][-1]]
            next_node = neighbors[(neighbors.index(face[-1][-2])+1) % (len(neighbors))]
            candidate_edge = (face[-1][-1], next_node)
            if candidate_edge == face[0]: # loop complete
                faces.append(face)
                face = [edgeset.pop()]
            else:
                face.append(candidate_edge)
                edgeset.remove(candidate_edge)
        
        # clean up any faces in progress when edgeset exhausted
        if len(face) > 0:
            faces.append(face)

        # remove outer "sphere" face
        facelist = sorted(faces, key=len)
        self.outerface = Face(facelist[-1])
        self.outerface.edges = [self[e[1]][e[0]]["spatial_edge"] for e in facelist[-1]]
        
        inner_facelist = [Face([self[e[1]][e[0]]["spatial_edge"] for e in edgelist]) for edgelist in facelist[:-1]]
        return inner_facelist
    
    def weak_dual(self):
        dual = Graph(name = self.name, degree = self.degree + 1)

        if self.number_of_nodes() < 2: 
            return dual 

        inner_facelist = self.trace_faces()
        
        if len(inner_facelist) == 1:
            dual.add_node(inner_facelist[0].centroid)
        else:
            for c in combinations(inner_facelist, 2):
                c0 = [e for e in c[0].edges if not e.road]
                c1 = [e for e in c[1].edges if not e.road]
                if len(set(c0).intersection(c1)) > 0:
                    dual.add_edge(Edge((c[0].centroid, c[1].centroid)))

        return dual 
