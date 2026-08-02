import pytest

from ordered_list import OrderedList, OrderedStringList
from ordered_list_2 import OrderedList as ExtendedOrderedList


def build_ordered(list_class, asc, *values):
    ordered_list = list_class(asc)

    for value in values:
        ordered_list.add(value)

    return ordered_list


def assert_list(ordered_list, expected_values):
    nodes = ordered_list.get_all()
    forward_values = [node.value for node in nodes]
    backward_values = []
    current = ordered_list.tail

    while current is not None:
        backward_values.append(current.value)
        current = current.prev

    assert forward_values == expected_values
    assert backward_values == expected_values[::-1]
    assert ordered_list.len() == len(expected_values)

    if len(expected_values) == 0:
        assert ordered_list.head is None
        assert ordered_list.tail is None
        return

    assert ordered_list.head is nodes[0]
    assert ordered_list.tail is nodes[-1]
    assert ordered_list.head.prev is None
    assert ordered_list.tail.next is None


def test_compare_numbers():
    ordered_list = OrderedList(True)

    assert ordered_list.compare(1, 2) == -1
    assert ordered_list.compare(2, 2) == 0
    assert ordered_list.compare(3, 2) == 1


def test_add_ascending():
    ordered_list = build_ordered(OrderedList, True, 3, 1, 4, 2, 2)

    assert_list(ordered_list, [1, 2, 2, 3, 4])


def test_add_descending():
    ordered_list = build_ordered(OrderedList, False, 3, 1, 4, 2, 2)

    assert_list(ordered_list, [4, 3, 2, 2, 1])


def test_delete_ascending():
    ordered_list = build_ordered(OrderedList, True, 1, 2, 2, 3)

    ordered_list.delete(2)
    assert_list(ordered_list, [1, 2, 3])

    ordered_list.delete(1)
    assert_list(ordered_list, [2, 3])

    ordered_list.delete(3)
    assert_list(ordered_list, [2])

    ordered_list.delete(10)
    ordered_list.delete(2)
    assert_list(ordered_list, [])


def test_delete_descending():
    ordered_list = build_ordered(OrderedList, False, 1, 2, 2, 3)

    ordered_list.delete(2)
    assert_list(ordered_list, [3, 2, 1])

    ordered_list.delete(3)
    ordered_list.delete(1)
    assert_list(ordered_list, [2])


def test_ordered_string_list():
    ascending = build_ordered(
        OrderedStringList,
        True,
        ' banana ',
        'apple',
        ' cherry ',
    )
    descending = build_ordered(
        OrderedStringList,
        False,
        ' banana ',
        'apple',
        ' cherry ',
    )

    assert ascending.compare(' apple ', 'apple') == 0
    assert_list(ascending, ['apple', ' banana ', ' cherry '])
    assert_list(descending, [' cherry ', ' banana ', 'apple'])


def test_find_ascending():
    ordered_list = build_ordered(OrderedList, True, 1, 3, 5, 7)

    assert ordered_list.find(1) is ordered_list.head
    assert ordered_list.find(5).value == 5
    assert ordered_list.find(4) is None
    assert ordered_list.find(10) is None


def test_find_descending():
    ordered_list = build_ordered(OrderedList, False, 1, 3, 5, 7)

    assert ordered_list.find(7) is ordered_list.head
    assert ordered_list.find(3).value == 3
    assert ordered_list.find(4) is None
    assert ordered_list.find(0) is None


def test_clean():
    ordered_list = build_ordered(OrderedList, True, 1, 2, 3)

    assert not hasattr(ordered_list, 'asc')
    assert not hasattr(ordered_list, '__ascending')

    ordered_list.clean(False)
    assert_list(ordered_list, [])

    ordered_list.add(1)
    ordered_list.add(3)
    ordered_list.add(2)
    assert_list(ordered_list, [3, 2, 1])


def test_delete_duplicates():
    ascending = build_ordered(
        ExtendedOrderedList,
        True,
        1, 1, 2, 3, 3, 3, 4, 4,
    )
    descending = build_ordered(
        ExtendedOrderedList,
        False,
        1, 1, 2, 3, 3, 3, 4, 4,
    )

    ascending.delete_duplicates()
    descending.delete_duplicates()

    assert_list(ascending, [1, 2, 3, 4])
    assert_list(descending, [4, 3, 2, 1])


def test_merge():
    left = build_ordered(ExtendedOrderedList, True, 1, 3, 3, 7)
    right = build_ordered(ExtendedOrderedList, True, 2, 3, 4, 8)

    result = left.merge(right)

    assert_list(result, [1, 2, 3, 3, 3, 4, 7, 8])
    assert_list(left, [1, 3, 3, 7])
    assert_list(right, [2, 3, 4, 8])

    descending_left = build_ordered(ExtendedOrderedList, False, 5, 3, 1)
    descending_right = build_ordered(ExtendedOrderedList, False, 6, 4, 2)
    descending_result = descending_left.merge(descending_right)

    assert_list(descending_result, [6, 5, 4, 3, 2, 1])

    with pytest.raises(ValueError, match='same sort order'):
        left.merge(descending_left)


def test_contains_sublist():
    ordered_list = build_ordered(
        ExtendedOrderedList,
        True,
        1, 2, 2, 3, 4, 5,
    )
    present = build_ordered(ExtendedOrderedList, True, 2, 3, 4)
    absent = build_ordered(ExtendedOrderedList, True, 2, 4)
    empty = ExtendedOrderedList(True)
    wrong_order = build_ordered(ExtendedOrderedList, False, 2, 3, 4)

    assert ordered_list.contains_sublist(present) is True
    assert ordered_list.contains_sublist(absent) is False
    assert ordered_list.contains_sublist(empty) is True
    assert ordered_list.contains_sublist(wrong_order) is False


def test_find_most_frequent():
    ascending = build_ordered(
        ExtendedOrderedList,
        True,
        1, 2, 2, 3, 3, 3, 4,
    )
    descending = build_ordered(
        ExtendedOrderedList,
        False,
        1, 2, 2, 2, 3, 3,
    )

    assert ExtendedOrderedList(True).find_most_frequent() is None
    assert ascending.find_most_frequent() == 3
    assert descending.find_most_frequent() == 2


def test_find_index():
    ascending = build_ordered(
        ExtendedOrderedList,
        True,
        10, 5, 15, 7, 7,
    )
    descending = build_ordered(
        ExtendedOrderedList,
        False,
        10, 5, 15, 7,
    )

    assert ascending.find_index(5) == 0
    assert ascending.find_index(7) == 1
    assert ascending.find_index(15) == 4
    assert ascending.find_index(20) == -1
    assert descending.find_index(15) == 0
    assert descending.find_index(7) == 2

    ascending.delete(7)
    assert ascending.find_index(7) == 1

    ascending.delete_duplicates()
    assert ascending.find_index(10) == 2

    ascending.clean(False)
    ascending.add(1)
    ascending.add(3)
    ascending.add(2)
    assert ascending.find_index(2) == 1
