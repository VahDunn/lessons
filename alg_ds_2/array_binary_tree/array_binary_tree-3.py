import pytest

from .array_binary_tree import aBST, GenerateBBSTArray


def fill_tree_with_bbst(tree: aBST, values):
    order = GenerateBBSTArray(values)
    for v in order:
        tree.AddKey(v)
    return order


def test_init_negative_depth_raises():
    with pytest.raises(ValueError):
        aBST(-1)


def test_init_depth_zero_tree_size_is_one():
    t = aBST(0)
    assert len(t.Tree) == 1
    assert t.Tree == [None]


def test_find_on_empty_tree_returns_zero_for_root_slot():
    t = aBST(2)
    assert t.FindKeyIndex(10) == 0


def test_add_and_find_single_key_at_root():
    t = aBST(0)
    assert t.AddKey(42) == 0
    assert t.FindKeyIndex(42) == 0


def test_add_existing_key_returns_same_index():
    t = aBST(2)
    t.AddKey(10)
    assert t.AddKey(10) == 0
    assert t.FindKeyIndex(10) == 0


def test_add_navigates_left_and_right():
    t = aBST(2)
    t.AddKey(8)
    t.AddKey(4)
    t.AddKey(12)
    assert t.Tree[0] == 8
    assert t.Tree[1] == 4
    assert t.Tree[2] == 12
    assert t.FindKeyIndex(4) == 1
    assert t.FindKeyIndex(12) == 2


def test_add_until_full_then_returns_minus_one():
    t = aBST(1)
    assert t.AddKey(2) == 0
    assert t.AddKey(1) == 1
    assert t.AddKey(3) == 2
    assert t.AddKey(0) == -1


def test_generate_bbst_array_and_fill_minimal_depth_matches_array():
    values = [1, 2, 3, 4, 5, 6, 7]
    order = GenerateBBSTArray(values)
    t = aBST(depth=2)
    filled_order = fill_tree_with_bbst(t, values)
    assert filled_order == order
    assert t.Tree == order
    for idx, key in enumerate(order):
        assert t.FindKeyIndex(key) == idx


def test_find_missing_key_returns_negative_insertion_index_in_larger_tree():
    values = [1, 2, 3, 4, 5, 6, 7]
    t = aBST(depth=3)
    fill_tree_with_bbst(t, values)

    assert t.FindKeyIndex(0) == -7


def test_find_none_returns_none():
    t = aBST(2)
    assert t.FindKeyIndex(None) is None
