import pytest

@pytest.fixture
def bst_empty():
    from .binary_search_tree import BST  # либо замени на свой модуль
    return BST(None)

@pytest.fixture
def bst_balanced():
    from .binary_search_tree import BST
    bst = BST(None)
    for k in [8, 4, 12, 2, 6, 10, 14]:
        bst.AddKeyValue(k, str(k))
    return bst

@pytest.fixture
def bst_unbalanced_right():
    from .binary_search_tree import BST
    bst = BST(None)
    for k in [1, 2, 3, 4, 5]:
        bst.AddKeyValue(k, str(k))
    return bst

@pytest.fixture
def bst_unbalanced_left():
    from .binary_search_tree import BST
    bst = BST(None)
    for k in [5, 4, 3, 2, 1]:
        bst.AddKeyValue(k, str(k))
    return bst


def keys(seq):
    return [n.NodeKey for n in seq]


def test_wide_empty(bst_empty):
    assert keys(bst_empty.WideAllNodes()) == []


def test_wide_balanced(bst_balanced):
    assert keys(bst_balanced.WideAllNodes()) == [8, 4, 12, 2, 6, 10, 14]


def test_deep_inorder_balanced(bst_balanced):
    assert keys(bst_balanced.DeepAllNodes(0)) == [2, 4, 6, 8, 10, 12, 14]


def test_deep_postorder_balanced(bst_balanced):
    assert keys(bst_balanced.DeepAllNodes(1)) == [2, 6, 4, 10, 14, 12, 8]


def test_deep_preorder_balanced(bst_balanced):
    assert keys(bst_balanced.DeepAllNodes(2)) == [8, 4, 2, 6, 12, 10, 14]


def test_unbalanced_right_traversals(bst_unbalanced_right):
    assert keys(bst_unbalanced_right.WideAllNodes()) == [1, 2, 3, 4, 5]
    assert keys(bst_unbalanced_right.DeepAllNodes(0)) == [1, 2, 3, 4, 5]  # in-order
    assert keys(bst_unbalanced_right.DeepAllNodes(1)) == [5, 4, 3, 2, 1]  # post-order
    assert keys(bst_unbalanced_right.DeepAllNodes(2)) == [1, 2, 3, 4, 5]  # pre-order


def test_unbalanced_left_traversals(bst_unbalanced_left):
    assert keys(bst_unbalanced_left.WideAllNodes()) == [5, 4, 3, 2, 1]
    assert keys(bst_unbalanced_left.DeepAllNodes(0)) == [1, 2, 3, 4, 5]   # in-order
    assert keys(bst_unbalanced_left.DeepAllNodes(1)) == [1, 2, 3, 4, 5]   # post-order
    assert keys(bst_unbalanced_left.DeepAllNodes(2)) == [5, 4, 3, 2, 1]   # pre-order


def test_returns_nodes_not_keys(bst_balanced):
    res = bst_balanced.WideAllNodes()
    from .binary_search_tree import BSTNode
    assert all(isinstance(n, BSTNode) for n in res)


def test_traversals_do_not_modify_tree(bst_balanced):
    before = bst_balanced.Count()
    _ = bst_balanced.WideAllNodes()
    _ = bst_balanced.DeepAllNodes(0)
    _ = bst_balanced.DeepAllNodes(1)
    _ = bst_balanced.DeepAllNodes(2)
    after = bst_balanced.Count()
    assert before == after


def test_deep_invalid_param_raises(bst_balanced):
    with pytest.raises(ValueError):
        bst_balanced.DeepAllNodes(999)
