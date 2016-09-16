from __future__ import print_function
import random
from collections import deque, namedtuple, Counter
from collections import OrderedDict as OD
from heapq import *

from Graph import *
from TimeUtils import *

# from experiments.queue import queue_insert

def get_path(prevs, goal, start):
    """Gets the path from start to goal using prev"""
    path = OD({goal: 0})
    cur = goal
    while cur != start:
        (cost, node) = prevs.get(cur)
        if node == None or node in path:
            print("ERROR: No path found from %s -> %s" % (start, goal))
            return (0, None)
        path[node] = path[cur] + cost
        cur = node
    return (path[start], path.keys()[::-1])

def search(g, start, goal):
    """Finds the closest path u->v on graph g
    if the path DNE:
        return (0, None)
    else:
        return (cost, path)
    """
    return dijkstra(g, start, goal)

@timer
def dijkstra(g, start, goal=None):
    """
    Finds the closest distances from u->(v in V) in graph g
    Returns either a cost for one path, or all costs and
    a dict from which paths (u->v) can be found.
    -----------------------------------------------------
    if goal:
       return cost, path
    else:
      return costs, prevs
    -----------------------------------------------------
    Data Structures:
    visited: which vertices have been visited
    costs: min cost from u->v (v,w)
    prevs: min edge u from v with weight w (w,v)
    """
    visited = OD()
    costs = {v: float('inf') for v in g.vertices }
    prevs = {v: (0, None) for v in g.vertices }
    fringe = []
    heappush(fringe, (0, start))
    # fringe = deque([(0, start)])
    while fringe:
        cost, node = heappop(fringe) # pop the min element
        # cost, node = fringe.popleft()
        if goal != None and node == goal:
            print("Visited %s nodes" % len(visited))
            return get_path(prevs, goal, start)
        if node in visited:
            continue
        visited[node] = True
        for (v, w) in g[node].edges.iteritems():
            next_cost = cost+w
            if next_cost < costs[v]:
                costs[v] = next_cost
                prevs[v] = (w, node)
                heappush(fringe, (next_cost, v))
                # queue_insert(fringe, (next_cost, v), key=lambda x: x[0])
    print("Visited %s nodes" % len(visited))
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
    sizes = [100, 10**3, 10**4, 2*10**4, 4*10**4]
    for s in (sizes):
        random.seed(10)
        TimeableGraph.set_weight_range(1,s)
        g = TimeableGraph.generate(s, 10*s)
        u,v = random.randint(0,50), random.randint(0,50)
        print("Running dijkstra from %s " % (u))
        costs, prevs = dijkstra(g, u)
        print("Searching for the shortest path %s --> %s" % (u,v))
        cost, path = get_path(prevs, v, u)
        print("Found path with cost %s\nPath: %s" % (cost, path))

@testcase
def test_3():
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
    call_tests([2], verbose=False)
    show_stack()