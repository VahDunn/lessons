from operator import add, mul

from stack import Stack as BaseStack


class Stack(BaseStack):

    def __init__(self):
        super().__init__()
        self.minimums = BaseStack()
        self.total = 0

    # Временная сложность: O(n)
    # Пространственная сложность: O(1), O(n) при реаллокации
    def push(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError('Stack supports only numeric values')

        should_store_minimum = (
            self.minimums.size() == 0
            or value <= self.minimums.peek()
        )
        super().push(value)
        self.total += value

        if should_store_minimum:
            self.minimums.push(value)

    # Временная сложность: O(n)
    # Пространственная сложность: O(1)
    def pop(self):
        value = super().pop()
        self.total -= value

        if value == self.minimums.peek():
            self.minimums.pop()

        return value

    # Задание на курсе: 4
    # Задача: 7
    # Название: получение минимального элемента
    # Временная сложность: O(1)
    # Пространственная сложность: O(1) для вызова, O(n) для второго стека
    def get_min(self):
        return self.minimums.peek()

    # Задание на курсе: 4
    # Задача: 8
    # Название: получение среднего значения элементов
    # Временная сложность: O(1)
    # Пространственная сложность: O(1)
    def get_average(self):
        if self.size() == 0:
            raise IndexError('Stack is empty')

        return self.total / self.size()

# Задание на курсе: 4
# Задача: 3
# Название: два вызова pop() за одну итерацию
#
# Ответ:
# При чётном количестве элементов цикл напечатает их попарно и опустошит стек.
# При нечётном количестве первый pop() последней итерации напечатает оставшийся
# элемент, а второй pop() вызовет IndexError, потому что стек уже будет пуст.


# Задание на курсе: 4
# Задача: 5
# Название: проверка баланса круглых скобок
# Временная сложность: O(n^2) для текущей реализации стека
# Пространственная сложность: O(n)
def is_brackets_balanced(sequence):
    stack = BaseStack()

    for parenthesis in sequence:
        if parenthesis == '(':
            stack.push(parenthesis)
            continue

        if parenthesis != ')':
            return False

        if stack.size() == 0:
            return False

        stack.pop()

    return stack.size() == 0


# Задание на курсе: 4
# Задача: 6
# Название: проверка баланса скобок трёх типов
# Временная сложность: O(n^2) для текущей реализации стека
# Пространственная сложность: O(n)
def is_brackets_balanced_ext(sequence):
    stack = BaseStack()
    opening_brackets = ('(', '{', '[')
    matching_opening_brackets = {
        ')': '(',
        '}': '{',
        ']': '[',
    }

    for bracket in sequence:
        if bracket in opening_brackets:
            stack.push(bracket)
            continue

        if bracket not in matching_opening_brackets:
            return False

        if stack.size() == 0:
            return False

        if stack.pop() != matching_opening_brackets[bracket]:
            return False

    return stack.size() == 0


# Задание на курсе: 4
# Задача: 9
# Название: вычисление постфиксного выражения
# Временная сложность: O(n^2) для текущей реализации стека
# Пространственная сложность: O(n)
def evaluate_postfix(expression):
    input_stack = BaseStack()
    result_stack = BaseStack()
    operations = {
        '+': add,
        '*': mul,
    }

    for token in reversed(expression.split()):
        input_stack.push(token)

    while input_stack.size() > 0:
        token = input_stack.pop()

        if token == '=':
            return _get_postfix_result(input_stack, result_stack)

        if token in operations:
            _apply_postfix_operation(result_stack, operations[token])
            continue

        result_stack.push(_parse_integer(token))

    return _get_postfix_result(input_stack, result_stack)


def _apply_postfix_operation(stack, operation):
    if stack.size() < 2:
        raise ValueError('Not enough operands')

    right_operand = stack.pop()
    left_operand = stack.pop()
    stack.push(operation(left_operand, right_operand))


def _parse_integer(token):
    try:
        return int(token)
    except ValueError as error:
        raise ValueError(f'Invalid token: {token}') from error


def _get_postfix_result(input_stack, result_stack):
    if input_stack.size() > 0:
        raise ValueError("'=' must be the last token")

    if result_stack.size() != 1:
        raise ValueError('Invalid postfix expression')

    return result_stack.peek()


# Рефлексия
# Некоторая проблема была с "аккуратно" при развороте списка, но
# в итоге все удалось. Циклы искал через 2 указателя, но через
# 1 определенно проще.
# Про сортировку пузырьком опять забыл, пошел перечитывать.
# Про круговой список с одним дамми интересно, кажется удобным.
# Делал кстати с флагом, но с отдельным классом выразительность лучше.
