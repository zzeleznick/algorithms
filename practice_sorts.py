import argparse
import math
from collections import deque
from random import shuffle
from itertools import chain
import random
import bisect
import time
from functools import wraps
from heapq import merge

def timer(func):
    @wraps(func) # meta-data capture
    def wrapper(*args, **kwargs):
        nums = None
        if args and type(args[0]) == list:
            nums = len(args[0])
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print("Called %s with %s args and took %0.3f ms" % (func.__name__, nums, 1000*(end-start)))
        return result
    return wrapper

def bubble_sort(arr):
    """N iterations, making N^2 comparisons.
    Swap adjacent numbers so that right > left
    Guaranteed to have the k-th largest number at the k-th spot after k iterations
    1. Start at the beginning of the list
    2. Move towards the end of the list, carrying larger numbers towards the end
    3. Repeat N times, growing the sorted list right to left.
    """
    # limit = (lambda x: x  * (x+1) / 2) (len(arr))
    for pushed in range(len(arr)):
        inorder = True # optimistic
        for i in range(1, len(arr) - pushed):
            if arr[i-1] >= arr[i]:
                arr[i-1], arr[i] = arr[i], arr[i-1]
                inorder = False
        if inorder:
            break
    print "Finished after iteration %s of %s" % (pushed, len(arr)-1)
    return arr

def insertion_sort(arr):
    """ """
    return insertion_sort_optimized(arr)
    for i in range(1, len(arr)):
        val = arr[i]
        if val >= arr[i-1]:
            continue
        pos = bisect.bisect_left(arr, val, hi=i)
        arr = list(chain(arr[:pos], [val], arr[pos:i], arr[i+1:]))
    return arr

def insertion_sort_alt(arr):
    """ """
    # much slower than regular
    arr = deque(arr)
    pop = lambda count: [ arr.popleft() for _ in range(count)]
    for i in range(1, len(arr)):
        left = pop(i)
        val = arr.popleft()
        bisect.insort_left(left, val)
        arr.extendleft(reversed(left))
    return list(arr)

def insertion_sort_optimized(arr, start=1):
    """ """
    arr = deque(arr)
    for i in range(start, len(arr)):
        val = arr[i]
        if val >= arr[i-1]:
            continue
        if i <= len(arr) // 2:
            arr.rotate(-i)
            arr.popleft()
            offset = bisect.bisect_left(arr, val, lo=len(arr)-i)
            if len(arr) - offset < offset:
                arr.rotate(len(arr) - offset)
                arr.append(val)
                arr.rotate(i - (len(arr) - offset) + 2)
            else:
                arr.rotate(-offset)
                arr.appendleft(val)
                arr.rotate(i + offset + 1)
        else:
            arr.rotate(len(arr)-i-1)
            arr.pop()
            offset = bisect.bisect_left(arr, val, lo=len(arr)-i)
            if len(arr) - offset < offset:
                arr.rotate(len(arr) - offset)
                arr.appendleft(val)
                arr.rotate(-(len(arr)-i-1) - (len(arr)-offset))
            else:
                arr.rotate(-offset)
                arr.append(val)
                arr.rotate(-(len(arr)-i-1) + offset + 1)
    return list(arr)

def selection_sort(arr):
    """N iterations, making N^2 comparisons.
    Place the smallest number from the unsorted array in the sorted array.
    Sorted array grows left to right.
    1. Pick the first number from the unsorted array.
    2. Place the smallest number of the unsorted array at the end of the sorted array.
    3. Repeat N times.
    """
    for i in range(len(arr)):
        for j in range(i, len(arr)):
            if arr[i] >= arr[j] and i != j:
                arr[i], arr[j] = arr[j], arr[i]
    return arr

def inner_merge(run, run_length):
    # Best Inner Merge
    left, right = run[:run_length//2], run[run_length//2:]
    [ bisect.insort_left(left, v) for v in right ]
    return left

def merge_sort(arr):
    """Split and insert sort
    bottom-up implementation"""
    # 2 * n/2, 4 * n/4, ... n/2 * 2
    # 0:2, 2:4; 0:4, 4:8 ...
    iterations = int(math.log(len(arr), 2))
    for k in range(iterations):
        run_length = 2**(k+1)
        run_count = len(arr) // run_length # last run will have extra
        # print "i: %s, length: %s, count: %s" % (k, run_length, run_count)
        runs = [ arr[j*run_length:(j+1)*run_length] for j in range(run_count) ]
        runs[-1].extend(arr[run_count*run_length:])
        # """
        arr = []
        for i, run in enumerate(runs):
             arr.extend(inner_merge(run, run_length))
             # arr.extend(insertion_sort_optimized(run, run_length//2))
        # """
        # arr = list(chain(*[ inner_merge(run, run_length) for run in runs ]))
    return arr

def merge_sort_alt(m):
    """Python built-in"""
    if len(m) <= 1:
        return m
    middle = len(m) // 2
    left = merge_sort(m[:middle])
    right = merge_sort(m[middle:])
    return list(merge(left, right))

@timer
def quick_sort(arr):
    """Pick a pivot to act as a comparator
    partition a left and right side and sort each
    using the same method"""
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
            elif val == pivot:
                pivots.append(pivot)
            else:
                right.append(val)
        return list(chain(qs_inner(left), pivots, qs_inner(right)))
    return qs_inner(arr)

def bucket_hybrid_sort(arr):
    """sorts natural numbers """
    max_idx = 0
    buckets = {}
    for v in arr:
        if v < 1:
            raise Exception("Only sorts natural numbers")
        idx = int(math.log(v,2))
        if idx > max_idx:
            max_idx = idx
        buckets[idx] = [v] if not buckets.get(idx) else list(chain(buckets[idx], [v]))
    out = []
    [ out.extend(sorted(buckets[i])) for i in range(max_idx+1) if buckets.get(i) ]
    return out

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

def benchmark(fnc):
    rand_arr_benchmark(fnc, sizes=[100, 1000, 10000])()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--bubble", action="store_true", help="bubble sort")
    parser.add_argument("-s", "--selection", action="store_true", help="selection sort")
    parser.add_argument("-i", "--insertion", action="store_true", help="insertion sort")
    parser.add_argument("-m", "--merge", action="store_true", help="merge sort")
    parser.add_argument("-q", "--quicksort", action="store_true", help="quick sort")
    parser.add_argument("-bh", "--hybrid", action="store_true", help="hybrid sort")
    return parser.parse_args()

def main():
    args = parse_args()
    arr = [random.randrange(1,100) for i in range(10**3)]
    # arr = range(10)
    # random.shuffle(arr)
    print len(arr)
    if args.bubble:
        sorted_arr = bubble_sort(arr)
    elif args.selection:
        sorted_arr = selection_sort(arr)
    elif args.insertion:
        sorted_arr = insertion_sort(arr)
    elif args.merge:
        sorted_arr = merge_sort(arr)
        # sorted_arr = merge_sort_alt(arr)
    elif args.quicksort:
        # sorted_arr = quick_sort(arr)
        benchmark(quick_sort)
        exit()
    elif args.hybrid:
        sorted_arr = bucket_hybrid_sort(arr)
    else:
        sorted_arr = sorted(arr)
    assert sorted(arr) == sorted_arr, "Failed Sort\n: %s" % sorted_arr

if __name__ == '__main__':
    main()