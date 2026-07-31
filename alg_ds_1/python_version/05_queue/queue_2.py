from queue import Queue as BaseQueue


# Задание на курсе: 5
# Задача: 3
# Название: циклическое вращение очереди на m элементов
# Временная сложность: O(n^2), где n — размер очереди
# Пространственная сложность: O(1)
def rotate_queue(queue, m):
    if queue.size() == 0:
        return

    rotations = m % queue.size()

    for _ in range(rotations):
        queue.enqueue(queue.dequeue())


# Задание на курсе: 5
# Задача: 4
# Название: очередь на двух стеках
class TwoStackQueue:

    def __init__(self):
        self.input_stack = []
        self.output_stack = []

    # Временная сложность: амортизированная O(1)
    # Пространственная сложность: O(1)
    def enqueue(self, item):
        self.input_stack.append(item)

    # Временная сложность: O(n), амортизированная O(1)
    # Пространственная сложность: O(1)
    def dequeue(self):
        if self.size() == 0:
            return None

        if len(self.output_stack) > 0:
            return self.output_stack.pop()

        while len(self.input_stack) > 0:
            self.output_stack.append(self.input_stack.pop())

        return self.output_stack.pop()

    # Временная сложность: O(1)
    # Пространственная сложность: O(1)
    def size(self):
        return len(self.input_stack) + len(self.output_stack)


# Задание на курсе: 5
# Задача: 5
# Название: очередь с обращением элементов
class Queue(BaseQueue):

    # Временная сложность: O(n^2)
    # Пространственная сложность: O(n)
    def reverse(self):
        stack = []

        while self.size() > 0:
            stack.append(self.dequeue())

        while len(stack) > 0:
            self.enqueue(stack.pop())


# Задание на курсе: 5
# Задача: 6
# Название: циклическая очередь в статическом массиве
class CircularQueue:

    def __init__(self, capacity):
        self.capacity = capacity
        self.queue = [None] * capacity
        self.head = 0
        self.tail = 0
        self.count = 0

    # Временная сложность: O(1)
    # Пространственная сложность: O(1)
    def size(self):
        return self.count

    # Временная сложность: O(1)
    # Пространственная сложность: O(1)
    def is_full(self):
        return self.count == self.capacity

    # Временная сложность: O(1)
    # Пространственная сложность: O(1)
    def enqueue(self, item):
        if self.is_full():
            return None

        self.queue[self.tail] = item
        self.tail = (self.tail + 1) % self.capacity
        self.count += 1

    # Временная сложность: O(1)
    # Пространственная сложность: O(1)
    def dequeue(self):
        if self.size() == 0:
            return None

        item = self.queue[self.head]
        self.queue[self.head] = None
        self.head = (self.head + 1) % self.capacity
        self.count -= 1

        return item


#  Рефлексия
# 1. Делал примерно так же, с учетной стоимостью append, но реаллокация по заполненному
# массиву, не из банка.

# 2. Не подумал про разложение на линейном массиве, совсем. Хотя он был на прошлой итерации.
# Получается, что мы должны хранить сам массив и каждое измерение, и далее просто прыгаем по каждому из них,
# Как по блокам.