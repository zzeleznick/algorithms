from __future__ import print_function
import random
from copy import deepcopy
from collections import OrderedDict as OD
from collections import Counter, deque
from Graph import Vertex, Graph

def generate_graph(v, e):
    """Generates a graph with v vertices and e edges
    Invariants:
        1. No self-pointing edges
    """
    import numpy as np
    adjency_matrix = np.zeros((v,v))
    graph = {i: {} for i in range(v)}
    filled = 0
    while filled <= e:
        x, y = random.randint(0,v-1), random.randint(0,v-1)
        if x != y and not graph[x].get(y):
            graph[x][y] = True
            adjency_matrix[x][y] = 1
            filled += 1
    print(adjency_matrix)
    return adjency_matrix

def calc_indegrees(graph):
    indegrees = Counter()
    for v in graph.vertices.itervalues():
        indegrees.update(v.edges.keys())
    return indegrees

def topsort(graph):
    indegrees = calc_indegrees(graph)
    sources = deque([v for v in graph.vertices if v not in indegrees])
    visited = []
    while sources:
        name = sources.popleft()
        visited.append(name)
        edges = graph[name].edges.keys()
        [ graph.remove_edge(name, e) for e in edges ]
        indegrees = calc_indegrees(graph)
        for e in edges:
            if not indegrees[e]:
                sources.append(e)
    if len(visited) != len(graph.vertices):
        # there is a cycle!
        print("Topsort not possible for this graph")
    else:
        print(visited)

def topsort_2(original_graph):
    """Topsorts and then finds the longest path"""
    graph = deepcopy(original_graph)
    indegrees = calc_indegrees(graph)
    sources = [name for name in graph.vertices if name not in indegrees]
    visited = OD()
    level_map = OD()
    level = 0
    while sources:
        level += 1
        visited.update(zip(sources, [level]*len(sources)))
        level_map[level] = sources
        for name in sources:
            edges = graph[name].edges.keys()
            [ graph.remove_edge(name, e) for e in edges ]
        indegrees = calc_indegrees(graph)
        sources = [name for name in graph.vertices if name not in indegrees and name not in visited]

    if len(visited) != len(graph.vertices):
        # there is a cycle!
        print("Topsort not possible for this graph")
    else:
        print("Topsort (name, level):\n%s" % visited.items())
        max_path = calc_max_path_2(original_graph, level_map)
        print("Longest Path:\n%s" % max_path)
        original_graph.display()

def first(gen):
    try:
        return gen.next()
    except StopIteration:
        return None

def mmax(seq):
    """"Returns the index and value of max value in seq"""
    index = 0
    best = first(seq)
    if best == None:
        return (-1, 0)
    for (idx, el) in enumerate(seq,1):
        if el > best:
            index, best = idx, el
    return (index, best)

def calc_max_path(graph, visited):
    """Calculates the max path as the number of nodes visited"""
    name, level = visited.popitem()
    path = OD()
    while name != None:
        path[name] = level
        name = first(pname for pname in graph.vertices if graph[pname].edges.get(name) and visited[pname] == level-1)
        level -= 1
    return path.items()[::-1]

def calc_max_path_2(graph, level_map):
    """Calculates the max path including the value of nodes"""
    costs = Counter()
    paths = OD()
    while level_map:
        level, names = level_map.popitem()
        for name in names:
            idx, best =  mmax(costs[child] for child in graph[name].edges)
            costs[name] = graph[name].value + best
            fav_child = graph[name].edges.keys()[idx] if idx != -1 else None
            paths[name] = [ name ]
            if fav_child != None:
                paths[name].extend(paths[fav_child])
    print("Costs %s" % costs)
    start, length = costs.most_common(1)[0]
    path = paths[start]
    return path

def main():
    V = 10 # number of nodes
    E = 8 # number of edges
    graph = Graph.generate_DAG(V,E)
    topsort_2(graph)

if __name__ == '__main__':
    main()

