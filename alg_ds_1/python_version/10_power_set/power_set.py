from __future__ import annotations

from itertools import chain
from typing import Any, Iterable


class PowerSet:

    def __init__(self) -> None:
        self.storage: dict[Any, None] = {}

    # Временная сложность: O(1)
    # Пространственная сложность: O(1)
    def size(self) -> int:
        return len(self.storage)

    # Временная сложность: O(1) в среднем
    # Пространственная сложность: O(1)
    def put(self, value: Any) -> None:
        self.storage[value] = None

    # Временная сложность: O(1) в среднем
    # Пространственная сложность: O(1)
    def get(self, value: Any) -> bool:
        return value in self.storage

    # Временная сложность: O(1) в среднем
    # Пространственная сложность: O(1)
    def remove(self, value: Any) -> bool:
        if not self.get(value):
            return False

        self.storage.pop(value)

        return True

    # Временная сложность: O(n)
    # Пространственная сложность: O(n)
    def intersection(self, set2: PowerSet) -> PowerSet:
        values = filter(set2.get, self.storage)

        return self._from_values(values)

    # Временная сложность: O(n + m)
    # Пространственная сложность: O(n + m)
    def union(self, set2: PowerSet) -> PowerSet:
        values = chain(self.storage, set2.storage)

        return self._from_values(values)

    # Временная сложность: O(n)
    # Пространственная сложность: O(n)
    def difference(self, set2: PowerSet) -> PowerSet:
        values = filter(lambda value: not set2.get(value), self.storage)

        return self._from_values(values)

    # Временная сложность: O(m)
    # Пространственная сложность: O(1)
    def issubset(self, set2: PowerSet) -> bool:
        return all(map(self.get, set2.storage))

    # Временная сложность: O(n)
    # Пространственная сложность: O(1)
    def equals(self, set2: PowerSet) -> bool:
        if self.size() != set2.size():
            return False

        return self.issubset(set2)

    def _from_values(self, values: Iterable[Any]) -> PowerSet:
        result = type(self)()
        result.storage = dict.fromkeys(values)

        return result
