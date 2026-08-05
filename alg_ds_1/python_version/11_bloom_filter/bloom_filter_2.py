from functools import reduce
from operator import attrgetter, or_

from bloom_filter import BloomFilter


# Задание на курсе: 11
# Задача: 2
# Название: слияние фильтров Блюма
# Временная сложность: O(n), где n — количество фильтров
# Пространственная сложность: O(1)
def merge_filters(filters):
    if len(filters) == 0:
        raise ValueError('At least one filter is required')

    filter_len = filters[0].filter_len
    same_length = all(map(
        lambda bloom_filter: bloom_filter.filter_len == filter_len,
        filters,
    ))

    if not same_length:
        raise ValueError('Filters must have the same length')

    result = BloomFilter(filter_len)
    bit_arrays = map(attrgetter('bit_array'), filters)
    result.bit_array = reduce(or_, bit_arrays, 0)

    return result


# При слиянии количество установленных битов не уменьшается, поэтому вероятность
# ложноположительного результата возрастает. Для k функций, m битов и n добавленных
# значений она приближённо равна (1 - exp(-k * n / m)) ** k (гугл).


# Задание на курсе: 11
# Задача: 3
# Название: считающий фильтр Блюма с удалением
class CountingBloomFilter(BloomFilter):

    def __init__(self, f_len):
        super().__init__(f_len)
        self.counters = [0] * self.filter_len

    # Временная сложность: O(n), где n — длина строки
    # Пространственная сложность: O(1)
    def add(self, str1):
        list(map(self._increment, self._hashes(str1)))

    # Временная сложность: O(n), где n — длина строки
    # Пространственная сложность: O(1)
    def remove(self, str1):
        if not self.is_value(str1):
            return False

        list(map(self._decrement, self._hashes(str1)))

        return True

    def _increment(self, index):
        self.counters[index] += 1
        self._set_bit(index)

    def _decrement(self, index):
        if self.counters[index] == 0:
            return

        self.counters[index] -= 1

        if self.counters[index] > 0:
            return

        self._clear_bit(index)


# Задание на курсе: 11
# Задача: 4
# Название: восстановление возможных исходных значений
# Временная сложность: O(c * n), где c — количество кандидатов
# Пространственная сложность: O(c)
def recover_possible_values(bloom_filter, candidates):
    return list(filter(bloom_filter.is_value, candidates))


# Без заранее заданного множества кандидатов восстановление невозможно: фильтр
# хранит только объединённые позиции битов и не сохраняет сами строки.
#
# Очень крутая штука, которую я в прошлый раз не до конца понял (сам фильтр)

# Рефлексия
# Я сразу сортировал оба массива, за счет чего получил логарифмическую сложность.
# Но так операции добавления дороже. Но зато get сильно быстрее :)
