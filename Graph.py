from __future__ import print_function
import random
from itertools import chain
from collections import Mapping, Iterable
from collections import OrderedDict as OD

from TimeUtils import *
from utils import *

class Vertex(object):
    """A representation of a node with potential edges and weights.
    Vertex.edges -> an ordered dictionary storing outgoing edges in the form {name: weight}
    Vertex._add_edge and Vertex._remove_edge should be called by the Graph class since
    the actual neighbors (Vertices) are stored in the graph, whereas the vertex stores the
    outgoing names and weights in its dictionary, not the objects.
    """
    def __init__(self, name, value=None):
        self.name = name
        self.value = name if (type(name) == int and value == None) else value
        self._edges = OD()
    def __setitem__(self, name, value):
        if value:
            self._add_edge(name, value)
        else:
            self._remove_edge(name)
    def __getitem__(self, name):
        return self._edges[name]
    def get(self, name, default=None):
        if name in self._edges:
            return self._edges[name]
        return default
    def _remove_edge(self, name):
        self._edges.pop(name)
    def _add_edge(self, name, weight=1):
        self._edges[name] = weight
    @classmethod
    def validate(cls, v):
        if not issubclass(type(v), Vertex):
            return False
        return True
    @property
    def edges(self):
        return self._edges

class Graph(object):
    """Graph class defaults"""
    # V, E, = 10, 15
    w_min, w_max = 1, 1
    def __init__(self, elements=[]):
        self._vertices = OD()
        if isinstance(elements, Mapping):
            vertices = [ Vertex(v) for v in elements.iterkeys() ]
            self._vertices.update({v.name: v for v in vertices})
            for (k, val) in elements.iteritems():
                if isinstance(val, Mapping):
                    [ self.add_edge(k,v,w) for (v,w) in val.iteritems() ]
                elif isinstance(val, Iterable):
                    [ self.add_edge(k,v) for v in val ]
                else:
                    # Mapping value must be iterable!
                    raise TypeError("Input non-iterable value in mapping.")
        else:
            vertices = [v if Vertex.validate(v) else Vertex(v) for v in elements]
            self._vertices.update({v.name: v for v in vertices})
    def __getitem__(self, name):
        return self._vertices[name]
    def __repr__(self):
        f = lambda k,v: str((k, v.keys())) if len(v) > 0 else str((k, []))
        return "\n".join(f(k,v) for (k,v) in self.adjacency_map.iteritems())
    @property
    def vertices(self):
        return self._vertices
    @property
    def adjacency_map(self):
        """The adjaceny map remains a dynamic property"""
        return {v.name: v.edges for v in self._vertices.itervalues() }
    @property
    def edgelist(self):
        mono = lambda v: self._get_mono_edgelist(v)
        return list(chain.from_iterable(mono(v) for v in self._vertices.itervalues() if v.edges))
    def _get_mono_edgelist(self, v):
        """Gets edges ((u,v), w) for one vertex u"""
        return interject(v.edges.items(), v.name)
    def add_vertex(self, name, value=None):
        v = Vertex(name, value)
        self._vertices[v.name] = v
    def remove_vertex(self, name):
        self._vertices.pop(name)
        for (i, v) in self._vertices.iteritems():
            if name in v.edges:
                v._remove_edge(name)
    def remove_edge(self, u, v):
        self._vertices[u]._remove_edge(v)
    def add_edge(self, u, v, w=1):
        if not self._vertices.get(v):
            raise Exception("No vertex %s could be added to vertex %s" % (v, u) )
        self._vertices[u]._add_edge(v,w)
    def remove_all_edges(self):
        [ self[v].edges.clear() for v in self._vertices]
    def is_path(self, start, goal):
        """Greedy algorithm to find any path to goal.
        Note that paths are not even directional, just the relative ordering
        of which nodes were explored first off of the fringe.
        If enumerated, the visited keys correspond to pre-order numbers"""
        visited = OD()
        fringe = [start]
        while fringe:
            v = fringe.pop()
            visited[v] = True
            if v == goal:
                return visited.keys()
            [ fringe.append(k) for k in self[v].edges.keys() if k not in visited ]
        return False

    def display(self):
        style = lambda u, v, w: "\t%s-->%s;" % (u, v) if w == 1 else "\t%s -- %s -->%s;" % (u, w, v)
        row_gen = lambda u: "\n".join(style(u.name, v, w) for (v,w) in u.edges.items()) if u.edges else "\t%s" % u.name
        full_gen = lambda: "\n".join("%s" % r for r in (row_gen(v) for v in self._vertices.itervalues()) if r)
        with FileManager() as FM:
            FM.display(full_gen)
    @classmethod
    def set_weight_range(cls, low=1, hi=1):
        cls.w_min, cls.w_max = low, hi
    @classmethod
    def generate(cls, v, e, allow_cycles=True, weight_range=None):
        """Generates a graph with v vertices and e edges
        Invariants:
            1. No self-pointing edges
        """
        weight_range = (cls.w_min, cls.w_max) if weight_range == None else weight_range
        graph = cls([Vertex(i) for i in range(v)])
        filled = 0
        while filled <= e:
            x, y = random.randint(0,v-1), random.randint(0,v-1)
            if x != y and not graph[x].get(y):
                if not allow_cycles and graph.is_path(y,x):
                    continue
                graph[x][y] = random.randint(*weight_range)
                filled += 1
        return graph
    @classmethod
    def generate_DAG(cls, v, e):
        """Generates a graph with v vertices and e edges
        Invariants:
            1. No self-pointing edges
            2. No cycles
        """
        return cls.generate(v, e, allow_cycles=False)

class ReversibleGraph(Graph):
    def __init__(self, vertices=[]):
        super(ReversibleGraph, self).__init__(vertices)
        self._reversed = False
    def reverse(self):
        """Modifies our internal state and flips the direction of all edges"""
        self._reversed = not self._reversed
        # Now our edgelist will be reversed
        # We sort edges by first value (assuming scalar numeric names for vertices)
        edges = sorted(self.edgelist)
        # delete all previous edges
        self.remove_all_edges()
        # now add the reversed edges
        for ((u,v), w) in edges:
            self.add_edge(v, u, w)

class TimeableGraph(ReversibleGraph):
    @classmethod
    @timer
    def generate(cls, v, e, allow_cycles=True, weight_range=None):
        return super(TimeableGraph, cls).generate( v, e, allow_cycles, weight_range)
    @timer
    def reverse(self):
        return super(TimeableGraph, self).reverse()

def test_init():
    print("Making a Graph from a generic range...")
    g = Graph([i for i in range(5)])
    print(g)
    print("Making a Graph from an array of Vertices...")
    g = Graph([Vertex(i) for i in range(5)])
    print(g)
    print("Making a Graph from a basic mapping...")
    g = Graph({i: [j for j in range(i)] for i in range(10)})
    print(g)
    print("Making a Graph from a nested mapping...")
    g = Graph({i: {j: i for j in range(i)} for i in range(10)})
    print(g)
    print(g.adjacency_map)

def test_reverse():
    g = ReversibleGraph.generate(10,20)
    print(g)
    g.display()
    print("Going to reverse our graph...")
    g.reverse()
    print(g)
    g.display()

def test_weighted_graph():
    print(ReversibleGraph.w_min, ReversibleGraph.w_max)
    ReversibleGraph.set_weight_range(1,10)
    print(ReversibleGraph.w_min, ReversibleGraph.w_max)
    g = ReversibleGraph.generate(10,20)
    print(g)
    g.display()

def test_reverse_2():
    sizes = [100, 10**3, 10**4, 5*10**4]
    for s in (sizes):
        random.seed(10)
        TimeableGraph.set_weight_range(1,s)
        g = TimeableGraph.generate(s, 10*s)
        print("Going to reverse our graph...")
        g.reverse()

if __name__ == '__main__':
    # test_reverse_2 = testcase(test_reverse_2)
    test_init = testcase(test_init)
    call_tests()
    show_stack()