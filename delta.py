from __future__ import print_function
import time
import math
import numpy as np
import argparse

FFT = np.fft.fft
IFFT = np.fft.ifft
zprint = globals()['__builtins__'].print

def pad(x, n):
    """Pads an 1-D vector x until its length is n"""
    return np.pad(x, (0,n-x.size), mode='constant', constant_values=0)

def flip(x):
    """Converts 0's from a binary 1-D vector to -1's"""
    return 2*x - 1

def calc_delta(u,v):
    """Finds the number of different bits at each index between two binary vectors"""
    flat = lambda x: len(x.shape) == 1
    assert flat(u) and flat(v), "Vectors must be 1-D not %s and %s" % (u.shape, v.shape)
    if v.size > u.size: # guarantee u >= v
        u,v = v,u
    u,v = flip(u), flip(v)
    big_size = u.size
    small_size = v.size
    # now we need to get the minimum size greater than u's size
    # that's a power of 2 so we can fit our values
    padded_size = 2 ** (int((math.log(u.size,2))) + 1)
    # for magic multiplication we need to flip our big vector and pad to fill for fft
    # flipping is required for easy indexing the result
    u = pad(np.flipud(u), padded_size)
    v = pad(v, padded_size)
    print("Padded and aligned Vectors:\nU: %s\nV: %s" % (u,v))
    uu, vv = FFT(u), FFT(v)
    # we flip our result again to line up with the original indices
    result = np.flipud(np.real(IFFT(uu*vv)))
    # print("Raw results including garbage coefficients:\n%s" % np.round(result))
    # now we throw away invalid coefficients
    valid = result[padded_size-big_size:-small_size+1]
    # delta = ( virus length - coefficients ) / 2
    # print(np.round((small_size - result ) / 2))
    delta = np.abs(np.round((small_size - valid ) / 2))
    print("Delta:\n%s" % delta)
    return delta

def brute_force(u,v):
    flat = lambda x: len(x.shape) == 1
    assert flat(u) and flat(v), "Vectors must be 1-D not %s and %s" % (u.shape, v.shape)
    # u, v = u.astype(np.bool_), v.astype(np.bool_)
    if v.size > u.size: # guarantee u >= v
        u,v = v,u
    comparisons = u.size-v.size+1
    # '''
    delta = np.zeros(comparisons)
    for i in xrange(comparisons):
        delta[i] = np.sum(np.mod(np.add(u[i:i+v.size],v), 2))
        # delta[i] = np.sum(np.logical_xor(u[i:i+v.size],v))
    '''
    # strided source: http://stackoverflow.com/questions/2485669/consecutive-overlapping-subsets-of-array-numpy-python
    as_strided = np.lib.stride_tricks.as_strided
    strides = as_strided(u, (comparisons, v.size), (1,1))
    delta = np.sum(np.logical_xor(strides, v),1)
    '''
    print("Delta:\n%s" % delta)
    return delta

def generate_rand_strings(size=100):
    u = (np.random.random(size) >= 0.5) # * 1
    v = (np.random.random(size//2) >= 0.5) # * 1
    # this will allow for m-n+1 delta comparisons,
    # which suits our needs quite well
    return (u,v)

def benchmark(naive=True, sizes=[]):
    globals()['__builtins__'].print = lambda *args, **kws: 42
    if not sizes:
        sizes = [10, 10**2, 10**3, 10**4, 5*10**4, 10**5, 10**6, 5*10**6, 5*10**6]
    np.random.seed(np.arange(len(sizes)*2))
    zprint("Testing method %s" % ("brute_force" if naive else "fft"))
    for (i, s) in enumerate(sizes):
        start = time.time()
        if naive:
            if s >= 10**5:
                # Don't kill your computer!
                continue
            delta = brute_force(*generate_rand_strings(s))
        else:
            delta = calc_delta(*generate_rand_strings(s))
        zprint("Iteration %s | Size %s | %0.3f ms" % (i,s, 1000 * (time.time()-start)) )

def test(naive=True):
    u = np.array([1,0,0,1,0,1,1,0,0,1])
    # u = np.array([1,0,0,1,1])
    v = np.array([0,0,1])
    # v = np.array([1,0,0,1,0,1,1,0,0])
    print("U: %s" % u)
    print("V: %s" % v)
    if naive:
        delta = brute_force(u, v)
    else:
        delta = calc_delta(u, v)
    return delta

def get_user_input(name, default):
    vector = raw_input('Enter a space seperated bit-string (the %s)\n' % name).strip().split()
    try:
        vector = np.array(vector, dtype=int)
    except Exception:
        vector = default
        print("Error with input, using default:\n%s" % vector)
    if not vector.size:
        vector = default
        print("No input entered, using default:\n%s" % vector)
    return vector

def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-b', "--benchmark", help="benchmark mode", action="store_true")
    group.add_argument('-f', "--fft", help="fft mode", action="store_true")
    args = parser.parse_args()
    if args.benchmark:
        sizes = [10, 10**2, 10**3, 10**4, 10**5, 10**6, 5*10**6, 5*10**6]
        np.random.seed(np.arange(len(sizes)*4))
        benchmark(naive=True)
        benchmark(naive=False)
    else:
        naive = not args.fft
        u_default, v_default = np.array([1,0,0,1,0,1,1,0,0,1]), np.array([0,0,1])
        u = get_user_input("RAM", u_default)
        v = get_user_input("virus", v_default)
        if naive:
            print("Using brute force method")
            brute_force(u, v)
        else:
            print("Using fft method")
            calc_delta(u, v)

if __name__ == '__main__':
    main()