import pytest

from stack import Stack
from stack_2 import (
    Stack as ExtendedStack,
    evaluate_postfix,
    is_brackets_balanced_ext,
    is_brackets_balanced,
)


def test_size():
    stack = Stack()

    assert stack.size() == 0

    stack.push(1)
    stack.push('2')
    assert stack.size() == 2

    stack.pop()
    assert stack.size() == 1


def test_push():
    stack = Stack()

    stack.push(1)
    stack.push('2')
    stack.push(3.14)

    assert stack.size() == 3
    assert stack.peek() == 3.14


def test_pop():
    stack = Stack()
    stack.push(1)
    stack.push('2')
    stack.push(3.14)

    assert stack.pop() == 3.14
    assert stack.pop() == '2'
    assert stack.pop() == 1
    assert stack.size() == 0

    with pytest.raises(IndexError, match='Stack is empty'):
        stack.pop()


def test_peek():
    stack = Stack()

    with pytest.raises(IndexError, match='Stack is empty'):
        stack.peek()

    stack.push(1)
    stack.push('2')
    size_before_peek = stack.size()

    assert stack.peek() == '2'
    assert stack.peek() == '2'
    assert stack.size() == size_before_peek



def test_stack_with_head():
    stack = Stack()

    stack.push(1)
    stack.push('2')
    stack.push(3.14)

    assert stack.stack == [3.14, '2', 1]
    assert stack.peek() == 3.14
    assert stack.pop() == 3.14
    assert stack.stack == ['2', 1]


@pytest.mark.parametrize(
    ('sequence', 'expected'),
    (
        ('', True),
        ('()', True),
        ('(()((())()))', True),
        ('(()()(()', False),
        ('())(', False),
        ('))((', False),
        ('((())', False),
        ('(a)', False),
        ('([])', False),
        ('{', False),
    ),
)
def test_parentheses_balance(sequence, expected):
    assert is_brackets_balanced(sequence) is expected


@pytest.mark.parametrize(
    ('sequence', 'expected'),
    (
        ('', True),
        ('()', True),
        ('{}', True),
        ('[]', True),
        ('({[]})', True),
        ('[(){}([])]', True),
        ('(]', False),
        ('([)]', False),
        ('{[}', False),
        (']', False),
        ('((())', False),
        ('(a)', False),
    ),
)
def test_brackets_balance(sequence, expected):
    assert is_brackets_balanced_ext(sequence) is expected


def test_get_min():
    stack = ExtendedStack()

    with pytest.raises(IndexError, match='Stack is empty'):
        stack.get_min()

    for value, expected_minimum in (
        (3, 3),
        (1, 1),
        (2, 1),
        (1, 1),
    ):
        stack.push(value)
        assert stack.get_min() == expected_minimum

    assert stack.pop() == 1
    assert stack.get_min() == 1
    assert stack.pop() == 2
    assert stack.get_min() == 1
    assert stack.pop() == 1
    assert stack.get_min() == 3
    assert stack.pop() == 3

    with pytest.raises(IndexError, match='Stack is empty'):
        stack.get_min()


def test_get_average():
    stack = ExtendedStack()

    with pytest.raises(IndexError, match='Stack is empty'):
        stack.get_average()

    stack.push(2)
    assert stack.get_average() == 2

    stack.push(4)
    assert stack.get_average() == 3

    stack.push(-3)
    assert stack.get_average() == 1

    assert stack.pop() == -3
    assert stack.get_average() == 3

    stack.push(2.5)
    assert stack.get_average() == pytest.approx(8.5 / 3)


def test_extended_stack_rejects_non_numeric_values():
    stack = ExtendedStack()

    with pytest.raises(TypeError, match='only numeric values'):
        stack.push('1')

    assert stack.size() == 0


@pytest.mark.parametrize(
    ('expression', 'expected'),
    (
        ('8 2 + 5 * 9 + =', 59),
        ('1 2 + 3 *', 9),
        ('2 3 4 * + =', 14),
        ('-2 3 * =', -6),
        ('42 =', 42),
    ),
)
def test_evaluate_postfix(expression, expected):
    assert evaluate_postfix(expression) == expected


@pytest.mark.parametrize(
    'expression',
    (
        '',
        '=',
        '1 2 =',
        '1 + =',
        '1 unknown + =',
        '1 = 2',
    ),
)
def test_evaluate_postfix_rejects_invalid_expression(expression):
    with pytest.raises(ValueError):
        evaluate_postfix(expression)
