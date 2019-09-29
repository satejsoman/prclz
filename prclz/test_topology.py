from topology import *
import time 

# (1) Test that our test of determining whether a point is ON the line segment is correct

# y = x 
n0 = Node((0,0))
n1 = Node((1,1))
edge = Edge([n0, n1])

p0 = Node((0.5,0.5))
p1 = Node((-0.5, -0.5))
p2 = Node((1.5,1.5))

assert edge.node_on_edge(p0), "Test 1a FAILURE"
assert not edge.node_on_edge(p1), "Test 1b FAILURE"
assert not edge.node_on_edge(p2), "Test 1c FAILURE"

# Horiz line
n0 = Node((0,0))
n1 = Node((1,0))
edge = Edge([n0, n1])

p0 = Node((0.5, 0))
p1 = Node((-0.5, 0))
p2 = Node((1.5, 0))

assert edge.node_on_edge(p0), "Test 2a FAILURE"
assert not edge.node_on_edge(p1), "Test 2b FAILURE"
assert not edge.node_on_edge(p2), "Test 2c FAILURE"

# y = -x
n0 = Node((0,0))
n1 = Node((-1,1))
edge = Edge([n0, n1])

p0 = Node((-0.5,0.5))
p1 = Node((0.5, -0.5))
p2 = Node((-1.5,1.5))

assert edge.node_on_edge(p0), "Test 3a FAILURE"
assert not edge.node_on_edge(p1), "Test 3b FAILURE"
assert not edge.node_on_edge(p2), "Test 3c FAILURE"

# Vert line
n0 = Node((0,0))
n1 = Node((0,1))
edge = Edge([n0, n1])

p0 = Node((0,0.5))
p1 = Node((0, -0.5))
p2 = Node((0,1.5))

assert edge.node_on_edge(p0), "Test 4a FAILURE"
assert not edge.node_on_edge(p1), "Test 4b FAILURE"
assert not edge.node_on_edge(p2), "Test 4c FAILURE"

# (2) Test that our projection of a node onto an edge is correct
n0 = Node((0,1))
n1 = Node((1,0))
edge = Edge([n0,n1])

# Test by extending along a projection
#projection_within = [(.25,.25), (0,0.5), (-.5,1.0), (.5,0), (.75, -.25), (1.0, -.5), (1.25, -.75), (-1,0), (-1,1)]
projection_within = [(-.5, .5), (-.25, .25), (0,0), (.25,-.25), (.5,-.5)]
for p in projection_within:
    p_projection = edge.vector_projection(Node(p))
    print("Project {} to {}".format(Node(p), p_projection))
    assert edge.node_on_edge(p_projection), "Failed on p={}".format(p)

# Test by rotating
projection_within2 = [(-.5,.5), (0, .5), (.5, .5), (.5,0), (.5,-.5), (0,-.5), (-.5,-.5), (-.5,0)]
for p in projection_within2:
    p_projection = edge.vector_projection(Node(p))
    print("Project {} to {}".format(Node(p), p_projection))
    assert edge.node_on_edge(p_projection), "Failed on p={}".format(p)

# NEED TO RETURN TO THIS CHECK
# projection_outside = []
# for p in projection_outside:
#     p_projection = edge.vector_projection(Node(p))
#     assert not edge.node_on_edge(p_projection), "Failed on p={}".format(p)

# (3) Test that getting the closest node to edge works
p0 = Node((0,0))
p1 = Node((0,1))
edge = Edge([p0, p1])

new_point0 = Node((-.1, -.1))
closet = edge.closest_point_to_node(new_point0)


# (4) Test that inserting a node to it's nearest edge works
p0 = Node((0,0))
p1 = Node((1,0))
p2 = Node((1,1))
p3 = Node((0,1))

g = PlanarGraph()
g.add_edge(Edge([p0,p1]))
g.add_edge(Edge([p2,p1]))
g.add_edge(Edge([p2,p3]))
g.add_edge(Edge([p0,p3]))

new_point0 = Node((-.1, -.1))
g.add_node_to_closest_edge(new_point0)

new_point1 = Node((0, .75))
g.add_node_to_closest_edge(new_point1)


# (5) Test of Steiner Tree Algorithm
p0 = Node((0,0))
p1 = Node((0,2))
p2 = Node((2,2))
p3 = Node((4,2))
p4 = Node((4,0))


g = PlanarGraph()
g.add_edge(Edge([p0,p1]))
g.add_edge(Edge([p0,p2]))
g.add_edge(Edge([p0,p4]))
g.add_edge(Edge([p2,p4]))
g.add_edge(Edge([p3,p4]))
g.add_edge(Edge([p1,p2]))
g.add_edge(Edge([p2,p3]))

# Original "parcel"
g.plot()
#plt.show()


b0 = Node((2,.3))
b1 = Node((1,2))
b2 = Node((1.5, 1))
b3 = Node((5,1))
b4 = Node((-.1,-.1))
all_blds = [b0, b1, b2, b3, b4]

# Original +buildings in raw locations
orig_g = g.copy()
for bld in all_blds:
    bld.terminal = True 
    orig_g.add_node(bld)
orig_g.plot_reblock()
#plt.show()

# Original +buildings in closest locations
for bld in all_blds:
    bld.terminal = True 
    g.add_node_to_closest_edge(bld)
g.plot_reblock()
#plt.show()

# Now do steiner tree approx
start = time.time()
for _ in range(1000):
    steiner = g.steiner_tree_approx(verbose=True)
end = time.time()
print("TAKES {} seconds".format(end-start))

# g.plot_reblock()
# plt.show()

