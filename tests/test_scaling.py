import pytest
from vector_tile_base.engine import scaling_calculation, zig_zag_encode_64
from random import random, uniform

def encode_to_int(dlist, sF, base, offset):
    return [int(round(sF*(d-base) - offset)) for d in dlist]

def decode_to_float(ilist, sR, base, offset):
    return [sR*(i + offset) + base for i in ilist]

def delta_encode(ilist, offset):
    prev = offset
    out = []
    for i in ilist:
        out.append(i - prev)
        prev = i
    return out

def find_diff(dlist, new_dlist):
    return [abs(dlist[i] - new_dlist[i]) for i in range(len(dlist))]

def calculate_size(some_data):
    size = 0
    for v in some_data:
        if isinstance(v, float):
            size = size + 8
        else:
            n = zig_zag_encode_64(v) >> 7
            size = size + 1
            while n != 0:
                n = n >> 7
                size = size + 1
    return size

def test_scaling_range():
    minf = 0.0
    maxf = 10.0**8
    dlist = [uniform(-maxf, maxf) for x in range(1000)]
    precision = 10**-6
    out = scaling_calculation(precision, minf, maxf)
    ilist = encode_to_int(dlist, out['sF'], out['base'], 0)
    ilist_delta = delta_encode(ilist, 0)
    new_dlist = decode_to_float(ilist, out['sR'], out['base'], 0)
    ilist_sorted = ilist
    ilist_sorted.sort()
    ilist_delta_sorted = delta_encode(ilist_sorted, 0)

    dlist_size = calculate_size(dlist)
    ilist_size = calculate_size(ilist)
    ilist_delta_size = calculate_size(ilist_delta)
    ilist_delta_sorted_size = calculate_size(ilist_delta_sorted)
    assert dlist_size > ilist_size

    assert ilist_size > ilist_delta_sorted_size
    assert ilist_delta_size > ilist_delta_sorted_size

    max_diff = max(find_diff(dlist, new_dlist))
    assert max_diff < precision

def test_bad_scaling_values():
    with pytest.raises(Exception):
        scaling_calculation(-1.0, 0.0, 10.0)
    with pytest.raises(Exception):
        scaling_calculation(100.0, 0.0, 10.0)
