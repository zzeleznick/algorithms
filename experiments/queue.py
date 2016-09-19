import itertools
from heapq import *
from collections import deque, namedtuple, Mapping
from collections import OrderedDict as OD
# Internal python modules
import init
from TimeUtils import *

class PriorityQueue(object):
    NULL = '<null-item>' # placeholder for a removed item
    def __init__(self, items=[], maxheap=False):
        self._maxheap = maxheap # whether to return lowest value on pop
        self.heap = []   # list of items arranged in a heap
        self.mapping = OD() # mapping of items to heap
        self.counter = itertools.count() # unique sequence count
        if isinstance(items, Mapping):
            [ self.insert(k,v) for (k,v) in items.iteritems() ]
        else:
            [ self.insert(k) for (k) in items]
    @property
    def weight(self):
        """Allows for max heap to flip signs"""
        return (1-2*int(self._maxheap))
    @property
    def items(self):
        return [ self[k][-1] for (p,c,k) in self.heap if k is not self.NULL ]
    def __repr__(self):
        return repr(self.items)
    def __len__(self):
        return len(self.mapping)
    def __iter__(self):
        return iter(self.mapping)
    def __getitem__(self, key):
        return self.mapping[key]
    def __setitem__(self, key, value):
        self.insert(key, value)
    def insert(self, item, priority=0):
        'Add a new item or update the priority of an existing item'
        priority = self.weight * priority
        if item in self.mapping:
            self.remove(item)
        count = next(self.counter)
        entry = [priority, count, item]
        self.mapping[item] = entry
        heappush(self.heap, entry)
    def remove(self, item):
        'Mark an existing item as NULL.  Raise KeyError if not found.'
        entry = self.mapping.pop(item)
        entry[-1] = self.NULL
    def pop(self):
        'Remove and return the lowest priority item. Raise KeyError if empty.'
        while self.heap:
            priority, count, item = heappop(self.heap)
            priority = self.weight * priority
            if item is not self.NULL:
                del self.mapping[item]
                return (priority, item)
        raise KeyError('pop from an empty priority queue')

def bisect_left(a, x, lo=0, hi=None, key=None):
    if lo < 0:
        raise ValueError('lo must be non-negative')
    if hi is None:
        hi = len(a)
    if key is None:
        key = lambda x:x
    xval = key(x)
    while lo < hi:
        mid = (lo+hi)//2
        if key(a[mid]) < xval: lo = mid+1
        else: hi = mid
    return lo

def queue_insert(q, value, key=lambda x: x):
    new_idx = bisect_left(q, value, key=key)
    length = len(q)
    if new_idx < length // 2:
        q.rotate(-new_idx)
        q.appendleft(value)
        q.rotate(new_idx)
    else:
        q.rotate(length-new_idx)
        q.append(value)
        q.rotate(-(length-new_idx))

def queue_remove(q, value, key=lambda x: x):
    idx = bisect_left(q, value, key=key)
    length = len(q)
    if idx < length // 2:
        q.rotate(-idx)
        q.popleft()
        q.rotate(idx)
    else:
        q.rotate((length-1)-idx)
        q.pop()
        q.rotate(-(length-1-idx))

def test_queue():
    a = deque(range(10))
    print a
    queue_insert(a, 12)
    print a
    queue_insert(a, 11.5)
    print a
    queue_insert(a, 2.5)
    print a
    queue_remove(a, 2.5)
    print a
    queue_remove(a, 9)
    print a
    queue_insert(a, 9)
    print a
    queue_insert(a, 9)
    print a
    queue_remove(a, 9)
    print a

def test_priority_queue():
    q = PriorityQueue(range(12))
    print q
    for i in q.items:
        assert q[i][-1] == i, "q did not assemble correctly"
    q[0] = 10
    assert q[0][0] == 10 and q[0][1] == 12,  "q did not set correctly"
    p, el = q.pop()
    assert p == 0 and el == 1, "q did not pop correctly"
    print q
    q[20] = -10
    print q
    p, el = q.pop()
    assert el == 20 and p == -10, "q did not pop correctly"
    print "Success"

def test_max_priority_queue():
    q = PriorityQueue(range(12), maxheap=True)
    print q
    for i in q.items:
        assert q[i][-1] == i, "q did not assemble correctly"
    q[0] = 10
    assert q[0][0] == -10 and q[0][1] == 12,  "q did not set correctly"
    p, el = q.pop()
    assert el == 0 and p == 10, "q did not pop correctly"
    print q
    q[20] = -10
    print q
    p, el = q.pop()
    assert el == 1 and p == 0, "q did not pop correctly"
    print "Success"

def test_perf(size=10**4):
    q = deque(range(size))
    @timer
    def remove(value):
        queue_remove(q, value)
    @timer
    def insert(value):
        queue_insert(q, value)
    remove(size//8)
    insert(size//8)
    # remove(size//2)
    # remove(size//1.1)

def test_native_perf(size=10**4):
    arr = list(range(size))
    @timer
    def native_remove(value):
        arr.remove(value)
    @timer
    def native_insert(value):
        arr.append(value)
    native_remove(size//8)
    native_insert(size//8)
    # native_remove(size//2)
    # native_remove(size//1.1)

def benchmark_queue():
    for size in [10**3, 10**4, 10**5, 10**6, 10**7]:
        test_perf(size)
        test_native_perf(size)

if __name__ == '__main__':
    test_perf = testcase(test_perf)
    test_native_perf = testcase(test_native_perf)
    benchmark_queue = testcase(benchmark_queue)
    test_priority_queue = testcase(test_priority_queue)
    test_max_priority_queue = testcase(test_max_priority_queue)
    call_tests([3, 4], verbose=False)
    show_stack()