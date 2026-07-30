import ctypes


class DynArray:

    def __init__(self):
        self.count = 0
        self.capacity = 16
        self.array = self.make_array(self.capacity)

    def __len__(self):
        return self.count

    def make_array(self, new_capacity):
        return (new_capacity * ctypes.py_object)()

    def __getitem__(self, i):
        if i < 0 or i >= self.count:
            raise IndexError('Index is out of bounds')

        return self.array[i]

    def resize(self, new_capacity):
        new_array = self.make_array(new_capacity)

        for i in range(self.count):
            new_array[i] = self.array[i]

        self.array = new_array
        self.capacity = new_capacity

    def append(self, itm):
        if self.count == self.capacity:
            self.resize(2 * self.capacity)

        self.array[self.count] = itm
        self.count += 1

    # Задание на курсе: 3
    # Задача: 1
    # Название: вставка элемента по индексу
    # Временная сложность: O(n)
    # Пространственная сложность: O(n) при реаллокации, без нее O(1)
    def insert(self, i, itm):
        if i < 0 or i > self.count:
            raise IndexError('Index is out of bounds')

        if i == self.count:
            self.append(itm)
            return

        if self.count == self.capacity:
            self.resize(2 * self.capacity)

        for index in range(self.count, i, -1):
            self.array[index] = self.array[index - 1]

        self.array[i] = itm
        self.count += 1

    # Задание на курсе: 3
    # Задача: 2
    # Название: удаление элемента по индексу
    # Временная сложность: O(n)
    # Пространственная сложность: O(n) при реаллокации, без нее O(1)
    def delete(self, i):
        if i < 0 or i >= self.count:
            raise IndexError('Index is out of bounds')

        for index in range(i, self.count - 1):
            self.array[index] = self.array[index + 1]

        self.count -= 1
        self.array[self.count] = None

        if self.count * 2 >= self.capacity:
            return

        new_capacity = max(16, int(self.capacity / 1.5))

        if new_capacity == self.capacity:
            return

        self.resize(new_capacity)
