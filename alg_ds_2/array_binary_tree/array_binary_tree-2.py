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
    # Поскольку дерево бинарное, нам достаточно подниматься по индексам родителей,
    # предварительно подняв более глубокий узел до уровня более мелкого - ниже уровня
    # родителя более мелкого узла НОП по определению лежать не может
    # Далее просто поднимаемся до пересечения - оно и будет НОП (если будет)
    # Преимуществом перед классической рекурсией является независимость от значений ключей -
    # мы работаем с индексами, которые гарантированно упорядочены в массиве (не могут не быть)
    # Плюс, глубина просто вычисляется по формуле - целая часть логарифма по основанию 2
    # Учитывая, что основание - двойка, можно как-то через биты посчитать, но я не придумал как
    # Также, если я все правильно понимаю, нам не нужно проверять,
    # в какой ветви дерева находятся узлы - они уже упорядочены

    def LowestCommonAncestor(self, key1, key2):
        if key1 is None or key2 is None:
            return None

        index_1 = self.FindKeyIndex(key1)
        index_2 = self.FindKeyIndex(key2)

        if index_1 is None or index_2 is None or index_1 < 0 or index_2 < 0:
            return None

        deepness_1, deepness_2 = 0, 0
        tmp = index_1
        while tmp > 0:
            tmp = (tmp - 1) // 2
            deepness_1 += 1

        tmp = index_2
        while tmp > 0:
            tmp = (tmp - 1) // 2
            deepness_2 += 1

        while deepness_1 > deepness_2:
            index_1 = (index_1 - 1) // 2
            deepness_1 -= 1

        while deepness_2 > deepness_1:
            index_2 = (index_2 - 1) // 2
            deepness_2 -= 1

        while index_1 != index_2:
            index_1 = (index_1 - 1) // 2
            index_2 = (index_2 - 1) // 2

        return index_1

    # получается просто линейный обход массива
    # тк массив хранит дерево как раз таки по уровням
    # круто!
    def WideAllNodes(self):
        res = []
        tree = self.Tree
        for i in range(len(tree)):
            val = tree[i]
            if val is not None:
                res.append(val)
        return res