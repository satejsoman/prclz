from itertools import product

import matplotlib.pyplot as plt

from prclz.plotting import plot_polygons, greens
from prclz.topology import Edge, Face, Node, PlanarGraph


def plot_double_dual(s0):
    s1 = s0.indexed_weak_dual()
    s2 = s1.indexed_weak_dual()
    
    plt.figure()
    s0.plot(ax=plt.gca(), node_color='r', node_size=50, width=0.3, edge_color='r')
    s1.plot(ax=plt.gca(), node_color='b', node_size=40, width=0.2, edge_color='b')
    s2.plot(ax=plt.gca(), node_color='g', node_size=30, width=0.1, edge_color='g')
    plt.show()

# legacy topology test
s0 = PlanarGraph()
n = [Node(xy) for xy in [(0, 0), (0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (0, 4), (-1, 4), (-1, 3), (-1, 2), (1, 4), (-2, 3)]]
edge_indices = [(0, 1), (1, 2), (1, 4), (2, 3), (2, 4), (2, 8), (3, 4), (3, 5), (3, 6), (3, 7), (3, 8), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9), (2, 9), (1, 9), (6, 10), (5, 10), (9, 11), (7, 11)]
for (u, v) in edge_indices:
    s0.add_edge(Edge((n[u], n[v])))

plot_double_dual(s0)

# test lattice
t0 = PlanarGraph()
size = 10
nodes = set(map(Node, product(range(size), range(size))))

for node in nodes:
    up = Node((node.x, node.y + 1))
    rt = Node((node.x + 1, node.y))
    if up in nodes:
        t0.add_edge(Edge((node, up)))
    if rt in nodes:
        t0.add_edge(Edge((node, rt)))

plot_double_dual(t0)