from __future__ import print_function
import random
from itertools import chain
from collections import deque, namedtuple
from collections import OrderedDict as OD
# from sortedcontainers import SortedList
from heapq import *

from Graph import *
from TimeUtils import *

@timer
def search(g, start, goal):
    """Finds the closest path u->v on graph g"""
    State = namedtuple("State", ["node", "path"])
    visited = OD()
    costs = {v: float('inf') for v in g.vertices }
    fringe = []
    state = State(start, [start])
    heappush(fringe, (0, state))
    while fringe:
        cost, state = heappop(fringe) # pop the min element
        node = state.node
        if node == goal:
            print("Visited %s nodes" % len(visited))
            return (cost, state.path)
        if node in visited:
            continue
        visited[node] = True
        for (v, w) in g[node].edges.iteritems():
            next_cost = cost+w
            next_state = State(v, list(chain(state.path, [v])))
            if next_cost <= costs[v]:
                costs[v] = min(costs[v], next_cost)
                heappush(fringe, (next_cost, next_state))
    print("No path found from %s -> %s" % (start, goal))
    return (0, None)

@testcase
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
    print("Searching for the shortest path %s --> %s" % (6,4))
    cost, path = search(g, 6, 4)
    print("Found path with cost %s\nPath: %s" % (cost, path))
    assert (cost, path) == (17, [6, 8, 9, 4]), "Wrong result"
    g.reverse()
    # g.display()
    cost, path = search(g, 4, 6)
    print("Found path with cost %s\nPath: %s" % (cost, path))
    assert (cost, path) == (17, [4, 9, 8, 6]), "Wrong result"

@testcase
def test_2():
    sizes = [100, 10**3, 10**4, 5*10**4]
    for s in (sizes):
        random.seed(10)
        TimeableGraph.set_weight_range(1,s)
        g = TimeableGraph.generate(s, 10*s)
        u,v = random.randint(0,50), random.randint(0,50)
        print("Searching for the shortest path %s --> %s" % (u,v))
        cost, path = search(g, u, v)
        print("Found path with cost %s\nPath: %s" % (cost, path))

if __name__ == '__main__':
    # test()
    # test_2()
    call_tests(verbose=False)