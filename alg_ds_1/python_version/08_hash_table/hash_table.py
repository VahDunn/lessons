# Задание на курсе: 8
# Название: хэш-таблица с открытой адресацией
class HashTable:

    def __init__(self, sz, stp):
        self.size = sz
        self.step = stp
        self.slots = [None] * self.size

    # Название: вычисление индекса слота
    # Временная сложность: O(k), где k — длина строки
    # Пространственная сложность: O(1)
    def hash_fun(self, value):
        hash_value = 0

        for symbol in value:
            hash_value = (hash_value * 31 + ord(symbol)) % self.size

        return hash_value

    # Название: поиск свободного слота
    # Временная сложность: O(1) в среднем, O(n) в худшем случае
    # Пространственная сложность: O(1)
    def seek_slot(self, value):
        slot = self.hash_fun(value)

        for _ in range(self.size):
            if self.slots[slot] is None:
                return slot

            slot = (slot + self.step) % self.size

        return None

    # Название: добавление значения
    # Временная сложность: O(1) в среднем, O(n) в худшем случае
    # Пространственная сложность: O(1)
    def put(self, value):
        slot = self.seek_slot(value)

        if slot is None:
            return None

        self.slots[slot] = value

        return slot

    # Название: поиск значения
    # Временная сложность: O(1) в среднем, O(n) в худшем случае
    # Пространственная сложность: O(1)
    def find(self, value):
        slot = self.hash_fun(value)

        for _ in range(self.size):
            if self.slots[slot] == value:
                return slot

            if self.slots[slot] is None:
                return None

            slot = (slot + self.step) % self.size

        return None
