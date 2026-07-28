from linked_list import LinkedList, Node
from linked_list_2 import sum_linked_lists


def build_list(*values):
    linked_list = LinkedList()
    nodes = [Node(value) for value in values]

    for node in nodes:
        linked_list.add_in_tail(node)

    return linked_list, nodes


def list_nodes(linked_list):
    nodes = []
    current = linked_list.head

    while current is not None:
        nodes.append(current)
        current = current.next

    return nodes


def assert_list(linked_list, expected_values):
    nodes = list_nodes(linked_list)

    assert [node.value for node in nodes] == expected_values
    assert linked_list.len() == len(expected_values)

    if expected_values:
        assert linked_list.head is nodes[0]
        assert linked_list.tail is nodes[-1]
        assert linked_list.tail.next is None
    else:
        assert linked_list.head is None
        assert linked_list.tail is None


def test_find_all_in_empty_list():
    linked_list = LinkedList()

    assert linked_list.find_all(1) == []
    assert_list(linked_list, [])


def test_find_all_returns_all_matching_nodes():
    linked_list, nodes = build_list(1, 2, 1, 3, 1)

    found = linked_list.find_all(1)

    assert found == [nodes[0], nodes[2], nodes[4]]
    assert_list(linked_list, [1, 2, 1, 3, 1])


def test_find_all_returns_empty_list_when_value_is_absent():
    linked_list, _ = build_list(1, 2, 3)

    assert linked_list.find_all(10) == []
    assert_list(linked_list, [1, 2, 3])


def test_delete_from_empty_list():
    linked_list = LinkedList()

    linked_list.delete(1)

    assert_list(linked_list, [])


def test_delete_removes_only_first_matching_node_by_default():
    linked_list, nodes = build_list(1, 1, 2, 1)

    linked_list.delete(1)

    assert list_nodes(linked_list) == [nodes[1], nodes[2], nodes[3]]
    assert_list(linked_list, [1, 2, 1])


def test_delete_removes_node_from_middle():
    linked_list, nodes = build_list(1, 2, 3)

    linked_list.delete(2)

    assert list_nodes(linked_list) == [nodes[0], nodes[2]]
    assert_list(linked_list, [1, 3])


def test_delete_updates_tail():
    linked_list, nodes = build_list(1, 2, 3)

    linked_list.delete(3)

    assert linked_list.tail is nodes[1]
    assert_list(linked_list, [1, 2])


def test_delete_only_node_makes_list_empty():
    linked_list, _ = build_list(1)

    linked_list.delete(1)

    assert_list(linked_list, [])


def test_delete_all_removes_matches_from_entire_list():
    linked_list, nodes = build_list(1, 1, 2, 1, 3, 1, 1)

    linked_list.delete(1, all=True)

    assert list_nodes(linked_list) == [nodes[2], nodes[4]]
    assert_list(linked_list, [2, 3])


def test_delete_all_matching_nodes_makes_list_empty():
    linked_list, _ = build_list(1, 1, 1)

    linked_list.delete(1, all=True)

    assert_list(linked_list, [])


def test_delete_absent_value_does_not_change_list():
    linked_list, nodes = build_list(1, 2, 3)

    linked_list.delete(10, all=True)

    assert list_nodes(linked_list) == nodes
    assert_list(linked_list, [1, 2, 3])


def test_clean_empties_list():
    linked_list, _ = build_list(1, 2, 3)

    linked_list.clean()

    assert_list(linked_list, [])


def test_cleaned_list_can_be_reused():
    linked_list, _ = build_list(1, 2)
    linked_list.clean()
    new_node = Node(3)

    linked_list.add_in_tail(new_node)

    assert linked_list.head is new_node
    assert linked_list.tail is new_node
    assert_list(linked_list, [3])


def test_len_for_empty_single_and_long_list():
    empty_list = LinkedList()
    single_list, _ = build_list(1)
    long_list, _ = build_list(1, 2, 3, 4, 5)

    assert empty_list.len() == 0
    assert single_list.len() == 1
    assert long_list.len() == 5


def test_insert_into_empty_list():
    linked_list = LinkedList()
    new_node = Node(1)

    linked_list.insert(None, new_node)

    assert linked_list.head is new_node
    assert linked_list.tail is new_node
    assert_list(linked_list, [1])


def test_insert_at_beginning_of_non_empty_list():
    linked_list, nodes = build_list(1, 2)
    new_node = Node(0)

    linked_list.insert(None, new_node)

    assert list_nodes(linked_list) == [new_node, nodes[0], nodes[1]]
    assert_list(linked_list, [0, 1, 2])


def test_insert_after_middle_node():
    linked_list, nodes = build_list(1, 2, 3)
    new_node = Node(10)

    linked_list.insert(nodes[1], new_node)

    assert list_nodes(linked_list) == [nodes[0], nodes[1], new_node, nodes[2]]
    assert_list(linked_list, [1, 2, 10, 3])


def test_insert_after_tail_updates_tail():
    linked_list, nodes = build_list(1, 2)
    new_node = Node(3)

    linked_list.insert(nodes[1], new_node)

    assert linked_list.tail is new_node
    assert_list(linked_list, [1, 2, 3])


def test_sum_linked_lists():
    first_list, _ = build_list(1, 2, 3)
    second_list, _ = build_list(4, 5, 6)

    result = sum_linked_lists(first_list, second_list)

    assert_list(result, [5, 7, 9])


def test_sum_linked_lists_supports_negative_values():
    first_list, _ = build_list(-5, 10, 0)
    second_list, _ = build_list(2, -3, -4)

    result = sum_linked_lists(first_list, second_list)

    assert_list(result, [-3, 7, -4])


def test_sum_linked_lists_returns_none_for_different_lengths():
    first_list, _ = build_list(1, 2)
    second_list, _ = build_list(3)

    assert sum_linked_lists(first_list, second_list) is None


def test_sum_linked_lists_returns_empty_list_for_empty_inputs():
    first_list = LinkedList()
    second_list = LinkedList()

    result = sum_linked_lists(first_list, second_list)

    assert isinstance(result, LinkedList)
    assert_list(result, [])


def test_sum_linked_lists_does_not_change_or_reuse_input_nodes():
    first_list, first_nodes = build_list(1, 2)
    second_list, second_nodes = build_list(3, 4)

    result = sum_linked_lists(first_list, second_list)
    result_nodes = list_nodes(result)

    assert_list(first_list, [1, 2])
    assert_list(second_list, [3, 4])
    assert all(node not in first_nodes + second_nodes for node in result_nodes)
