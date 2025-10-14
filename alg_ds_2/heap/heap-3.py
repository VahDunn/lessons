import random
import pytest

from heap import Heap

def build_naive(arr, depth):
    h = Heap()
    h.MakeHeap([], depth)
    for x in arr:
        h.Add(x)
    return h

def extract_all(h):
    out = []
    while h.size > 0:
        out.append(h.GetMax())
    return out

@pytest.mark.parametrize("depth", [0, 1, 2, 3, 5])
def test_makeheap_bottom_up_matches_naive(depth):
    arr = [random.randint(-50, 50) for _ in range(57)]
    h1 = Heap()
    h1.MakeHeap(arr, depth)
    out1 = extract_all(h1)

    h2 = build_naive(arr, depth)
    out2 = extract_all(h2)

    assert out1 == out2

def test_capacity_and_overflow():
    h = Heap()
    depth = 2  # capacity = 2^(2+1)-1 = 7
    cap = 2 ** (depth + 1) - 1

    h.MakeHeap([], depth)
    for i in range(cap):
        assert h.Add(i) is True
    assert h.Add(999) is False
    out = extract_all(h)
    assert len(out) == cap
    assert all(out[i] >= out[i+1] for i in range(len(out)-1))

def test_getmax_on_empty():
    h = Heap()
    h.MakeHeap([], depth=0)
    assert h.GetMax() == -1
    assert h.GetMax() == -1

def test_makeheap_truncates_input_to_capacity():
    depth = 1  # cap = 3
    arr = [10, 9, 8, 7, 6]
    h = Heap()
    h.MakeHeap(arr, depth)
    out = extract_all(h)
    assert len(out) == 3
    assert sorted(out, reverse=True) == sorted(arr, reverse=True)[:3]

def test_duplicates_and_negatives():
    depth = 3  # cap=15
    arr = [5, 5, 5, -1, 0, 7, 7, 7, 2, 2, 2, -10, 7, 5, 0]
    h = Heap()
    h.MakeHeap(arr, depth)
    out = extract_all(h)
    assert out == sorted(arr, reverse=True)

def test_interleaved_add_and_getmax():
    h = Heap()
    h.MakeHeap([], depth=2)  # cap=7
    assert h.Add(10) and h.Add(3) and h.Add(8)
    assert h.GetMax() == 10
    assert h.Add(9)
    assert h.GetMax() == 9
    assert h.Add(15)
    assert h.GetMax() == 15
    assert h.Add(1) and h.Add(1) and h.Add(1) and h.Add(1) is True
    assert h.Add(100) is True
    assert h.Add(200) is False
    rest = extract_all(h)
    assert rest == sorted(rest, reverse=True)

@pytest.mark.parametrize("depth", [0, 1, 2, 5])
def test_heap_property_invariant(depth):
    arr = [random.randint(-1000, 1000) for _ in range(100)]
    h = Heap()
    h.MakeHeap(arr, depth)

    def check_invariant(heap: Heap):
        for i in range(heap.size):
            l, r = 2*i + 1, 2*i + 2
            if l < heap.size:
                assert heap.HeapArray[i] >= heap.HeapArray[l]
            if r < heap.size:
                assert heap.HeapArray[i] >= heap.HeapArray[r]

    check_invariant(h)

    for x in [9999, -5000, 0, 123, 123]:
        h.Add(x)
        check_invariant(h)
