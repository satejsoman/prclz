from itertools import combinations, chain, permutations
from functools import reduce 

from networkx.utils import pairwise, not_implemented_for
import networkx as nx
from tqdm import tqdm 

__all__ = ['metric_closure', 'steiner_tree']

# NOTE: this is just source code from networkx, we've copied it here so add progress updates
# SOURCE: https://networkx.github.io/documentation/stable/_modules/networkx/algorithms/approximation/steinertree.html

@not_implemented_for('directed')
def metric_closure(G, weight='weight', verbose=False):
    """  Return the metric closure of a graph.

    The metric closure of a graph *G* is the complete graph in which each edge
    is weighted by the shortest path distance between the nodes in *G* .

    Parameters
    ----------
    G : NetworkX graph

    Returns
    -------
    NetworkX graph
        Metric closure of the graph `G`.

    """
    #print("in metric_closure in steiner_tree.py")
    M = nx.Graph()

    Gnodes = set(G)

    # check for connected graph while processing first node
    #print("begin dijkistra in metric_closure")
    all_paths_iter = nx.all_pairs_dijkstra(G, weight=weight)
    u, (distance, path) = next(all_paths_iter)
    if Gnodes - set(distance):
        msg = "G is not a connected graph. metric_closure is not defined."
        raise nx.NetworkXError(msg)
    Gnodes.remove(u)

    if verbose:
        #print("\nmetric_closure for-loop #1\n")
        for v in tqdm(Gnodes):
            M.add_edge(u, v, distance=distance[v], path=path[v])        
    else:
        for v in Gnodes:
            M.add_edge(u, v, distance=distance[v], path=path[v])

    # first node done -- now process the rest
    if verbose:
        print("\nmetric_closure for-loop #2\n")
        # NOTE: this loop takes FOREVER!
        for u, (distance, path) in tqdm(all_paths_iter):
            Gnodes.remove(u)
            for v in Gnodes:
                M.add_edge(u, v, distance=distance[v], path=path[v])

    else:
        for u, (distance, path) in all_paths_iter:
            Gnodes.remove(u)
            for v in Gnodes:
                M.add_edge(u, v, distance=distance[v], path=path[v])

    return M

def coopers_steiner_tree(G, terminal_nodes, weight='weight', verbose=False):
    '''
    Just do pairwise dijkstra distances for the terminal nodes
    we care about
    Parameters
    ----------
    G : NetworkX graph

    terminal_nodes : list
         A list of terminal nodes for which minimum steiner tree is
         to be found.

    '''
    H = nx.Graph()
    for u,v in tqdm(combinations(terminal_nodes, 2)):

        distance = nx.dijkstra_path_length(G, u, v, weight=weight)
        path = nx.dijkstra_path(G, u, v, weight=weight)
        H.add_edge(u, v, distance=distance, path=path)

    mst_edges = nx.minimum_spanning_edges(H, weight='distance', data=True)

    # Create an iterator over each edge in each shortest path; repeats are okay
    #if verbose: print("Begin iterator thing")
    edges = chain.from_iterable(pairwise(d['path']) for u, v, d in mst_edges)
    T = G.edge_subgraph(edges)
    return T

def igraph_steiner_tree(G, terminal_vertices, weight='weight'):
    '''
    terminal_nodes is List of igraph.Vertex
    '''

    # Build closed graph of terminal_vertices where each weight is the shortest path distance
    H = PlanarGraph()
    for u,v in combinations(terminal_vertices, 2):
        path_idxs = G.get_shortest_paths(u, v, weights='weight', output='epath')
        path_edges = G.es[path_idxs[0]]
        path_distance = reduce(lambda x,y : x+y, map(lambda x: x['weight'], path_edges))
        kwargs = {'weight':path_distance, 'path':path_idxs[0]}
        H.add_edge(u['name'], v['name'], **kwargs)

    # Now get the MST of that complete graph of only terminal_vertices
    mst_edge_idxs = H.spanning_tree(weights='weight', return_tree=False)

    # Now, we join the paths for all the mst_edge_idxs
    steiner_edge_idxs = list(chain.from_iterable(H.es[i]['path'] for i in mst_edge_idxs))

    return H, steiner_edge_idxs
    #steiner_subgraph = G.subgraph_edges(steiner_edge_idxs, delete_vertices=True)

@not_implemented_for('multigraph')
@not_implemented_for('directed')
def steiner_tree(G, terminal_nodes, weight='weight', verbose=False):
    """ Return an approximation to the minimum Steiner tree of a graph.

    Parameters
    ----------
    G : NetworkX graph

    terminal_nodes : list
         A list of terminal nodes for which minimum steiner tree is
         to be found.

    Returns
    -------
    NetworkX graph
        Approximation to the minimum steiner tree of `G` induced by
        `terminal_nodes` .

    Notes
    -----
    Steiner tree can be approximated by computing the minimum spanning
    tree of the subgraph of the metric closure of the graph induced by the
    terminal nodes, where the metric closure of *G* is the complete graph in
    which each edge is weighted by the shortest path distance between the
    nodes in *G* .
    This algorithm produces a tree whose weight is within a (2 - (2 / t))
    factor of the weight of the optimal Steiner tree where *t* is number of
    terminal nodes.

    """
    # M is the subgraph of the metric closure induced by the terminal nodes of
    # G.

    #print("In steiner_tree within steiner_tree.py")
    M = metric_closure(G, weight=weight, verbose=verbose)
    # Use the 'distance' attribute of each edge provided by the metric closure
    # graph.
    H = M.subgraph(terminal_nodes)

    if verbose: print("Begin min span edges")
    mst_edges = nx.minimum_spanning_edges(H, weight='distance', data=True)

    # Create an iterator over each edge in each shortest path; repeats are okay
    if verbose: print("Begin iterator thing")
    edges = chain.from_iterable(pairwise(d['path']) for u, v, d in mst_edges)
    T = G.edge_subgraph(edges)
    return T
