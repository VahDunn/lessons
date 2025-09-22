import pytest
from .simple_tree import SimpleTree, SimpleTreeNode



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



def test_get_all_nodes_and_count(sample_tree):
    tree, root, n2, n3, n4, n5 = sample_tree
    nodes = tree.GetAllNodes()
    assert nodes[0] is root
    assert set(nodes) == {root, n2, n3, n4, n5}
    assert tree.Count() == 5


def test_leaf_count_initial(sample_tree):
    tree, root, n2, n3, n4, n5 = sample_tree
    assert tree.LeafCount() == 3


def test_find_nodes_by_value(sample_tree):
    tree, root, n2, n3, n4, n5 = sample_tree
    r = tree.FindNodesByValue(4)
    assert len(r) == 1 and r[0] is n4
    assert tree.FindNodesByValue(42) == []


def test_add_child_increases_count_and_sets_parent(sample_tree):
    tree, root, n2, n3, n4, n5 = sample_tree
    n6 = SimpleTreeNode(6, None)
    tree.AddChild(n3, n6)

    assert n6.Parent is n3
    assert n6 in n3.Children
    assert tree.Count() == 6
    assert tree.LeafCount() == 3


def test_delete_node_detaches_subtree(sample_tree):
    tree, root, n2, n3, n4, n5 = sample_tree
    tree.DeleteNode(n4)

    assert n4.Parent is None
    assert n4 not in root.Children
    nodes = set(tree.GetAllNodes())
    assert nodes == {root, n2, n3}
    assert tree.Count() == 3
    assert tree.LeafCount() == 2


def test_enum_nodes_levels_sets_correct_levels(sample_tree):
    tree, root, n2, n3, n4, n5 = sample_tree
    tree.enum_nodes_levels()

    assert root.NodeLevel == 0
    assert n2.NodeLevel == 1
    assert n3.NodeLevel == 1
    assert n4.NodeLevel == 1
    assert n5.NodeLevel == 2


def test_move_node_reparents_and_updates_children_collections(sample_tree):
    tree, root, n2, n3, n4, n5 = sample_tree
    old_parent = n5.Parent
    assert old_parent is n4

    tree.MoveNode(n5, n3)
    assert n5.Parent is n3, "Parent должен указывать на нового родителя"
    assert n5 not in n4.Children, "Узел должен быть удалён из детей старого родителя"
    assert n5 in n3.Children, "Узел должен быть добавлен к детям нового родителя"
    assert tree.LeafCount() == 3
