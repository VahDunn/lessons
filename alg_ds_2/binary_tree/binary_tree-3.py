# test_bst.py
import pytest

# импортируй BST, BSTNode из своего файла, например:
# from bst import BST, BSTNode
from .binary_tree import BST, BSTNode  # <-- поменяй на реальный импорт, если нужно


# --------- вспомогалки ----------
def build_bst(pairs):
    """
    pairs: iterable[(key, value)]
    """
    tree = BST(None)
    for k, v in pairs:
        tree.AddKeyValue(k, v)
    return tree


def keys_inorder(node):
    if node is None:
        return []
    return keys_inorder(node.LeftChild) + [node.NodeKey] + keys_inorder(node.RightChild)


def test_empty_tree_find_returns_parent_none_and_flags():
    t = BST(None)
    res = t.FindNodeByKey(10)
    assert res.Node is None
    assert res.NodeHasKey is False
    assert res.ToLeft in (True, False)  # допустимо любое, родителя нет


def test_add_first_node_sets_root_and_returns_node():
    t = BST(None)
    added = t.AddKeyValue(5, "five")
    assert added is t.Root
    assert t.Root.NodeKey == 5
    assert t.Root.NodeValue == "five"
    assert t.Root.Parent is None
    assert t.Count() == 1


def test_add_and_find_existing_and_nonexisting():
    t = build_bst([(5, "a"), (2, "b"), (8, "c"), (1, "d"), (3, "e")])
    # существующий
    res = t.FindNodeByKey(3)
    assert res.NodeHasKey is True
    assert res.Node.NodeKey == 3
    # несуществующий — вернётся родитель и направление
    res2 = t.FindNodeByKey(4)
    assert res2.NodeHasKey is False
    assert res2.Node.NodeKey == 3     # место вставки справа от 3
    assert res2.ToLeft is False


def test_inorder_is_sorted_after_inserts():
    t = build_bst([(5, "a"), (2, "b"), (8, "c"), (1, "d"), (3, "e"), (7, "f"), (9, "g")])
    assert keys_inorder(t.Root) == [1, 2, 3, 5, 7, 8, 9]
    assert t.Count() == 7


def test_finminmax_on_root_min_and_max():
    t = build_bst([(5, "a"), (2, "b"), (8, "c"), (1, "d"), (3, "e"), (7, "f"), (9, "g")])
    mn = t.FinMinMax(t.Root, FindMax=False)
    mx = t.FinMinMax(t.Root, FindMax=True)
    assert mn.NodeKey == 1
    assert mx.NodeKey == 9


def test_finminmax_on_subtree():
    t = build_bst([(10, "a"), (5, "b"), (15, "c"), (3, "d"), (7, "e"), (6, "f"), (8, "g")])
    sub = t.FindNodeByKey(5).Node
    mn = t.FinMinMax(sub, FindMax=False)
    mx = t.FinMinMax(sub, FindMax=True)
    assert mn.NodeKey == 3
    assert mx.NodeKey == 8


def test_finminmax_returns_none_if_fromnode_not_found():
    t = build_bst([(5, "a"), (2, "b")])
    ghost = BSTNode(999, "x", None)
    assert t.FinMinMax(ghost, FindMax=False) is None
    assert t.FinMinMax(ghost, FindMax=True) is None


def test_delete_leaf():
    t = build_bst([(5, "a"), (3, "b"), (7, "c")])  # лист: 3 или 7
    assert t.DeleteNodeByKey(3) is not False
    assert keys_inorder(t.Root) == [5, 7]
    assert t.Count() == 2


def test_delete_node_with_one_child():
    t = build_bst([(5, "a"), (3, "b"), (7, "c"), (6, "d")])  # у 7 один левый ребёнок 6
    assert t.DeleteNodeByKey(7) is not False
    assert keys_inorder(t.Root) == [3, 5, 6]
    # проверим корректность Parent
    six = t.FindNodeByKey(6).Node
    assert six.Parent.NodeKey == 5


def test_delete_node_with_two_children():
    t = build_bst([(5, "a"), (3, "b"), (7, "c"), (6, "d"), (8, "e")])  # у 7 два ребёнка
    assert t.DeleteNodeByKey(7) is not False
    # после удаления 7 корнем правого поддерева становится 8 или 6 в зависимости от реализации (берётся min справа)
    assert keys_inorder(t.Root) == [3, 5, 6, 8]


def test_delete_root_only_node():
    t = build_bst([(42, "x")])
    assert t.DeleteNodeByKey(42) is not False
    assert t.Root is None
    assert t.Count() == 0


def test_delete_root_with_two_children():
    t = build_bst([(5, "a"), (3, "b"), (7, "c"), (6, "d"), (8, "e")])
    assert t.DeleteNodeByKey(5) is not False
    # удаление корня с двумя детьми: на место корня должен прийти min из правого поддерева (6)
    assert t.Root.NodeKey in (6, 7)  # допускаем разные промежуточные шаги, но проверим порядок
    assert keys_inorder(t.Root) == [3, 6, 7, 8]


def test_delete_absent_key_returns_false():
    t = build_bst([(5, "a"), (3, "b")])
    assert t.DeleteNodeByKey(999) is False


def test_add_existing_key_returns_false_and_does_not_change_tree():
    t = build_bst([(5, "a"), (3, "b"), (7, "c")])
    before = keys_inorder(t.Root)
    assert t.AddKeyValue(3, "dup") is False
    assert keys_inorder(t.Root) == before
