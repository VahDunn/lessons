from functools import reduce


# Задание на курсе: 9
# Задача: 5
# Название: словарь с упорядоченными ключами
class OrderedDictionary:

    def __init__(self):
        self.keys = []
        self.values = []

    # Временная сложность: O(n)
    # Пространственная сложность: O(1), O(n) при реаллокации
    def put(self, key, value):
        index, found = self._find_position(key)

        if found:
            self.values[index] = value
            return index

        self.keys.insert(index, key)
        self.values.insert(index, value)

        return index

    # Временная сложность: O(log n)
    # Пространственная сложность: O(1)
    def is_key(self, key):
        _, found = self._find_position(key)

        return found

    # Временная сложность: O(log n)
    # Пространственная сложность: O(1)
    def get(self, key):
        index, found = self._find_position(key)

        if not found:
            return None

        return self.values[index]

    # Временная сложность: O(n)
    # Пространственная сложность: O(1)
    def delete(self, key):
        index, found = self._find_position(key)

        if not found:
            return False

        self.keys.pop(index)
        self.values.pop(index)

        return True

    def _find_position(self, key):
        left = 0
        right = len(self.keys)

        while left < right:
            middle = (left + right) // 2

            if self.keys[middle] < key:
                left = middle + 1
                continue

            right = middle

        found = left < len(self.keys) and self.keys[left] == key

        return left, found


# Задание на курсе: 9
# Задача: 6
# Название: словарь с битовыми ключами фиксированной длины
class BitStringDictionary:

    def __init__(self, bit_length):
        self.bit_length = bit_length
        self.values = [None] * (1 << self.bit_length)
        self.occupied = 0

    # Временная сложность: O(k), для фиксированного k — O(1)
    # Пространственная сложность: O(1)
    def put(self, key, value):
        index = self._key_to_index(key)
        self.values[index] = value
        self.occupied |= 1 << index

        return index

    # Временная сложность: O(k), для фиксированного k — O(1)
    # Пространственная сложность: O(1)
    def is_key(self, key):
        index = self._key_to_index(key)

        return bool(self.occupied & 1 << index)

    # Временная сложность: O(k), для фиксированного k — O(1)
    # Пространственная сложность: O(1)
    def get(self, key):
        index = self._key_to_index(key)

        if not self.occupied & 1 << index:
            return None

        return self.values[index]

    # Временная сложность: O(k), для фиксированного k — O(1)
    # Пространственная сложность: O(1)
    def delete(self, key):
        index = self._key_to_index(key)

        if not self.occupied & 1 << index:
            return False

        self.values[index] = None
        self.occupied &= ~(1 << index)

        return True

    def _key_to_index(self, key):
        if len(key) != self.bit_length:
            raise ValueError('Invalid bit key length')

        is_binary = all(map(lambda symbol: symbol in '01', key))

        if not is_binary:
            raise ValueError('Bit key must contain only 0 and 1')

        return reduce(
            lambda result, symbol: (
                result << 1
            ) | (ord(symbol) - ord('0')),
            key,
            0,
        )


# Рекомендации по решению задач задания 7.
# Слиение списков аналогично обычному, но сортировать не надо.
# Про подсписок - проверяем порядок, потом проверяем элементы, на каждую пароу сопоставление
# Само сопоставление вынес в метод-хелпер.
# Из-за упорядоченности с частотой встречания все просто - либо сброс либо инкремент + сохранение максимума.
# А вот по поводу индекса нюанс.
# Оптимум бинарный поиск, но он требует индекса, для "настоящего" линкед листа только O(n).