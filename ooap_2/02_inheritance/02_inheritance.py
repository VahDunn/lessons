class Stack:
    def __init__(self):
        self._items = []

    def push(self, item):
        self._items.append(item)

    def pop(self):
        return self._items.pop()


class Deque(Stack):

    def push_front(self, item):
        self._items.insert(0, item)

    def pop_front(self):
        return self._items.pop(0)

# Расширение - два доп. метода.


class BoundedStack(Stack):

    def __init__(self, capacity: int):
        super().__init__()
        self._capacity = capacity

    def push(self, item):
        if len(self._items) >= self._capacity:
            raise OverflowError("Stack is full")

        super().push(item)

# Сужение - более частный случай, с capacity.
# Пытался привести примеры из жизни, но не получилось, пришлось идти за вдохновением на
# предыдущую часть курса :)