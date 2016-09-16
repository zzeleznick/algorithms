from collections import deque
from bisect import bisect_left, insort_left


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