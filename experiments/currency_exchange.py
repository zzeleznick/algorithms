"""
Data from Slide (32 of 47) https://www.cs.princeton.edu/~rs/AlgsDS07/15ShortestPaths.pdf
"""
from __future__ import print_function
import pandas as pd
from collections import OrderedDict as OD
from math import log10
from heapq import *
# Internals
import init
from Graph import *
from utils import *
from experiments.queue import PriorityQueue

# DATA_FILE = "currencies.csv"
DATA_FILE = "currencies_cycle.csv"

def load_data(fname = DATA_FILE):
    with open(fname) as infile:
        df = pd.read_csv(infile, sep=',')
        # drop leading currency column
        df = df[df.columns[1:]]
        # convert int index to column
        df = df.set_index(df.columns)
    return df

def make_graph():
    df = load_data()
    edges = df.to_dict()
    g = Graph(edges)
    return g

def ck_bellman_ford(g, start, k=0):
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
            next_cost = costs[i-1][u] -log10(w)
            if next_cost < costs[i][v]:
                costs[i][v] = next_cost
                prevs[v] = (-log10(w), u)
    # Check for any negative-weight cycles
    for ((u, v), w) in g.edgelist:
        if costs[k][u] - log10(w) < costs[k][v]:
            if v == start:
                print("RoR: %s" % 10**(-(costs[k][u] - log10(w))))
            # raise Exception("Graph contains a negative-weight cycle")
            # print("Graph contains a negative-weight cycle"); break
    return (costs, prevs)

def c_dijkstra(g, start, end):
    visited = OD()
    costs = {v: 0 for v in g.vertices }
    prevs = {v: (1, None) for v in g.vertices }
    costs[start] = g[start][end] # rate directly
    fringe = PriorityQueue(costs, maxheap=True)
    while fringe:
        rate, node = fringe.pop() # pop the max element
        if node in visited:
            continue
        visited[node] = True
        for (v, w) in g[node].edges.iteritems():
            pre_cost = rate * 1.0 / g[node][end]
            next_cost = pre_cost * w * g[v][end]
            if next_cost > costs[v]:
                print("Update: %s -> %s to %s from %s" % (node, v, next_cost, costs[v]))
                print("Pre_cost: %s, w: %s, to $: %s" % (pre_cost, w,g[v][end] ))
                costs[v] = next_cost
                prevs[v] = (log10(w), node)
                fringe[v] = next_cost
    print("Visited %s nodes" % len(visited))
    return (costs, prevs)

def main():
    g = make_graph()
    # print(g.adjacency_map)
    u,v = "Gold", "Dollar"
    # costs, prevs = c_dijkstra(g, u, v)
    costs, prevs = ck_bellman_ford(g, u)
    print(costs)
    print(prevs)
    cost, path = get_path(prevs, v, u)
    print(10**(-cost))
    # print(10**(cost))
    print(path)

if __name__ == '__main__':
    main()

