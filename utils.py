from __future__ import print_function
import os
from collections import deque
from collections import OrderedDict as OD

OUTPUT_FOLDER = 'output/'

class FileManager(object):
    dest = OUTPUT_FOLDER
    if not os.path.exists(dest):
        os.mkdir(dest)
    home = os.getcwd()
    outname = "testGraph"
    def __enter__(self):
        os.chdir(self.dest)
        return self
    def __exit__(self, type, value, traceback):
        os.chdir(self.home)
    @classmethod
    def gen_fileid(cls):
        idx = "%s" % len([name for name in os.listdir(os.getcwd()) if name.endswith(".md")])
        return "%s%s" % ("0" * (2-len(idx)), idx)
    @classmethod
    def gen_filename(cls):
        padded_id = cls.gen_fileid()
        return "%s-%s.md" % (cls.outname, padded_id)
    @classmethod
    def display(cls, caller, fname=None):
        fname = cls.gen_filename() if not fname else fname
        rpath = fname + ".png"
        with open(fname, "w") as outfile:
            outfile.write("graph TD;\n")
            outfile.write(caller())
        os.system("mermaid %s > /dev/null" % fname)
        os.system("open %s" % rpath)

def yielder(scalar, n):
    for i in xrange(n):
        yield scalar

def interject(tuplist, scalar, first=True):
    if not tuplist:
        return []
    if first:
        return [ ((s, t[0]), t[1]) for t,s in zip(tuplist, yielder(scalar, len(tuplist))) ]
    return [ ((t[0], s), t[1]) for t,s in zip(tuplist, yielder(scalar, len(tuplist))) ]

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

