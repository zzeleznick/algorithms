"""
Mumbling Martians - CS170 programming project
Due 10/10
"""
from __future__ import print_function, unicode_literals
import re
from io import BytesIO, StringIO
from collections import OrderedDict as OD
from collections import deque, namedtuple
from itertools import chain

# Internals
import init
from Graph import *
from utils import *
from dk import *

# Externals
from suffix_trees.STree import STree

def read(s_io, start=0, end=0):
    s_io.seek(start)
    res = s_io.read(end-start)
    s_io.seek(0)
    return res

def DFS(g, start, goal):
    Node = namedtuple("Node", ["vertex", "path"])
    visited = OD()
    fringe = deque( [Node(start, [start])] )
    while fringe:
        # print(fringe)
        node = fringe.popleft()
        # print(node)
        v, path = node.vertex, node.path
        visited[v] = True
        if v == goal:
            return path
        verts = sorted([k for k in g[v].edges.keys() if k not in visited], reverse=True)
        nodes = [ Node(v, list(chain(path, [v]))) for v in verts  ]
        fringe.extendleft(nodes)
    return False

def create_graph(d,s,t_d):
    g = ReversibleGraph([Vertex(name=i, value=letter) for (i,letter) in enumerate(s)])
    query = StringIO(s)
    size = len(s)
    g.add_vertex(name=size, value="")
    for i in range(0, size):
        # iterate first char to end
        for j in range(i+1, size+1):
            # read from i to end including trail char
            subq = read(query,start=i,end=j)
            # print(subq)
            res = d.get(subq)
            if res:
                # print("%s: %s" % (subq, res))
                g.add_edge(i, j, w=res)
    # print(g)
    return g

def translate(d,s,t_d):
    """
    Returns a valid translation of s using words in d
    Breaks ties by shortest earliest word
    Runs in O(n^3)
    You don't need to worry about the t_d argument unless you're modifying transform_d
    >>> translate({"gork":"hello","bork":"world"},"gorkbork")
    "hello world"
    """
    g = create_graph(d, s, t_d)
    # g.display()
    size = len(s)
    path = DFS(g, 0, size)
    out = []
    if path:
        print("Found path: %s" % path)
        prev = None
        for (k, idx) in enumerate(path):
            if k != 0:
                word = s[prev:idx]
                human_word = d[word]
                out.append(human_word)
                print("%s: %s" % (word, human_word))
            prev = idx
    return " ".join(out)

def num_interpretations(d,s,t_d):
    """
    Returns the number of possible translations of s using words in d
    Runs in O(n^3)
    You don't need to worry about the t_d argument unless you're modifying transform_d
    >>> num_interpretations({"gork":"hello","g":"hi","ork":"friends"},"gork")
    2
    """
    g = create_graph(d, s, t_d)
    size = len(s)
    start = 0
    path_count = {i: 0 for i in range(size+1) }
    path_count[start] = 1
    """
    ordered_vertices = topsort(g)
    if not ordered_vertices:
        return None
    """
    od_edges = OD()
    for v in range(size+1):
        od_edges.update(dict(g._get_mono_edgelist(g[v])))
        # sorted(g._get_mono_edgelist(g[v]), key=lambda x: x[0][1])
    # print(od_edges)
    visited = {start: True}
    for (u,v) in od_edges:
        if u in visited:
            path_count[v] = path_count[v] + path_count[u]
            visited[v] = True
    # print(path_count)
    return path_count[size]

def transform_d(d):
    """
    If you need to mutate d for any reason (probably only relevant for an O(n^2) solution),
    use this function instead of mucking around with the starter code
    Whatever is returned from this function will be passed in to translate
    and num_interpretations
    """
    return None

# you don't need to worry about anything below this line - it just parses input
# if your program is crashing somewhere here, it's likely the root cause is either
# in the way you called the program (is the file in your local directory and valid?)
# or originates somewhere in your code
# if not, please let us know on Piazza!
import sys
if len(sys.argv) != 4:
    print("USAGE: ./main.py INPUT_FILE OUTPUT_TRANSLATE_FILE OUTPUT_NUM_INTERPRETATIONS_FILE")
    exit(1)
input_file = sys.argv[1]
output_translate_file = sys.argv[2]
output_num_interpretations_file = sys.argv[3]
d = {}
queries = []
with open(input_file) as f:
    # first line gives us the number of elements in the dictionary
    n = int(f.readline())
    d = {}
    for _ in range(n):
        # each successive line is a space-separated dictionary element
        martian_word, english_word = f.readline().replace('\n','').split(' ')
        d[martian_word] = english_word
    # the rest of the lines are queries
    for s in f:
        queries.append(s.replace('\n',''))
t_d = transform_d(d)
with open(output_translate_file,'w') as f:
    for query in queries:
        answer = translate(d,query,t_d)
        f.write(str(answer)+"\n")
        # exit(1)
with open(output_num_interpretations_file,'w') as f:
    for query in queries:
        answer = num_interpretations(d,query,t_d)
        f.write(str(answer)+"\n")
        # exit(1)

