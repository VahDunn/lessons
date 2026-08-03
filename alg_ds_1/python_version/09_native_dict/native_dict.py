from functools import reduce


# Задание на курсе: 9
# Название: ассоциативный массив
class NativeDictionary:

    def __init__(self, sz):
        self.size = sz
        self.step = 1
        self.slots = [None] * self.size
        self.values = [None] * self.size

    # Временная сложность: O(k), где k — длина ключа
    # Пространственная сложность: O(1)
    def hash_fun(self, key):
        return reduce(
            lambda hash_value, symbol: (
                hash_value * 31 + ord(symbol)
            ) % self.size,
            key,
            0,
        )

    # Временная сложность: O(1) в среднем, O(n) в худшем случае
    # Пространственная сложность: O(1)
    def put(self, key, value):
        slot = self._find_slot_for_put(key)

        if slot is None:
            return None

        self.slots[slot] = key
        self.values[slot] = value

        return slot

    # Временная сложность: O(1) в среднем, O(n) в худшем случае
    # Пространственная сложность: O(1)
    def is_key(self, key):
        return self._find_key_slot(key) is not None

    # Временная сложность: O(1) в среднем, O(n) в худшем случае
    # Пространственная сложность: O(1)
    def get(self, key):
        slot = self._find_key_slot(key)

        if slot is None:
            return None

        return self.values[slot]

    def _find_slot_for_put(self, key):
        slot = self.hash_fun(key)

        for _ in range(self.size):
            if self.slots[slot] is None:
                return slot

            if self.slots[slot] == key:
                return slot

            slot = (slot + self.step) % self.size

        return None

    def _find_key_slot(self, key):
        slot = self.hash_fun(key)

        for _ in range(self.size):
            if self.slots[slot] == key:
                return slot

            if self.slots[slot] is None:
                return None

            slot = (slot + self.step) % self.size

        return None
