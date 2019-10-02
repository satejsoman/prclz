from i_topology import *
import time 

# (1) Test that our test of determining whether a point is ON the line segment is correct

# y = x 
n0 = (0,0)
n1 = (1,1)
#edge = Edge([n0, n1])

p0 = (0.5,0.5)
p1 = (-0.5, -0.5)
p2 = (1.5,1.5)

assert node_on_edge([n0,n1], p0), "Test 1a FAILURE"
assert not node_on_edge([n0,n1], p1), "Test 1b FAILURE"
assert not node_on_edge([n0,n1], p2), "Test 1c FAILURE"

# Horiz line
n0 = (0,0)
n1 = (1,0)
edge = [n0, n1]

p0 = (0.5, 0)
p1 = (-0.5, 0)
p2 = (1.5, 0)

assert node_on_edge(edge, p0), "Test 2a FAILURE"
assert not node_on_edge(edge, p1), "Test 2b FAILURE"
assert not node_on_edge(edge, p2), "Test 2c FAILURE"

# y = -x
n0 = (0,0)
n1 = (-1,1)
edge = [n0, n1]

p0 = (-0.5,0.5)
p1 = (0.5, -0.5)
p2 = (-1.5,1.5)

assert node_on_edge(edge, p0), "Test 3a FAILURE"
assert not node_on_edge(edge, p1), "Test 3b FAILURE"
assert not node_on_edge(edge, p2), "Test 3c FAILURE"

# Vert line
n0 = (0,0)
n1 = (0,1)
edge = [n0, n1]

p0 = (0,0.5)
p1 = (0, -0.5)
p2 = (0,1.5)

assert node_on_edge(edge, p0), "Test 4a FAILURE"
assert not node_on_edge(edge, p1), "Test 4b FAILURE"
assert not node_on_edge(edge, p2), "Test 4c FAILURE"

 
# (2) Test that our projection of a node onto an edge is correct
n0 = (0,1)
n1 = (1,0)
edge = [n0,n1]

# Test by extending along a projection
#projection_within = [(.25,.25), (0,0.5), (-.5,1.0), (.5,0), (.75, -.25), (1.0, -.5), (1.25, -.75), (-1,0), (-1,1)]
projection_within = [(-.5, .5), (-.25, .25), (0,0), (.25,-.25), (.5,-.5)]
for p in projection_within:
    p_projection = vector_projection(edge, p)
    print("Project {} to {}".format(p, p_projection))
    assert node_on_edge(edge, p_projection), "Failed on p={}".format(p)

# Test by rotating
projection_within2 = [(-.5,.5), (0, .5), (.5, .5), (.5,0), (.5,-.5), (0,-.5), (-.5,-.5), (-.5,0)]
for p in projection_within2:
    p_projection = vector_projection(edge, p)
    print("Project {} to {}".format(p, p_projection))
    assert node_on_edge(edge, p_projection), "Failed on p={}".format(p)

# NEED TO RETURN TO THIS CHECK
# projection_outside = []
# for p in projection_outside:
#     p_projection = edge.vector_projection(Node(p))
#     assert not edge.node_on_edge(p_projection), "Failed on p={}".format(p)

# (3) Test that getting the closest node to edge works
p0 = (0,0)
p1 = (0,1)
edge = [p0, p1]

new_point0 = (-.1, -.1)
closet = PlanarGraph.closest_point_to_node(edge, new_point0)


# (4) Test that inserting a node to it's nearest edge works
p0 = (0,0)
p1 = (1,0)
p2 = (1,1)
p3 = (0,1)

g = PlanarGraph()
g.add_edge(p0,p1)
g.add_edge(p2,p1)
g.add_edge(p2,p3)
g.add_edge(p0,p3)

print("PlanarGraph g before:\n", g)
new_point0 = (-.1, -.1)
g.add_node_to_closest_edge(new_point0)

new_point1 = (0, .75)
g.add_node_to_closest_edge(new_point1)
print("PlanarGraph g after:\n", g)


# (5) Test of Steiner Tree Algorithm
p0 = (0,0)
p1 = (0,2)
g = PlanarGraph()
g.add_edge(p0,p1)
g.plot_reblock("test0.png")

# Now add a building
b0 = (.1, 1)
g.add_node_to_closest_edge(b0, terminal=True)
g.plot_reblock("test1.png")

p0 = (0,0)
p1 = (0,2)
p2 = (2,2)
p3 = (4,2)
p4 = (4,0)

g = PlanarGraph()
g.add_edge(p0,p1)
g.add_edge(p0,p2)
g.add_edge(p0,p4)
g.add_edge(p2,p4)
g.add_edge(p3,p4)
g.add_edge(p1,p2)
g.add_edge(p2,p3)

# Original "parcel"
g.plot_reblock("0_original_parcel.png")


b0 = (2,.3)
b1 = (1,2)
b2 = (1.5, 1)
b3 = (5,1.75)
b4 = (-.1,-.1)
all_blds = [b0, b1, b2, b3, b4]

# Original +buildings in raw locations
orig_g = g.copy()
for bld in all_blds: 
    orig_g.add_node(bld, terminal = True)
orig_g.plot_reblock("1_add_buildings_raw.png")

# Original +buildings in closest locations
for bld in all_blds:
    g.add_node_to_closest_edge(bld, terminal=True)
g.plot_reblock("2_add_buildings_closest.png")

# term = g.vs.select(terminal_eq=True)
# H, steiner_edge_idxs = igraph_steiner_tree(g, term)
# for i in steiner_edge_idxs:
#     g.es[i]['steiner'] = True 
g.steiner_tree_approx()
g.plot_reblock("3_reblocked.png")


# Test saving and reloading
g.save_planar("test.ig")
g_new = PlanarGraph.load_planar("test.ig")
g_new.plot_reblock("restored_graph.png")
 

# Now do steiner tree approx
start = time.time()
for _ in range(1000):
    steiner = g.steiner_tree_approx()
end = time.time()
print("TAKES {} seconds".format(end-start))


