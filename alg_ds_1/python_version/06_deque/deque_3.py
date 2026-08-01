import pytest

from deque import Deque
from deque_2 import (
    ArrayDeque,
    Deque as MinDeque,
    is_brackets_balanced,
    is_palindrome,
)


# Основные тесты для deque.py


def test_add_front():
    deque = Deque()

    deque.addFront(1)

    assert deque.size() == 1
    assert 1 in deque.deque


def test_remove_front():
    deque = Deque()
    deque.addFront(1)
    deque.addFront(2)

    assert deque.removeFront() == 2
    assert deque.size() == 1
    assert 2 not in deque.deque
    assert deque.removeFront() == 1
    assert deque.removeFront() is None


def test_add_tail():
    deque = Deque()

    deque.addTail(1)

    assert deque.size() == 1
    assert 1 in deque.deque


def test_remove_tail():
    deque = Deque()
    deque.addTail(1)
    deque.addTail(2)

    assert deque.removeTail() == 2
    assert deque.size() == 1
    assert 2 not in deque.deque
    assert deque.removeTail() == 1
    assert deque.removeTail() is None


def test_mixed_deque_operations():
    deque = Deque()
    deque.addFront(2)
    deque.addFront(1)
    deque.addTail(3)
    deque.addTail(4)

    assert deque.size() == 4
    assert deque.removeFront() == 1
    assert deque.removeTail() == 4
    assert deque.removeFront() == 2
    assert deque.removeTail() == 3
    assert deque.size() == 0


# Дополнительные тесты для deque_2.py


@pytest.mark.parametrize(
    ('value', 'expected'),
    (
        ('', True),
        ('a', True),
        ('level', True),
        ('abba', True),
        ('python', False),
        ('abca', False),
    ),
)
def test_is_palindrome(value, expected):
    assert is_palindrome(value) is expected


def test_get_min():
    deque = MinDeque()

    assert deque.get_min() is None
    assert deque.removeFront() is None
    assert deque.removeTail() is None

    deque.addTail(3)
    assert deque.get_min() == 3

    deque.addFront(5)
    assert deque.get_min() == 3

    deque.addTail(1)
    deque.addFront(1)
    assert deque.get_min() == 1

    assert deque.removeFront() == 1
    assert deque.get_min() == 1
    assert deque.removeTail() == 1
    assert deque.get_min() == 3
    assert deque.removeFront() == 5
    assert deque.get_min() == 3
    assert deque.removeTail() == 3
    assert deque.get_min() is None


def test_array_deque():
    deque = ArrayDeque()
    initial_capacity = len(deque.array)

    assert deque.removeFront() is None
    assert deque.removeTail() is None

    for item in range(10):
        deque.addTail(item)

    assert deque.size() == 10
    assert len(deque.array) > initial_capacity

    for expected in range(3):
        assert deque.removeFront() == expected

    for item in (-1, -2, -3):
        deque.addFront(item)

    assert deque.removeFront() == -3
    assert deque.removeTail() == 9
    assert [deque.removeFront() for _ in range(8)] == [
        -2, -1, 3, 4, 5, 6, 7, 8,
    ]
    assert deque.size() == 0
    assert len(deque.array) == initial_capacity


@pytest.mark.parametrize(
    ('expression', 'expected'),
    (
        ('', True),
        ('()', True),
        ('[]({})', True),
        ('[({})]{}', True),
        ('(())}{(', False),
        ('([)]', False),
        (']', False),
        ('((())', False),
    ),
)
def test_brackets_balance(expression, expected):
    assert is_brackets_balanced(expression) is expected
