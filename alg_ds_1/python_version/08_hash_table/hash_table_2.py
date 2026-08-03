from hashlib import sha256

from hash_table import HashTable as BaseHashTable


# Задание на курсе: 8
# Задача: 3
# Название: динамическая хэш-таблица
class DynamicHashTable(BaseHashTable):

    def __init__(self, sz, stp, threshold=0.75):
        super().__init__(sz, stp)
        self.threshold = threshold
        self.count = 0

    # Временная сложность: амортизированная O(1), O(n) при увеличении
    # Пространственная сложность: O(1), O(n) при увеличении
    def put(self, value):
        if (self.count + 1) / self.size > self.threshold:
            self._resize()

        slot = super().put(value)

        if slot is None:
            self._resize()
            slot = super().put(value)

        if slot is None:
            return None

        self.count += 1

        return slot

    def _resize(self):
        values = [value for value in self.slots if value is not None]
        self.size *= 2
        self.slots = [None] * self.size
        self.count = 0

        for value in values:
            slot = BaseHashTable.put(self, value)

            if slot is None:
                raise RuntimeError('Failed to redistribute hash table')

            self.count += 1


# Задание на курсе: 8
# Задача: 4
# Название: хэш-таблица с несколькими хэш-функциями
# Несколько функций дают каждому значению больше независимых начальных слотов и
# уменьшают вероятность длинной цепочки коллизий. Цена — вычисление h хэшей и
# проверка до h слотов на каждом шаге пробирования.
class MultiHashTable(BaseHashTable):

    def __init__(self, sz, steps, hash_functions):
        self.size = sz
        self.steps = steps
        self.hash_functions = hash_functions
        self.slots = [None] * self.size

    # Временная сложность: O(1) в среднем, O(h * n) в худшем случае
    # Пространственная сложность: O(h)
    def seek_slot(self, value):
        for slot in self._candidate_slots(value):
            if self.slots[slot] is None:
                return slot

        return None

    # Временная сложность: O(1) в среднем, O(h * n) в худшем случае
    # Пространственная сложность: O(h)
    def find(self, value):
        for slot in self._candidate_slots(value):
            if self.slots[slot] == value:
                return slot

            if self.slots[slot] is None:
                return None

        return None

    def _candidate_slots(self, value):
        start_slots = [
            hash_function(value) % self.size
            for hash_function in self.hash_functions
        ]

        for attempt in range(self.size):
            for start_slot, step in zip(start_slots, self.steps):
                yield (start_slot + attempt * step) % self.size


# Задание на курсе: 8
# Задача: 5
# Название: хэш-таблица с солью
class SecureHashTable(BaseHashTable):

    def __init__(self, sz, stp, salt):
        super().__init__(sz, stp)
        self.salt = salt

    # Временная сложность: O(k), где k — длина строки
    # Пространственная сложность: O(k)
    def hash_fun(self, value):
        salted_value = f'{self.salt}{value}'.encode()
        digest = sha256(salted_value).digest()

        return int.from_bytes(digest, byteorder='big') % self.size


# Рефлексия
# Проверка строки на палиндром - да, через деку очень удобно, что впрочем и логично. Делал с добавлением и сравнением.
# А я просто сортированный список хранил... Ну и соответственно получается, что минимум всегда в начале.
# Но вот добавление/удаление работает за O(N)
# Присвоил массив как атрибут (но я уже раньше так делал). Абстракция над массивом получается.