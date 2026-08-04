from functools import reduce


class BloomFilter:

    def __init__(self, f_len):
        if f_len <= 0:
            raise ValueError('Filter length must be positive')

        self.filter_len = f_len
        self.bit_array = 0

    # Временная сложность: O(n), где n — длина строки
    # Пространственная сложность: O(1)
    def hash1(self, str1):
        return self._hash(str1, 17)

    # Временная сложность: O(n), где n — длина строки
    # Пространственная сложность: O(1)
    def hash2(self, str1):
        return self._hash(str1, 223)

    # Временная сложность: O(n), где n — длина строки
    # Пространственная сложность: O(1)
    def add(self, str1):
        list(map(self._set_bit, self._hashes(str1)))

    # Временная сложность: O(n), где n — длина строки
    # Пространственная сложность: O(1)
    def is_value(self, str1):
        return all(map(self._is_bit_set, self._hashes(str1)))

    def _hash(self, value, multiplier):
        return reduce(
            lambda result, symbol: (
                result * multiplier + ord(symbol)
            ) % self.filter_len,
            value,
            0,
        )

    def _hashes(self, value):
        return self.hash1(value), self.hash2(value)

    def _set_bit(self, index):
        self.bit_array |= 1 << index

    def _clear_bit(self, index):
        self.bit_array &= ~(1 << index)

    def _is_bit_set(self, index):
        return bool(self.bit_array & 1 << index)
