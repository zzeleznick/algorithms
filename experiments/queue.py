from collections import deque
from bisect import bisect_left, insort_left
# Internal python modules
import init
from TimeUtils import *

def queue_insert(q, value):
    new_idx = bisect_left(q, value)
    length = len(q)
    if new_idx < length // 2:
        q.rotate(-new_idx)
        q.appendleft(value)
        q.rotate(new_idx)
    else:
        q.rotate(length-new_idx)
        q.append(value)
        q.rotate(-(length-new_idx))

def queue_remove(q, value):
    idx = bisect_left(q, value)
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

@testcase
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

@testcase
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

@testcase
def benchmark_queue():
    for size in [10**3, 10**4, 10**5, 10**6, 10**7]:
        test_perf(size)
        test_native_perf(size)

if __name__ == '__main__':
    call_tests([2], verbose=False)
    show_stack()