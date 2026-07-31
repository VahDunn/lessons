class Stack:

    def __init__(self):
        self.stack = []

    # Название: количество элементов в стеке
    # Временная сложность: O(1)
    # Пространственная сложность: O(1)
    def size(self):
        return len(self.stack)

    # Название: удаление и возврат верхнего элемента
    # Временная сложность: O(n)
    # Пространственная сложность: O(1)
    def pop(self):
        if self.size() == 0:
            return None

        return self.stack.pop(0)

    # Название: добавление элемента на верхушку стека
    # Временная сложность: O(n)
    # Пространственная сложность: O(1), O(n) при реаллокации
    def push(self, value):
        self.stack.insert(0, value)

    # Название: возврат верхнего элемента без удаления
    # Временная сложность: O(1)
    # Пространственная сложность: O(1)
    def peek(self):
        if self.size() == 0:
            return None

        return self.stack[0]
