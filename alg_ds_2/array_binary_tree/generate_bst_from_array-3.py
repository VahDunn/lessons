from generate_bst_from_array import BSTNode, BalancedBST
import pytest


def inorder_keys(root):
    if root is None:
        return []
    return inorder_keys(root.LeftChild) + [root.NodeKey] + inorder_keys(root.RightChild)


def node_by_key(root, key):
    cur = root
    while cur:
        if key < cur.NodeKey:
            cur = cur.LeftChild
        elif key > cur.NodeKey:
            cur = cur.RightChild
        else:
            return cur
    return None


def test_empty_input_builds_empty_tree_and_is_valid_and_balanced():
    t = BalancedBST()
    t.GenerateTree([])
    assert t.Root is None
    assert t.IsBSTValid()
    assert t.IsBalanced()


def test_single_element_tree_levels_valid_and_balanced():
    t = BalancedBST()
    t.GenerateTree([42])
    assert t.Root is not None
    assert t.Root.NodeKey == 42
    assert t.Root.Level == 0
    assert t.IsBSTValid()
    assert t.IsBalanced()
    assert inorder_keys(t.Root) == [42]


def test_generate_tree_from_sorted_range_levels_and_shape():
    data = list(range(1, 8))  # 1..7
    t = BalancedBST()
    t.GenerateTree(data)

    root = t.Root
    assert root is not None
    assert root.NodeKey == 4
    assert root.Level == 0

    left = root.LeftChild
    right = root.RightChild
    assert left and right
    assert left.NodeKey == 2
    assert right.NodeKey == 6
    assert left.Level == right.Level == 1

    # листья уровня 2 (1,3,5,7)
    assert left.LeftChild.NodeKey == 1
    assert left.RightChild.NodeKey == 3
    assert right.LeftChild.NodeKey == 5
    assert right.RightChild.NodeKey == 7
    for leaf in (left.LeftChild, left.RightChild, right.LeftChild, right.RightChild):
        assert leaf.Level == 2
        assert leaf.LeftChild is None and leaf.RightChild is None
    assert t.IsBSTValid()
    assert t.IsBalanced()
    assert inorder_keys(root) == data


@pytest.mark.parametrize("n", [2, 3, 4, 5, 6, 7, 15, 31])
def test_generated_trees_are_bst_and_balanced_for_various_sizes(n):
    t = BalancedBST()
    data = list(range(n))
    t.GenerateTree(data)
    assert t.IsBSTValid()
    assert t.IsBalanced()
    assert inorder_keys(t.Root) == data


def test_is_bst_valid_detects_violation_left_child_equal_to_parent():
    t = BalancedBST()
    t.GenerateTree([1, 2, 3, 4, 5])

    node = t.Root
    assert node is not None and node.LeftChild is not None

    node.LeftChild.NodeKey = node.NodeKey

    assert not t.IsBSTValid()


def test_is_bst_valid_respects_right_child_ge_parent():
    t = BalancedBST()
    t.GenerateTree([1, 2, 3])
    root = t.Root
    dup = BSTNode(root.NodeKey, root)
    dup.LeftChild = None
    dup.RightChild = None
    if root.RightChild is None:
        root.RightChild = dup
    else:
        cur = root.RightChild
        parent = root
        while cur:
            parent = cur
            cur = cur.LeftChild
        parent.LeftChild = dup
        dup.Parent = parent

    assert t.IsBSTValid()

def test_is_balanced_detects_unbalanced_tree():
    t = BalancedBST()
    prev = None
    for i in range(5):
        node = BSTNode(i, prev)
        node.Level = i if prev is None else prev.Level + 1
        if prev is not None:
            prev.RightChild = node
        else:
            t.Root = node
        prev = node

    assert not t.IsBalanced()
    assert t.IsBSTValid()
