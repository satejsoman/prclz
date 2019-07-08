from prclz.topology.planar import Edge, Face, Node, PlanarGraph
import matplotlib.pyplot as plt


n = [Node(xy) for xy in [
    (0, 0),
    (0, 1),
    (0, 2),
    (0, 3),
    (1, 2),
    (1, 3),
    (0, 4),
    (-1, 4),
    (-1, 3),
    (-1, 2),
    (1, 4),
    (-2, 3)
]]

s0 = PlanarGraph()
edge_indices = [(0, 1), (1, 2), (1, 4), (2, 3), (2, 4), (2, 8), (3, 4), (3, 5), (3, 6), (3, 7), (3, 8), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9), (2, 9), (1, 9), (6, 10), (5, 10), (9, 11), (7, 11)]
for (u, v) in edge_indices:
    s0.add_edge(Edge((n[u], n[v])))

plt.figure()

s1 = s0.weak_dual()
s0.plot(ax=plt.gca(), node_color='r', node_size=50)
s1.plot(ax=plt.gca(), node_color='b', node_size=50)
plt.show()
