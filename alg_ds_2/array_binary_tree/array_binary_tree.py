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


def build(input_list, start, end, index, res):
    if start >= end or index >= len(res):
        return
    mid = (start + end) // 2
    res[index] = input_list[mid]
    build(input_list, start, mid, 2 * index + 1, res)
    build(input_list, mid + 1, end, 2 * index + 2, res)

def GenerateBBSTArray(input_list: list):
    sorted_list = sorted(input_list)
    res = [None] * len(sorted_list)
    build(sorted_list, start=0, end=len(sorted_list), index=0, res=res)
    return res

