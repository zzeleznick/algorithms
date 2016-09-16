import time
import random
from math import ceil
from random import shuffle
from bisect import bisect_left
from collections import deque as _deque
from collections import Counter, namedtuple
from functools import wraps
from itertools import chain
# Internal python modules
import init
from TimeUtils import *
from treap import treap as Treap

Link = namedtuple("Link", ["prev", "next"])

class zdeque(_deque):
    """docstring for zdeque"""
    def __init__(self, arg = []):
        super(zdeque, self).__init__(arg)
    def __repr__(self):
        return " ".join(["%s" % el for el in self])

def binary_search(sorted_arr, key):
    if not sorted_arr:
        return 0
    if len(sorted_arr) == 1:
        return 0 if key <= sorted_arr[0] else 1

    start, end = 0, len(sorted_arr) - 1
    median_id = (end+start) // 2
    median = sorted_arr[median_id]

    while end > start:
        # print(start, end)
        if key == median:
            return median_id
        elif key < median:
            start, end = start, median_id - 1
            median_id = (end+start) // 2
            median = sorted_arr[median_id]
        else:
            start, end = median_id + 1, end
            median_id = (end+start) // 2
            median = sorted_arr[median_id]
    if key > sorted_arr[start]:
        return start + 1
    return start


@timer
def level_sort(arr, printerMode = False):
    """
    if printerMode:
        deque = zdeque
    """
    deque = _deque
    queue = deque([deque(arr)])
    res = []
    while queue:
        elements = queue.popleft()
        if not elements:
            break
        first = elements.popleft()
        if not elements:
            res.append(first)
            continue
        small, big = deque(), deque()
        [ small.append(el) if el <= first else big.append(el) for el in elements ]
        mid = deque([first])
        [ queue.appendleft(lst) for lst in [big, mid, small] if lst ]
        """
        if printerMode:
            line = " ".join(["%s" % el for el in res]) + " " if res else ""
            print("[%s%s]" % (line, repr(queue)))
        """
    return res

@timer
def recursive_qsort(arr):
    def qs_inner(arr):
        if len(arr) <= 1:
            return arr
        elif len(arr) == 2:
            if arr[0] <= arr[1]:
                return arr
            return [arr[1], arr[0]]
        pivot = arr[len(arr)//2]
        left, pivots, right = [], [], []
        for val in arr:
            if val < pivot:
                left.append(val)
            elif val > pivot:
                right.append(val)
            else:
                pivots.append(pivot)
        return list(chain(qs_inner(left), pivots, qs_inner(right)))
    return qs_inner(arr)

def test_bin():
    arr = list(range(10))
    idx = 4
    res_idx = binary_search(arr, idx)
    assert res_idx == idx or res_idx == idx+1, "mismatch"
    arr = list(range(100))
    idx = 10
    res_idx = binary_search(arr, idx)
    assert res_idx == idx or res_idx == idx+1, "mismatch"

def test_0():
    arr = list(range(10*2))
    shuffle(arr)
    level_sort(arr, printerMode = False)

def test_1():
    arr = list(range(10**4))
    shuffle(arr)
    res1 = recursive_qsort(arr)
    assert list(range(10**4)) == res1, "mismatch"
    res2 =level_sort(arr)
    assert list(range(10**4)) == res2, "mismatch"
    """Iterative version is between thirty and forty-percent faster"""

def benchmark_level():
    benched = rand_arr_benchmark(level_sort, sizes = [100, 10**3, 10**4, 10**5])
    benched()

def benchmark_native():
    benched = rand_arr_benchmark(timer(sorted))
    benched()

def benchmark_recursive():
    benched = rand_arr_benchmark(recursive_qsort, sizes = [100, 10**3, 10**4, 10**5])
    benched()

if __name__ == '__main__':
    benchmark_recursive()
    benchmark_level()
