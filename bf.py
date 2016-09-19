from __future__ import print_function
import random
from collections import OrderedDict as OD
from heapq import *

from Graph import *
from TimeUtils import *
from utils import *

@timer
def bellman_ford(g, start):
    """
    Finds the closest distances from u->(v in V) in graph g
    Returns either a cost for one path, or all costs and
    a dict from which paths (u->v) can be found.
    """
    costs = {v: float('inf') for v in g.vertices }
    prevs = {v: (0, None) for v in g.vertices }
    costs[start] = 0
    for i in range(1, len(g.vertices)):
        # iterate to find best paths through all vertices
        # worst case for path of length v-1
        for ((u, v), w) in g.edgelist:
            next_cost = costs[u] + w
            if next_cost < costs[v]:
                costs[v] = next_cost
                prevs[v] = (w, u)
    # Check for any negative-weight cycles
    for ((u, v), w) in g.edgelist:
        if costs[u] + w < costs[v]:
           raise Exception("Graph contains a negative-weight cycle")
    return (costs, prevs)

@timer
def k_bellman_ford(g, start, k=0):
    """
    Finds the closest distances from u->(v in V) in graph g
    Returns either a cost for one path, or all costs and
    a dict from which paths (u->v) can be found.
    """
    k = len(g.vertices)-1 if k<1 else k
    costs = {0: { v: float('inf') for v in g.vertices }}
    prevs = {v: (0, None) for v in g.vertices }
    costs[0][start] = 0
    for i in range(1, k+1):
        # iterate to find best paths through all vertices
        # worst case for path of length k
        costs[i] = {k:v for (k,v) in costs[i-1].iteritems()}
        for ((u, v), w) in g.edgelist:
            next_cost = costs[i-1][u] + w
            if next_cost < costs[i][v]:
                costs[i][v] = next_cost
                prevs[v] = (w, u)
    # Check for any negative-weight cycles
    for ((u, v), w) in g.edgelist:
        if costs[k][u] + w < costs[k][v]:
           raise Exception("Graph contains a negative-weight cycle")
    return (costs, prevs)

@testcase
@timer
def test():
    g = TimeableGraph([Vertex(i) for i in range(10)])
    g.add_edge(0, 8, 8)
    g.add_edge(0, 3, 3)
    g.add_edge(1, 4, 6)
    g.add_edge(1, 7, 1)
    g.add_edge(1, 9, 5)
    g.add_edge(2, 4, 8)
    g.add_edge(2, 3, 2)
    g.add_edge(3, 7, 4)
    g.add_edge(4, 9, 6)
    g.add_edge(4, 5, 2)
    g.add_edge(4, 7, 9)
    g.add_edge(4, 2, 6)
    g.add_edge(5, 7, 10)
    g.add_edge(6, 0, 1)
    g.add_edge(6, 8, 8)
    g.add_edge(7, 1, 9)
    g.add_edge(7, 2, 8)
    g.add_edge(8, 5, 4)
    g.add_edge(8, 9, 4)
    g.add_edge(9, 0, 10)
    g.add_edge(9, 4, 5)
    # g.display()
    u,v = 6,4

    print("Running bellman-ford on start %s" % (u))
    costs, prevs = bellman_ford(g, u)
    print(costs)
    cost, path = get_path(prevs, v, u)
    print("Found path with cost %s\nPath: %s" % (cost, path))
    assert (cost, path) == (17, [6, 8, 9, 4]), "Wrong result"
    # g.display()
    g.reverse()
    # print(g)
    # print(g.edgelist)
    # g.display()
    print("Running bellman-ford on reversed start %s" % (v))
    costs, prevs = bellman_ford(g, v)
    print(costs)
    cost, path = get_path(prevs, u, v)
    print("Found path with cost %s\nPath: %s" % (cost, path))
    assert (cost, path) == (17, [4, 9, 8, 6]), "Wrong result"

if __name__ == '__main__':
    call_tests([], verbose=False)
    show_stack()