from functools import reduce


_DELETED_SLOT = object()


# Задание на курсе: 12
# Название: нативный кэш
class NativeCache:

    def __init__(self, sz):
        if sz <= 0:
            raise ValueError('Cache size must be positive')

        self.size = sz
        self.step = 1
        self.slots = [None] * self.size
        self.values = [None] * self.size
        self.hits = [0] * self.size

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

    # Временная сложность: O(1) в среднем, O(n) при вытеснении
    # Пространственная сложность: O(1)
    def put(self, key, value):
        slot = self._find_key_slot(key)

        if slot is not None:
            self.values[slot] = value
            return slot

        slot = self._find_free_slot(key)

        if slot is None:
            self._evict_least_used()
            slot = self._find_free_slot(key)

        self._store(slot, key, value)

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

        self.hits[slot] += 1

        return self.values[slot]

    def _find_key_slot(self, key):
        slot = self.hash_fun(key)

        for _ in range(self.size):
            stored_key = self.slots[slot]

            if stored_key is None:
                return None

            if stored_key is not _DELETED_SLOT and stored_key == key:
                return slot

            slot = (slot + self.step) % self.size

        return None

    def _find_free_slot(self, key):
        slot = self.hash_fun(key)

        for _ in range(self.size):
            is_free = (
                self.slots[slot] is None
                or self.slots[slot] is _DELETED_SLOT
            )

            if is_free:
                return slot

            slot = (slot + self.step) % self.size

        return None

    def _evict_least_used(self):
        slot = min(range(self.size), key=self.hits.__getitem__)
        self.slots[slot] = _DELETED_SLOT
        self.values[slot] = None
        self.hits[slot] = 0

    def _store(self, slot, key, value):
        self.slots[slot] = key
        self.values[slot] = value
        self.hits[slot] = 0

# Рефлексия
# Декартово произведение сделал просто через оркестрацию функций ( product), но можно и
# итеративно. Про рекурсивное обобщение как-то не думал, но как будто там сложность растет
# по степени двойки.
#
# Bag по сути так и реализовал. Всегда считал, что это скорее частный случай словаря (и с тз когда так
# и есть), хотя по смыслу это действительно больше похоже на частный случай множества. Забавно.
#
# Со слиянием фильтров, насколько понимаю, основная проблема как раз в быстрой деградации в
# полное ложноположительное (хотя конечно это от наполненности зависит).
#
# Про счетный фильтр помнил с прошлого раза (только название :), пошел гуглить.
# Интересна сфера применения, интуитивно кажется, что какие-то прогнозы или исследования.
#
# На счет воссстановления - как понимаю это в любом случае "брутфорс с предварительной разведкой",
# то есть набираем n кандидатов, логически подходящих, а потом тестим. Но как-то это хз,
# учитывая ложноположительные срабатывания. Надо очень строго держать выборку.
