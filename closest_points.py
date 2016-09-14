from __future__ import print_function
import time
import numpy as np
from scipy.spatial.distance import cdist
# from scipy.spatial.distance import euclidean
from bisect import bisect_left
import argparse

zprint = globals()['__builtins__'].print

def brute_force(pts):
    assert pts.shape[0] >= 2, "Must input at least 2 points not %s" % pts.shape[0]
    best = (pts[0], pts[1])
    min_dist = cdist(pts[0:1], pts[1:2]).ravel()
    for i in xrange(0, pts.shape[0]-1):
        idx = (i+1) + cdist(pts[i:i+1], pts[i+1:]).argmin()
        dist = cdist(pts[i:i+1], pts[idx:idx+1]).ravel()
        if dist < min_dist:
            min_dist = dist
            best = (pts[i], pts[idx])
    return min_dist, best


def euc(u,v):
    dist = np.sqrt(np.sum((u-v)**2, 1))
    idx = dist.argmin()
    return dist[idx], (u[idx], v[idx])

def middle_call(gamma, tau, arry_potter):
    best = None
    # print("Gamma: %s, Tau: %s, LHS size: %s, RHS size: %s" % (gamma, tau, lhs.shape[0], rhs.shape[0]) )
    selected_indices = np.zeros(arry_potter.shape[0], dtype=np.bool_)
    for (i, p) in enumerate(arry_potter['x']):
        if abs(p - gamma) < tau:
            selected_indices[i] = True
    comparables = arry_potter[selected_indices]
    size = comparables.shape[0]
    for (i,p) in enumerate(comparables):
        low = bisect_left(comparables['y'], p['y']-tau)
        hi = bisect_left(comparables['y'], p['y']+tau)
        selected = np.array(zip(comparables[low:hi]['x'], comparables[low:hi]['y']))
        v = np.array([p['x'], p['y']])
        vv = np.repeat(v,[selected.shape[0]]).reshape(2,selected.shape[0]).T
        """
        print("Comparing %s points to %s" % (selected.shape[0], v) )
        if selected.shape[0] > 0:
            print("%s" % selected)
        """
        try:
            dist, pair = euc(vv, selected)
        except ValueError as e:
            # no points in bounding box
            pass
        else:
            best = pair if dist <= tau else best
            tau = min(tau, dist)
    return tau, best

def closest_points_optimized(pts, arry_potter=[], gamma=None):
    if pts.shape[0] <= 2**8:
        if pts.shape[0] < 2:
            return 10**8, None
        if gamma == None:
            return brute_force(pts)
        else:
            pts = np.array(zip(pts['x'], pts['y']))
            return brute_force(pts)
    if gamma == None:
        dtype = np.dtype([('x', float), ('y', float)])
        arr = np.sort(np.array(zip(pts.ravel()[::2], pts.ravel()[1::2]), dtype), order='x')
        arry_potter = np.sort(arr, order='y')
        gamma = np.median(arr['x'])
        return closest_points_optimized(arr, arry_potter, gamma)
    else:
        arr = pts
        lxarr = arr[:arr.shape[0]//2]
        rxarr = arr[arr.shape[0]//2:]
        gamma = arr[-1]['x']
        selected_indices = np.zeros(arry_potter.shape[0], dtype=np.bool_)
        for (i, pt) in enumerate(arry_potter['x']):
            if pt <= gamma:
                selected_indices[i] = True
        lhs = arry_potter[selected_indices]
        rhs = arry_potter[np.logical_not(selected_indices)]
        ltau, lbest = closest_points_optimized(lxarr, lhs, gamma)
        rtau, rbest = closest_points_optimized(rxarr, rhs, gamma)
        tau = min(ltau, rtau)
        best = lbest if ltau == tau else rbest
        mtau, mbest = middle_call(gamma, tau, arry_potter)
        best = best if tau <= mtau else mbest
        tau = min(tau, mtau)
        return tau, best

def closest_points(pts, naive=True):
    if naive:
        return brute_force(pts)
    return closest_points_optimized(pts)

def benchmark(naive=True, sizes=[]):
    globals()['__builtins__'].print = lambda *args, **kws: 42
    if not sizes:
        sizes = [10, 10**2, 10**3, 5*10**3, 10**4, 2*10**4, 4*10**4]
    np.random.seed(np.arange(len(sizes)*2))
    zprint("Testing method %s" % ("brute_force" if naive else "optimized"))
    for (i, s) in enumerate(sizes):
        start = time.time()
        points = np.round(np.random.random((s,2)) * s*20 - s*10)
        closest_points(points, naive)
        zprint("Iteration %s | Size %s | %0.3f ms" % (i,s, 1000 * (time.time()-start)) )

def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-b', "--benchmark", help="benchmark mode", action="store_true")
    group.add_argument('-o', "--optimized", help="optimized mode", action="store_true")
    args = parser.parse_args()
    if args.benchmark:
        benchmark()
        benchmark(naive=False)
    else:
        size = 2**6 * 10**2
        np.random.seed(np.arange(size*2)+2)
        points = np.round(np.random.random((size,2)) * size*10 - size*5)
        print("Selected %s points:\n%s" % (size, points) )
        if args.optimized:
            min_dist, best = closest_points(points, naive=False)
        else:
            min_dist, best = closest_points(points)
        print("Mininum distance:\n%s" % min_dist)
        print("Closest points:\n(%s, %s)" % (best[0], best[1]))

if __name__ == '__main__':
    main()