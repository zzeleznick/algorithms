from __future__ import print_function
import time
import argparse
import collections
from bisect import bisect_left, insort_left
from math import log, ceil
from functools import wraps
from inspect import getouterframes, currentframe
from collections import OrderedDict as OD


def named_tuple(typename, fields, defaults =()):
    T = collections.namedtuple(typename, fields)
    T.__new__.__defaults__ = (None,) * len(T._fields)
    if isinstance(defaults, collections.Mapping):
        prototype = T(**defaults)
    else:
        prototype = T(*defaults)
    T.__new__.__defaults__ = tuple(prototype)
    return T

Caller = named_tuple("Caller", ["name", "args", "kwargs", "time_elapsed"])

def call_all(*fncs):
    return [ f() for f in fncs ]

def override_print():
    try:
        globals()['zprint']
    except KeyError:
        globals()['zprint'] = globals()['__builtins__'].get('print', print)
        globals()['_stack'] = OD()
        globals()['_verbose'] = True
        pad = lambda idx: "%s " % (">" * idx) if idx > 0 else ""
        stringy = lambda arr, level=1: " ".join("%s" % el for el in arr).replace("\n", "\n%s" % pad(level))
        def pp(*ags, **kws):
            try:
                level = max(2, kws.pop('level'))
            except KeyError:
                level = max(2, len(getouterframes(currentframe(1))))
            idx = int(ceil(log(level-1, 2)))
            zprint(pad(idx), end="")
            zprint(stringy(ags, idx), **kws)
        globals()['__builtins__']['print'] = pp

class ShowTimer(object):
    def __init__(self, fnc, args, kwargs):
        override_print()
        self.name = fnc.__name__
        self.args = args
        self.kwargs = kwargs
    def __enter__(self):
        self.start = time.time()
        if globals().get("_verbose", True):
            print("------ TIMING BLOCK ------", level=0)
    def __exit__(self, type, value, traceback):
        elapsed = 1000*(time.time()-self.start)
        callee = Caller(self.name, self.args, self.kwargs, elapsed)
        if self.name not in globals()["_stack"]:
            globals()["_stack"][self.name] = [ callee ]
        else:
            globals()["_stack"][self.name].append(callee)
        if globals().get("_verbose", True):
            print("```\nCalled %s\nArgs: [%s]\nElapsed: %0.3f ms\n```" % (self.name, self.args, elapsed), level=0)

def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        override_print()
        def fmt(arg):
            s = "%s" % arg
            return s if len(s) < 50 else "%s..." % s[:50]
        if args and type(args[0]) == list:
            tmp = len(args[0])
        else:
            tmp = [ fmt(arg) for arg in args ]
        with ShowTimer(func, tmp, kwargs):
            result = func(*args, **kwargs)
        return result
    return wrapper

def testcase(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return result
    try:
        globals()['_tests']
    except KeyError:
        globals()['_tests'] = [(func, (), {})]
    else:
        globals()['_tests'].append((func, (), {}))
    return wrapper

def call_tests(indices=[], verbose=True):
    """Assumed to be called once"""
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-s", "--silent", action="store_true")
    group.add_argument("-v", "--verbose", action="store_true")
    cmd_args = parser.parse_args()
    override_print()
    tests = globals().get('_tests', [])
    for (i, (fnc, args, kwargs)) in enumerate(tests):
        if indices and i not in indices:
            continue
        print("[---- %s (%s) ----]" % (fnc.__name__, i), level=1)
        if cmd_args.verbose: # verbosity is default
            pass
        elif not verbose or cmd_args.silent:
            globals()['_verbose'] = False
        fnc(*args, **kwargs)

def show_stack():
    override_print()
    print("-" * 30)
    print("NAME", " " * 20, "TIME")
    print("-" * 30)
    for callee in globals()["_stack"].itervalues():
        for c in callee:
            elapsed = "%0.3f ms" % c.time_elapsed
            name = "%s%s" % (c.name[:14], " " * (29 - len(c.name) - len(elapsed)) )
            print(name, elapsed)

