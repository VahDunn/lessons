from linked_list_2 import LinkedList2, Node
from linked_list_2_2 import LinkedList2 as ExtendedLinkedList2
from linked_list_2_2 import LinkedList2WithDummy, Node as ExtendedNode


def build_list(*values):
    linked_list = LinkedList2()
    nodes = [Node(value) for value in values]

    for node in nodes:
        linked_list.add_in_tail(node)

    return linked_list, nodes


def build_extended_list(*values):
    linked_list = ExtendedLinkedList2()
    nodes = [ExtendedNode(value) for value in values]

    for node in nodes:
        linked_list.add_in_tail(node)

    return linked_list, nodes


def assert_list(linked_list, expected_nodes):
    forward_nodes = []
    current = linked_list.head

    while current is not None:
        forward_nodes.append(current)
        current = current.next

    backward_nodes = []
    current = linked_list.tail

    while current is not None:
        backward_nodes.append(current)
        current = current.prev

    assert forward_nodes == expected_nodes
    assert backward_nodes == expected_nodes[::-1]
    assert linked_list.len() == len(expected_nodes)

    if expected_nodes:
        assert linked_list.head is expected_nodes[0]
        assert linked_list.tail is expected_nodes[-1]
        assert linked_list.head.prev is None
        assert linked_list.tail.next is None
    else:
        assert linked_list.head is None
        assert linked_list.tail is None


def build_dummy_list(*values):
    linked_list = LinkedList2WithDummy()
    nodes = [ExtendedNode(value) for value in values]

    for node in nodes:
        linked_list.add_in_tail(node)

    return linked_list, nodes


def assert_dummy_list(linked_list, expected_nodes):
    assert linked_list.head is not linked_list.tail
    assert linked_list.head.value is None
    assert linked_list.tail.value is None
    assert linked_list.head.prev is None
    assert linked_list.tail.next is None

    forward_nodes = []
    current = linked_list.head.next

    while current is not linked_list.tail:
        forward_nodes.append(current)
        current = current.next

    backward_nodes = []
    current = linked_list.tail.prev

    while current is not linked_list.head:
        backward_nodes.append(current)
        current = current.prev

    assert forward_nodes == expected_nodes
    assert backward_nodes == expected_nodes[::-1]
    assert linked_list.len() == len(expected_nodes)

    if expected_nodes:
        assert linked_list.head.next is expected_nodes[0]
        assert expected_nodes[0].prev is linked_list.head
        assert linked_list.tail.prev is expected_nodes[-1]
        assert expected_nodes[-1].next is linked_list.tail
    else:
        assert linked_list.head.next is linked_list.tail
        assert linked_list.tail.prev is linked_list.head


# Основные тесты для linked_list_2.py


def test_find_in_empty_list():
    linked_list = LinkedList2()

    assert linked_list.find(1) is None


def test_find_returns_first_matching_node():
    linked_list, nodes = build_list(1, 2, 1)

    assert linked_list.find(1) is nodes[0]


def test_find_returns_none_when_value_is_absent():
    linked_list, _ = build_list(1, 2, 3)

    assert linked_list.find(10) is None


def test_find_all_in_empty_list():
    linked_list = LinkedList2()

    assert linked_list.find_all(1) == []


def test_find_all_returns_all_matching_nodes():
    linked_list, nodes = build_list(1, 2, 1, 3, 1)

    assert linked_list.find_all(1) == [nodes[0], nodes[2], nodes[4]]


def test_find_all_returns_empty_list_when_value_is_absent():
    linked_list, _ = build_list(1, 2, 3)

    assert linked_list.find_all(10) == []


def test_insert_after_node_and_at_head():
    linked_list, nodes = build_list(1, 3)
    first = Node(0)
    middle = Node(2)

    linked_list.insert(nodes[0], middle)
    linked_list.insert(None, first)

    assert_list(linked_list, [first, nodes[0], middle, nodes[1]])


def test_add_in_head():
    linked_list = LinkedList2()
    nodes = [Node(2), Node(1)]

    for node in nodes:
        linked_list.add_in_head(node)

    assert_list(linked_list, nodes[::-1])


def test_len_for_empty_single_and_long_list():
    empty_list = LinkedList2()
    single_list, _ = build_list(1)
    long_list, _ = build_list(1, 2, 3, 4, 5)

    assert empty_list.len() == 0
    assert single_list.len() == 1
    assert long_list.len() == 5


def test_clean_empties_list():
    linked_list, _ = build_list(1, 2, 3)

    linked_list.clean()

    assert linked_list.head is None
    assert linked_list.tail is None
    assert linked_list.len() == 0


def test_clean_empty_list():
    linked_list = LinkedList2()

    linked_list.clean()

    assert linked_list.head is None
    assert linked_list.tail is None
    assert linked_list.len() == 0


def test_delete_from_empty_list():
    linked_list = LinkedList2()

    linked_list.delete(1)

    assert_list(linked_list, [])


def test_delete_removes_only_first_matching_node_by_default():
    linked_list, nodes = build_list(1, 2, 1)

    linked_list.delete(1)

    assert_list(linked_list, [nodes[1], nodes[2]])


def test_delete_removes_node_from_middle():
    linked_list, nodes = build_list(1, 2, 3)

    linked_list.delete(2)

    assert_list(linked_list, [nodes[0], nodes[2]])


def test_delete_updates_tail():
    linked_list, nodes = build_list(1, 2, 3)

    linked_list.delete(3)

    assert_list(linked_list, [nodes[0], nodes[1]])


def test_delete_only_node_makes_list_empty():
    linked_list, _ = build_list(1)

    linked_list.delete(1)

    assert_list(linked_list, [])


def test_delete_all_removes_matches_from_entire_list():
    linked_list, nodes = build_list(1, 1, 2, 1, 3, 1, 1)

    linked_list.delete(1, all=True)

    assert_list(linked_list, [nodes[2], nodes[4]])


def test_delete_all_matching_nodes_makes_list_empty():
    linked_list, _ = build_list(1, 1, 1)

    linked_list.delete(1, all=True)

    assert_list(linked_list, [])


def test_delete_absent_value_does_not_change_list():
    linked_list, nodes = build_list(1, 2, 3)

    linked_list.delete(10, all=True)

    assert_list(linked_list, nodes)


# Дополнительные тесты для linked_list_2_2.py


def test_reverse():
    for values in ((), (1,), (1, 2, 3, 4)):
        linked_list, nodes = build_extended_list(*values)

        linked_list.reverse()

        assert_list(linked_list, nodes[::-1])


def test_has_cycle():
    assert ExtendedLinkedList2().has_cycle() is False

    linked_list, nodes = build_extended_list(1, 2, 3, 4)
    assert linked_list.has_cycle() is False

    nodes[-1].next = nodes[1]
    assert linked_list.has_cycle() is True


def test_sort():
    for values in ((), (1,)):
        linked_list, nodes = build_extended_list(*values)
        linked_list.sort()
        assert_list(linked_list, nodes)

    linked_list, nodes = build_extended_list(3, 1, 2, 1, 3)
    linked_list.sort()
    assert_list(linked_list, [nodes[1], nodes[3], nodes[2], nodes[0], nodes[4]])


def test_merge():
    assert_list(ExtendedLinkedList2().merge(ExtendedLinkedList2()), [])

    left, left_nodes = build_extended_list(1, 3, 3, 7)
    right, right_nodes = build_extended_list(2, 3, 4, 8)
    result = left.merge(right)

    result_nodes = []
    current = result.head

    while current is not None:
        result_nodes.append(current)
        current = current.next

    assert [node.value for node in result_nodes] == [1, 2, 3, 3, 3, 4, 7, 8]
    assert all(node not in left_nodes + right_nodes for node in result_nodes)
    assert_list(result, result_nodes)
    assert_list(left, left_nodes)
    assert_list(right, right_nodes)


def test_dummy_list_boundaries():
    linked_list = LinkedList2WithDummy()
    dummy_head = linked_list.head
    dummy_tail = linked_list.tail

    assert_dummy_list(linked_list, [])

    linked_list.add_in_tail(ExtendedNode(1))
    linked_list.clean()

    assert linked_list.head is dummy_head
    assert linked_list.tail is dummy_tail
    assert_dummy_list(linked_list, [])


def test_dummy_list_find_ignores_dummy_nodes():
    linked_list, nodes = build_dummy_list(None, 1, None, 2)

    assert linked_list.find(None) is nodes[0]
    assert linked_list.find_all(None) == [nodes[0], nodes[2]]
    assert linked_list.find(10) is None


def test_dummy_list_insert_and_delete():
    linked_list, nodes = build_dummy_list(1, 3, 1)
    first = ExtendedNode(0)
    middle = ExtendedNode(2)

    linked_list.insert(nodes[0], middle)
    linked_list.insert(None, first)
    linked_list.delete(1, all=True)

    assert_dummy_list(linked_list, [first, middle, nodes[1]])


def test_dummy_list_algorithms():
    linked_list, nodes = build_dummy_list(3, 1, 2, 1, 3)

    linked_list.sort()

    assert_dummy_list(
        linked_list,
        [nodes[1], nodes[3], nodes[2], nodes[0], nodes[4]],
    )

    linked_list.reverse()
    assert_dummy_list(
        linked_list,
        [nodes[4], nodes[0], nodes[2], nodes[3], nodes[1]],
    )

    assert linked_list.has_cycle() is False

    linked_list.tail.prev.next = linked_list.head.next
    assert linked_list.has_cycle() is True


def test_dummy_list_merge():
    left, left_nodes = build_dummy_list(1, 3, 5)
    right, right_nodes = build_dummy_list(2, 4, 6)

    result = left.merge(right)
    result_nodes = []
    current = result.head.next

    while current is not result.tail:
        result_nodes.append(current)
        current = current.next

    assert [node.value for node in result_nodes] == [1, 2, 3, 4, 5, 6]
    assert_dummy_list(result, result_nodes)
    assert_dummy_list(left, left_nodes)
    assert_dummy_list(right, right_nodes)
