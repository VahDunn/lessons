from __future__ import annotations

from functools import reduce
from itertools import product
from typing import Any

from power_set import PowerSet as BasePowerSet


class PowerSet(BasePowerSet):

    # Задание на курсе: 10
    # Задача: 4
    # Название: декартово произведение множеств
    # Временная сложность: O(n * m)
    # Пространственная сложность: O(n * m)
    def cartesian_product(self, set2: BasePowerSet) -> BasePowerSet:
        return self._from_values(product(self.storage, set2.storage))


# Задание на курсе: 10
# Задача: 5
# Название: пересечение трёх и более множеств
# Временная сложность: O(n1 + n2 + ... + nk)
# Пространственная сложность: O(n)
def intersection_many(sets: list[BasePowerSet]) -> BasePowerSet:
    if len(sets) < 3:
        raise ValueError('At least three sets are required')

    return reduce(
        lambda result, current: result.intersection(current),
        sets[1:],
        sets[0],
    )


# Задание на курсе: 10
# Задача: 6
# Название: мультимножество
class Bag:

    def __init__(self) -> None:
        self.storage: dict[Any, int] = {}

    # Временная сложность: O(1) в среднем
    # Пространственная сложность: O(1)
    def add(self, value: Any) -> None:
        self.storage[value] = self.storage.get(value, 0) + 1

    # Временная сложность: O(1) в среднем
    # Пространственная сложность: O(1)
    def remove(self, value: Any) -> bool:
        count = self.storage.get(value, 0)

        if count == 0:
            return False

        if count > 1:
            self.storage[value] = count - 1
            return True

        self.storage.pop(value)

        return True

    # Временная сложность: O(n)
    # Пространственная сложность: O(n)
    def get_frequencies(self) -> list[tuple[Any, int]]:
        return list(self.storage.items())

    # Временная сложность: O(n)
    # Пространственная сложность: O(1)
    def size(self) -> int:
        return sum(self.storage.values())
