from typing import Sequence


class General:
    pass


class Any(General):
    pass


class Addable(General):
    def __add__(self, other):
        raise NotImplementedError


class Number(Any, Addable):
    def __init__(self, value: int):
        self.value = value

    def __add__(self, other):
        return Number(self.value + other.value)


class Vector[T: Addable](Any, Addable):
    def __init__(self, items: Sequence[T]):
        self.items = items

    def __add__(self, other):
        if len(self.items) != len(other.items):
            return None

        return Vector(
            [left + right for left, right in zip(self.items, other.items)]
        )


def test_vector_add():
    left = Vector([Number(1), Number(2)])
    right = Vector([Number(10), Number(20)])

    result = left + right

    assert result.items[0].value == 11
    assert result.items[1].value == 22


def test_recursive_add():
    left = Vector([
        Vector([
            Vector([Number(1), Number(2)]),
            Vector([Number(3), Number(4)]),
        ])
    ])

    right = Vector([
        Vector([
            Vector([Number(10), Number(20)]),
            Vector([Number(30), Number(40)]),
        ])
    ])

    result = left + right

    assert result.items[0].items[0].items[0].value == 11
    assert result.items[0].items[0].items[1].value == 22
    assert result.items[0].items[1].items[0].value == 33
    assert result.items[0].items[1].items[1].value == 44


def test_different_lengths():
    left = Vector([Number(1)])
    right = Vector([Number(10), Number(20)])

    assert left + right is None