import time
import random
from math import ceil
from bisect import bisect_left
from collections import deque as _deque
from collections import Counter, namedtuple
# Internal python modules
import init
from TimeUtils import *

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

@testcase
@timer
def test_zcounter(arr):
    return zcounter(arr)

@testcase
@timer
def benchmark_zcounter():
    rand_arr_benchmark(test_zcounter)()

@testcase
def benchmark_native_counter():
    @timer
    def make_ctr(arr):
        arr.sort()
        return Counter(arr)
    benched = rand_arr_benchmark(make_ctr)()

@testcase
@timer
def benchmark_native():
    benched = rand_arr_benchmark(sorted)()

@testcase
@timer
def zcounter_add_n_items(n):
    arr = list(range(1000))
    random.shuffle(arr)
    ctr = zcounter(arr)
    for i in range(n):
        r = random.randint(1000,2000)
        ctr.update([r])
        r2 = random.randint(1000,2000)
        if r2 in ctr:
            ctr.pop(r2)
    return ctr

@testcase
@timer
def native_add_n_items(n):
    arr = list(range(1000))
    random.shuffle(arr)
    sorted(arr)
    for i in range(n):
        r = random.randint(1000,2000)
        arr.extend([r])
        arr.pop()
        sorted(arr)

@timer
def treap_add_n_items(n):
    arr = list(range(1000))
    random.shuffle(arr)
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
    # benchmark_zcounter()
    # benchmark_native_counter()
    # benchmark_native()
    native_add_n_items(400)
    ctr = zcounter_add_n_items(400)
    # t = treap_add_n_items(400)
    # print(list(ctr.elements()))
    show_stack()