class aBST:
    def __init__(self, depth):
        if depth < 0:
            raise ValueError("depth must be non-negative")
        tree_size = 2 ** (depth + 1) - 1
        self.Tree = [None] * tree_size

    def FindKeyIndex(self, key):
        if key is None:
            return None
        index = 0

        while index < len(self.Tree):
            node = self.Tree[index]
            if node is None:
                return -index
            if key == node:
                return index
            if key < node:
                index = 2 * index + 1
            if key > node:
                index = 2 * index + 2
        return None

    def AddKey(self, key):
        index = 0
        while index < len(self.Tree):
            node = self.Tree[index]
            if node is None:
                self.Tree[index] = key
                return index
            if key == node:
                return index
            if key < node:
                index = 2 * index + 1
            if key > node:
                index = 2 * index + 2
        return -1
        # индекс добавленного/существующего ключа или -1 если не удалось

    def _build_balanced_from_sorted(self, sorted_list):
        res = [None] * len(self.Tree)

        def build_range(start, end, idx):
            if start >= end or idx >= len(res):
                return
            mid = (start + end) // 2
            res[idx] = sorted_list[mid]
            build_range(start, mid, 2 * idx + 1)
            build_range(mid + 1, end, 2 * idx + 2)

        build_range(0, len(sorted_list), 0)
        self.Tree = res

    def RemoveKey(self, key):
        if self.FindKeyIndex(key) is None:
            return False
        keys = [x for x in self.Tree if x is not None]
        try:
            keys.remove(key)
        except ValueError:
            return False
        keys.sort()
        self._build_balanced_from_sorted(keys)
        return True

    def RemoveAll(self, key):
        keys = [x for x in self.Tree if x is not None and x != key]
        if len(keys) == sum(1 for x in self.Tree if x is not None):
            return 0
        keys.sort()
        self._build_balanced_from_sorted(keys)
        return 1


# Задание 4 - никак, B-tree уже отсортировано


