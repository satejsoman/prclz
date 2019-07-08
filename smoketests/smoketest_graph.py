from prclz.topology.planar import Edge, Face, Node, PlanarGraph
import matplotlib.pyplot as plt


n = [
    Node((0, 0)),
    Node((0, 1)),
    Node((0, 2)),
    Node((0, 3)),
    Node((1, 2)),
    Node((1, 3)),
    Node((0, 4)),
    Node((-1, 4)),
    Node((-1, 3)),
    Node((-1, 2)),
    Node((1, 4)),
    Node((-2, 3))
]

s0 = PlanarGraph()
s0.add_edge(Edge((n[0], n[1])))
s0.add_edge(Edge((n[1], n[2])))
s0.add_edge(Edge((n[1], n[4])))
s0.add_edge(Edge((n[2], n[3])))
s0.add_edge(Edge((n[2], n[4])))
s0.add_edge(Edge((n[2], n[8])))
s0.add_edge(Edge((n[3], n[4])))
s0.add_edge(Edge((n[3], n[5])))
s0.add_edge(Edge((n[3], n[6])))
s0.add_edge(Edge((n[3], n[7])))
s0.add_edge(Edge((n[3], n[8])))
s0.add_edge(Edge((n[4], n[5])))
s0.add_edge(Edge((n[5], n[6])))
s0.add_edge(Edge((n[6], n[7])))
s0.add_edge(Edge((n[7], n[8])))
s0.add_edge(Edge((n[8], n[9])))
s0.add_edge(Edge((n[2], n[9])))
s0.add_edge(Edge((n[1], n[9])))
s0.add_edge(Edge((n[6], n[10])))
s0.add_edge(Edge((n[5], n[10])))
s0.add_edge(Edge((n[9], n[11])))
s0.add_edge(Edge((n[7], n[11])))

plt.figure()

s1 = s0.weak_dual()
s0.plot(ax=plt.gca(), node_color='r', node_size=50)
s1.plot(ax=plt.gca(), node_color='b', node_size=50)
plt.show()
