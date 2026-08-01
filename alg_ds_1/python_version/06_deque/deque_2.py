from deque import Deque as BaseDeque


# Задание на курсе: 6
# Задача: 7.3
# Название: проверка строки на палиндром с помощью деки
# Временная сложность: O(n^2) для текущей реализации деки
# Пространственная сложность: O(n)
def is_palindrome(value):
    deque = BaseDeque()

    for symbol in value:
        deque.addTail(symbol)

    while deque.size() > 1:
        if deque.removeFront() != deque.removeTail():
            return False

    return True


# Задание на курсе: 6
# Задача: 7.4
# Название: дека с получением минимального элемента за O(1)
class Deque(BaseDeque):

    def __init__(self):
        super().__init__()
        self.sorted_values = []

    # Временная сложность: O(n)
    # Пространственная сложность: O(1), O(n) при реаллокации
    def addFront(self, item):
        super().addFront(item)
        self._insert_sorted_value(item)

    # Временная сложность: O(n)
    # Пространственная сложность: O(1)
    def removeFront(self):
        if self.size() == 0:
            return None

        item = super().removeFront()
        self._remove_sorted_value(item)

        return item

    # Временная сложность: O(n)
    # Пространственная сложность: O(1), O(n) при реаллокации
    def addTail(self, item):
        super().addTail(item)
        self._insert_sorted_value(item)

    # Временная сложность: O(n)
    # Пространственная сложность: O(1)
    def removeTail(self):
        if self.size() == 0:
            return None

        item = super().removeTail()
        self._remove_sorted_value(item)

        return item

    # Требуемая временная сложность: O(1)
    # Пространственная сложность: O(1)
    def get_min(self):
        if self.size() == 0:
            return None

        return self.sorted_values[0]

    def _insert_sorted_value(self, item):
        index = self._find_sorted_index(item)
        self.sorted_values.insert(index, item)

    def _remove_sorted_value(self, item):
        index = self._find_sorted_index(item)
        self.sorted_values.pop(index)

    def _find_sorted_index(self, item):
        left = 0
        right = len(self.sorted_values)

        while left < right:
            middle = (left + right) // 2

            if self.sorted_values[middle] < item:
                left = middle + 1
                continue

            right = middle

        return left


# Задание на курсе: 6
# Задача: 7.5
# Название: дека на динамическом массиве
class ArrayDeque:

    MIN_CAPACITY = 4

    def __init__(self):
        self.array = [None] * self.MIN_CAPACITY
        self.head = 0
        self.count = 0

    # Временная сложность: O(1)
    # Пространственная сложность: O(1)
    def size(self):
        return self.count

    # Требуемая амортизированная сложность: O(1)
    def addFront(self, item):
        self._grow_if_full()
        self.head = (self.head - 1) % len(self.array)
        self.array[self.head] = item
        self.count += 1

    # Требуемая амортизированная сложность: O(1)
    def removeFront(self):
        if self.size() == 0:
            return None

        item = self.array[self.head]
        self.array[self.head] = None
        self.head = (self.head + 1) % len(self.array)
        self.count -= 1
        self._shrink_if_needed()

        return item

    # Требуемая амортизированная сложность: O(1)
    def addTail(self, item):
        self._grow_if_full()
        tail = (self.head + self.count) % len(self.array)
        self.array[tail] = item
        self.count += 1

    # Требуемая амортизированная сложность: O(1)
    def removeTail(self):
        if self.size() == 0:
            return None

        tail = (self.head + self.count - 1) % len(self.array)
        item = self.array[tail]
        self.array[tail] = None
        self.count -= 1
        self._shrink_if_needed()

        return item

    def _grow_if_full(self):
        if self.count < len(self.array):
            return

        self._resize(len(self.array) * 2)

    def _shrink_if_needed(self):
        if len(self.array) == self.MIN_CAPACITY:
            return

        if self.count * 4 > len(self.array):
            return

        self._resize(max(self.MIN_CAPACITY, len(self.array) // 2))

    def _resize(self, capacity):
        resized_array = [None] * capacity

        for index in range(self.count):
            source_index = (self.head + index) % len(self.array)
            resized_array[index] = self.array[source_index]

        self.array = resized_array
        self.head = 0


# Задание на курсе: 6
# Задача: 7.6
# Название: проверка баланса скобок с использованием стека
# Требуемая временная сложность: O(n)
# Пространственная сложность: O(n)
def is_brackets_balanced(expression: str) -> bool:
    stack = []
    opening_brackets = ('(', '[', '{')
    matching_opening_brackets = {
        ')': '(',
        ']': '[',
        '}': '{',
    }

    for bracket in expression:
        if bracket in opening_brackets:
            stack.append(bracket)
            continue

        if len(stack) == 0:
            return False

        if stack.pop() != matching_opening_brackets[bracket]:
            return False

    return len(stack) == 0

# Рефлексия
# Со скобками решал просто через проверку на непустой стек, для разных типов - проверка на непустой с предварительной
# проверкой типа скобки.
# Минимум за О(1) - стек + стек минимумов, в котором история минимумов хранится параллельно основному стеку.
# Соответственно при удалении элемента из обычного стека, если он равен минимуму во втором, значит, это один и тот же
# элемент. По сути второй стек это вариант сжатия первого.
# Про среднее за О(1) - хранил сумму. Сначала думал обновлять среднее каждый раз, но это зависит от частоты запросов
# на это среднее по отношению к частоте обновления стека. Так что скорее всего сумму хранить дешевле.
# С постфиксным выражением интересно получилось. Раньше решал как описано неправильно решение в эталоне, но
# вывод в отдельные функции помог в текущей итерации.


