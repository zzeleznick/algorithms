from __future__ import print_function
import random
from itertools import chain
from collections import deque, namedtuple
from collections import OrderedDict as OD
from heapq import *

from Graph import *
from TimeUtils import *

def unpack(klass):
    res = [ klass.__getattribute__(field) for field in klass._fields ]
    return res

@timer
def tarjan(g):
    """Finds the scc graph g"""
    fringe = []
    enqueued = OD()
    indices  = OD()
    lowlinks = OD()
    result   = OD()
    TarjanCtx = namedtuple("TarjanCtx", ["fringe", "enqueued",
                                        "indices", "lowlinks", "result"])
    global ctx
    ctx = TarjanCtx(fringe, enqueued, indices, lowlinks, result)
    def visit(v):
        fringe, enqueued, indices, lowlinks, result = unpack(ctx)
        index = len(indices)
        indices[v.name] = index
        lowlinks[v.name] = index
        fringe.append(v)
        enqueued[v.name] = True
        for w in v.edges:
            if indices.get(w) == None:
                # Successor w is has not been visited
                visit(g[w])
                lowlinks[v.name] = min(lowlinks[v.name], lowlinks[w])
            elif (enqueued[w]):
                # Successor w is in stack S and hence in the current SCC
                lowlinks[v.name] = min(lowlinks[v.name], indices[w])
        # check if vertex is root of scc
        if indices[v.name] == lowlinks[v.name]:
            result[v.name] = []
            w = Vertex(None)
            while v.name != w.name:
                w = fringe.pop()
                enqueued[w.name] = False
                result[v.name].append(w.name)
    # End Visit Definition
    for (v) in g.vertices.itervalues():
        if indices.get(v.name) == None:
            visit(v)
    # End Visit Routine
    # print("Indices:\n%s" % indices)
    # print("Lowlinks:\n%s" % lowlinks)
    return result

@testcase
@timer
def test():
    g = TimeableGraph([Vertex(i) for i in range(8)])
    g.add_edge(0, 1)
    g.add_edge(0, 2)
    g.add_edge(0, 3)
    g.add_edge(2, 0)
    g.add_edge(3, 0)
    g.add_edge(3, 4)
    g.add_edge(4, 5)
    g.add_edge(5, 4)
    g.add_edge(5, 6)
    # g.display()
    print("Searching for scc on g")
    res = tarjan(g)
    print("Result:\n%s" % res)

@testcase
@timer
def test_2():
    names = ["A", "B", "C", "D", "E", "F", "G", "H"]
    g = TimeableGraph([Vertex(i) for i in names])
    g.add_edge(names[0], names[1])
    g.add_edge(names[0], names[2])
    g.add_edge(names[0], names[3])
    g.add_edge(names[2], names[0])
    g.add_edge(names[3], names[0])
    g.add_edge(names[3], names[4])
    g.add_edge(names[4], names[5])
    g.add_edge(names[5], names[4])
    g.add_edge(names[5], names[6])
    # g.display()
    print("Searching for scc on g")
    res = tarjan(g)
    print("Result:\n%s" % res)

@testcase
def test_3():
    print("Hi")

@testcase
@timer
def test_4():
    print("DERP")
    time.sleep(1)

@testcase
@timer
def test_5():
    g = TimeableGraph.generate(5*10**3, 10**3)
    print("Searching for scc on g")
    res = tarjan(g)

if __name__ == '__main__':
    # test()
    # test_2()
    call_tests(verbose=False)
    show_stack()