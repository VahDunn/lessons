import math
from heap import Heap

class Heap_2(Heap):

    def MaxInRange(self, low, high):
        best = None
        def dfs(i: int):
            nonlocal best
            if i >= self.size:
                return
            val = self.a[i]
            if val is None:
                return
            if val < low:
                return
            if low <= val <= high:
                if best is None or val > best:
                    best = val
                    if best == high:
                        return
            dfs(self._left(i))
            if best == high:
                return
            dfs(self._right(i))
        dfs(0)
        return best

# Логично воспользоваться свойством кучи, точнее - тем, что поддерево гарантировано меньше текущего элементы
# - если узел < low, всё поддерево < low -> можно не спускаться.
#           - если узел == high, это верхняя граница -> ответ найден.

    def AnyLessThan(self, x):
        def dfs(i: int):
            if i >= self.size:
                return None
            v = self.a[i]
            if v < x:
                return v
            left = dfs(self._left(i))
            if left is not None:
                return left
            return dfs(self._right(i))
        return dfs(0)

# В худшем случае мы обходим всю кучу, но в среднем выходим раньше
# для поиска точного значения куча не так удобна, как БСТ, но здесь это и не требуется

    def PeekMax(self):
        return -1 if self.size == 0 else self.a[0]

    def MergeFrom(self, other: "Heap"):
        total = self.size + other.size
        if total == 0:
            return

        if total == 1:
            new_depth = 0
        else:
            new_depth = math.ceil(math.log2(total + 1)) - 1
            new_depth = max(0, new_depth)

        merged = Heap()
        merged.MakeHeap([], new_depth)

        while self.size > 0 and other.size > 0:
            if self.PeekMax() >= other.PeekMax():
                merged.Add(self.GetMax())
            else:
                merged.Add(other.GetMax())

        while self.size > 0:
            merged.Add(self.GetMax())
        while other.size > 0:
            merged.Add(other.GetMax())

        self.a = merged.a
        self.size = merged.size

        # краевые случаи + сначала по двум "родительским кучам" итерируемся, а потом по остаткам былой роскоши
