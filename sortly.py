import time
import random
from math import ceil
from random import shuffle
from bisect import bisect_left
from collections import deque as _deque
from collections import Counter, namedtuple
from functools import wraps
from itertools import chain

from TimeUtils import timer
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

class zcounter(Counter):
    """A counter that keeps all its elements in order
       Should only take positive integers for values
       Odd behavior may ensue with mixed types or negative numbers"""

    @staticmethod
    def search(sorted_arr, val):
        """Method to find insertion point of val in a sorted array"""
        # return binary_search(sorted_arr, val)
        return bisect_left(sorted_arr, val)

    def __init__(self, arg = {}):
        self.sorted_uniques = _deque()
        self._in_init = True
        # print("Arg:", arg)
        if isinstance(arg, Counter):
            # must extract keys to re_init
            super(zcounter, self).__init__(arg.keys())
            for k,v in arg.items(): # for float cases
                self[k] = v # allow non-natural values
        else:
            super(zcounter, self).__init__(arg)
        self._in_init = False
        self.sorted_uniques = _deque(sorted(self.sorted_uniques))

    def __iter__(self):
        """overrides default iterate behavior for sorted order"""
        for k in self.sorted_uniques:
            yield(k)

    def __deletefirst(self, key):
        """Should use popitem instead of callling directly"""
        self.sorted_uniques.popleft()
        super(zcounter, self).__delitem__(key)

    def __delitem__(self, key):
        """Should use pop instead of callling directly"""
        if key in self:
            super(zcounter, self).__delitem__(key)
            idx = self.search(self.sorted_uniques, key)
            self.sorted_uniques.rotate(-idx)
            self.sorted_uniques.popleft()
            self.sorted_uniques.rotate(idx)

    def __setitem__(self, key, value):
        # print("Setting key %s with value %s" % (key,value))
        is_new = key not in self
        super(zcounter, self).__setitem__(key,value)
        if self._in_init and is_new:
            self.sorted_uniques.appendleft(key)
        elif is_new:
            new_idx = self.search(self.sorted_uniques, key)
            self.sorted_uniques.rotate(-new_idx)
            self.sorted_uniques.appendleft(key)
            self.sorted_uniques.rotate(new_idx)

    def __mul__(self, factor):
        if isinstance(factor, int) or isinstance(factor, float):
            result = zcounter(self)
            for k in result:
                result[k] = result[k] * factor
            return result
        else:
            raise NotImplementedError("Can only scale zcounters")

    def __truediv__(self, factor):
        if isinstance(factor, int) or isinstance(factor, float):
            result = zcounter(self)
            for k in result:
                result[k] = result[k] / factor
            return result
        else:
            raise NotImplementedError("Can only scale zcounters")

    def __iadd__(self, other):
        """Add values from two counters and allows floats"""
        if not isinstance(other, Counter):
            return NotImplemented
        for key, value in other.items():
            self[key] += value
        return self

    def __add__(self, other):
        """Add values from two counters and allows floats"""
        if not isinstance(other, Counter):
            return NotImplemented
        result = zcounter(self)
        for key, value in other.items():
            result[key] = result[key] + value
        return result

    def __sub__(self, other):
        """Subtract values from two counters and allows floats"""
        if not isinstance(other, Counter):
            return NotImplemented
        result = zcounter(self)
        for key, value in other.items():
            result[key] = result[key] - value
        return result

    def __or__(self, other):
        """Union is the maximum of value in either of the input counters.
        might implement a la https://hg.python.org/cpython/file/2.7/Lib/collections.py"""
        return NotImplemented

    def __and__(self, other):
        """Intersection is the minimum of intersecting counts."""
        return NotImplemented

    def __xor__(self, other):
        """see https://docs.python.org/3/reference/datamodel.html#object.__xor__"""
        return NotImplemented

    def pop(self, key):
        """overrides super pop method call to ensure in order"""
        if key not in self:
            raise(KeyError(key))
        else:
            val = self[key]
            self.__delitem__(key)
            return val

    def popitem(self):
        """overrides super popitem method call to ensure in order"""
        if not self.sorted_uniques:
            raise(KeyError('popitem(): collection is empty'))
        key = self.sorted_uniques[0]
        res = (key, self[key])
        self.__deletefirst(key)
        return res

    def keys(self):
        """overrides super values method call to ensure in order"""
        for k in self:
            yield(k)

    def values(self):
        """overrides super values method call to ensure in order"""
        for k in self:
            yield(self[k])

    def items(self):
        """overrides super items method call to ensure in order"""
        return zip(self.keys(), self.values())

    def elements(self):
        """overrides super elements method call to ensure in order
        any negative elements will not be shown"""
        for k in self:
            # iterate in order
            copies = max(1, int(ceil(self[k])))
            for _ in range(copies):
                # yield duplicates
                yield(k)

def rand_arr_benchmark(func, sizes = [100, 1000, 10000]):
    @wraps(func) # meta-data capture
    def benchmark(size, **kwargs):
        arr = list(range(size))
        shuffle(arr)
        start = time.time()
        result = func(arr, **kwargs)
        end = time.time()
        return ((end - start), result)
    def run(**kwargs):
        results = []
        for size in sizes:
            delta, res = benchmark(size, **kwargs)
            print("Size: %s\t Item/ms: %s" % (size, size/(1000*delta)) )
            results.append((delta,res))
        return results
    return run

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

def test_bin():
    arr = list(range(10))
    idx = 4
    res_idx = binary_search(arr, idx)
    assert res_idx == idx or res_idx == idx+1, "mismatch"
    arr = list(range(100))
    idx = 10
    res_idx = binary_search(arr, idx)
    assert res_idx == idx or res_idx == idx+1, "mismatch"

@timer
def test_zcounter(arr):
    return zcounter(arr)

def benchmark_zcounter():
    benched = rand_arr_benchmark(test_zcounter)
    benched()

def benchmark_native_counter():
    @timer
    def make_ctr(arr):
        arr.sort()
        return Counter(arr)
    benched = rand_arr_benchmark(make_ctr)
    benched()

@timer
def zcounter_add_n_items(n):
    arr = list(range(1000))
    shuffle(arr)
    ctr = zcounter(arr)
    for i in range(n):
        r = random.randint(1000,2000)
        ctr.update([r])
        r2 = random.randint(0,1000)
        if r2 in ctr:
            ctr.pop(r2)
    return ctr
    # elements = [ random.randint(1000,2000) for i in range(n) ]
@timer
def native_add_n_items(n):
    arr = list(range(1000))
    shuffle(arr)
    sorted(arr)
    for i in range(n):
        r = random.randint(1000,2000)
        arr.extend([r])
        arr.pop()
        sorted(arr)

@timer
def treap_add_n_items(n):
    arr = list(range(1000))
    shuffle(arr)
    t = Treap()
    for el in arr:
        t[el] = 1
    for i in range(n):
        r = random.randint(1000,2000)
        t[r] = 1
        r2 = random.randint(0,1000)
        if r2 in t:
           t.remove(r2)
    return t

if __name__ == '__main__':
    # benchmark_native()
    # benchmark_native_counter()
    # benchmark_zcounter()
    benchmark_recursive()
    benchmark_level()
    # native_add_n_items(400)
    # ctr = zcounter_add_n_items(400)
    # t = treap_add_n_items(400)
    # print(list(ctr.elements()))