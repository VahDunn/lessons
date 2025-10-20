import pytest
from simple_tree import SimpleTree, SimpleTreeNode


@pytest.fixture
def sample_tree():
    root = SimpleTreeNode(1, None)
    tree = SimpleTree(root)

    n2 = SimpleTreeNode(2, root)
    n3 = SimpleTreeNode(3, root)
    n4 = SimpleTreeNode(4, root)
    n5 = SimpleTreeNode(5, n4)

    tree.AddChild(root, n2)
    tree.AddChild(root, n3)
    tree.AddChild(root, n4)
    tree.AddChild(n4, n5)

    return tree, root, n2, n3, n4, n5


@pytest.fixture
def empty_tree():
    return SimpleTree(None)


@pytest.fixture
def even_tree_example():
    # Классический пример из задачи «Even Tree»
    # Рёбра по значениям:
    # 1-2, 1-3, 1-6, 2-5, 2-7, 3-4, 4-8, 4-9, 6-10
    n1 = SimpleTreeNode(1, None)
    t = SimpleTree(n1)

    n2 = SimpleTreeNode(2, n1)
    n3 = SimpleTreeNode(3, n1)
    n6 = SimpleTreeNode(6, n1)
    n5 = SimpleTreeNode(5, n2)
    n7 = SimpleTreeNode(7, n2)
    n4 = SimpleTreeNode(4, n3)
    n8 = SimpleTreeNode(8, n4)
    n9 = SimpleTreeNode(9, n4)
    n10 = SimpleTreeNode(10, n6)

    t.AddChild(n1, n2)
    t.AddChild(n1, n3)
    t.AddChild(n1, n6)
    t.AddChild(n2, n5)
    t.AddChild(n2, n7)
    t.AddChild(n3, n4)
    t.AddChild(n4, n8)
    t.AddChild(n4, n9)
    t.AddChild(n6, n10)

    return t, n1, n2, n3, n4, n5, n6, n7, n8, n9, n10


def pairs_to_values(pairs):
    it = iter(pairs)
    return [(a.NodeValue, b.NodeValue) for a, b in zip(it, it)]


def test_get_all_nodes_and_count(sample_tree):
    tree, root, n2, n3, n4, n5 = sample_tree
    nodes = tree.GetAllNodes()
    assert nodes[0] is root
    assert set(nodes) == {root, n2, n3, n4, n5}
    assert tree.Count() == 5


def test_leaf_count_initial(sample_tree):
    tree, *_ = sample_tree
    assert tree.LeafCount() == 3


def test_find_nodes_by_value(sample_tree):
    tree, _, _, _, n4, _ = sample_tree
    r = tree.FindNodesByValue(4)
    assert len(r) == 1 and r[0] is n4
    assert tree.FindNodesByValue(42) == []


def test_find_nodes_by_value_multiple(sample_tree):
    tree, root, *_ = sample_tree
    x1 = SimpleTreeNode(4, None)
    x2 = SimpleTreeNode(4, None)
    tree.AddChild(root, x1)
    tree.AddChild(root, x2)
    r = tree.FindNodesByValue(4)
    assert len(r) == 3
    assert {n.NodeValue for n in r} == {4}


def test_add_child_increases_count_and_sets_parent(sample_tree):
    tree, _, _, n3, _, _ = sample_tree
    n6 = SimpleTreeNode(6, None)
    tree.AddChild(n3, n6)
    assert n6.Parent is n3
    assert n6 in n3.Children
    assert tree.Count() == 6
    assert tree.LeafCount() == 3


def test_add_child_ignores_none_parent(sample_tree):
    tree, *_ = sample_tree
    before = tree.Count()
    n = SimpleTreeNode(99, None)
    tree.AddChild(None, n)
    assert tree.Count() == before
    assert n.Parent is None
    assert n.Children == []


def test_delete_node_detaches_subtree(sample_tree):
    tree, root, n2, n3, n4, n5 = sample_tree
    tree.DeleteNode(n4)
    assert n4.Parent is None
    assert n4 not in root.Children
    nodes = set(tree.GetAllNodes())
    assert nodes == {root, n2, n3}
    assert tree.Count() == 3
    assert tree.LeafCount() == 2


def test_delete_root_clears_tree(sample_tree):
    tree, root, *_ = sample_tree
    tree.DeleteNode(root)
    assert tree.Root is None
    assert tree.GetAllNodes() == []
    assert tree.Count() == 0
    assert tree.LeafCount() == 0


def test_enum_nodes_levels_sets_correct_levels(sample_tree):
    tree, root, n2, n3, n4, n5 = sample_tree
    tree.enum_nodes_levels()
    assert root.NodeLevel == 0
    assert n2.NodeLevel == 1
    assert n3.NodeLevel == 1
    assert n4.NodeLevel == 1
    assert n5.NodeLevel == 2


def test_move_node_reparents_and_updates_children_collections(sample_tree):
    tree, _, _, n3, n4, n5 = sample_tree
    assert n5.Parent is n4
    tree.MoveNode(n5, n3)
    assert n5.Parent is n3
    assert n5 not in n4.Children
    assert n5 in n3.Children
    assert tree.LeafCount() == 3


def test_move_node_prevent_cycle(sample_tree):
    tree, root, n2, n3, n4, n5 = sample_tree
    before_children_root = set(root.Children)
    before_children_n4 = set(n4.Children)
    tree.MoveNode(n4, n5)
    assert n4.Parent is root
    assert set(root.Children) == before_children_root
    assert set(n4.Children) == before_children_n4

def test_move_node_allowed_between_branches(sample_tree):
    tree, root, n2, n3, n4, n5 = sample_tree
    assert n3.Parent is root
    assert n5.Parent is n4
    tree.MoveNode(n3, n5)
    assert n3.Parent is n5
    assert n3 in n5.Children
    assert n3 not in root.Children


def test_get_all_nodes_with_empty_tree(empty_tree):
    assert empty_tree.GetAllNodes() == []
    assert empty_tree.Count() == 0
    assert empty_tree.LeafCount() == 0
    assert empty_tree.FindNodesByValue(1) == []


def test_even_trees_on_odd_total_returns_empty(sample_tree):
    tree, *_ = sample_tree
    assert tree.Count() % 2 == 1
    assert tree.EvenTrees() == []


def test_even_trees_classic_example(even_tree_example):
    t, n1, n2, n3, n4, n5, n6, n7, n8, n9, n10 = even_tree_example
    assert t.Count() == 10
    cuts = t.EvenTrees()
    pv = pairs_to_values(cuts)
    assert set(pv) == {(1, 3), (1, 6)}
    assert len(pv) == 2
    t.enum_nodes_levels()
    assert n1.NodeLevel == 0
    assert {n2.NodeLevel, n3.NodeLevel, n6.NodeLevel} == {1}
    assert n4.NodeLevel == 2
