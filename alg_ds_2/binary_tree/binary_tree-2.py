class BSTNode:

    def __init__(self, key, val, parent):
        self.NodeKey = key  # ключ узла
        self.NodeValue = val  # значение в узле
        self.Parent = parent  # родитель или None для корня
        self.LeftChild = None  # левый потомок
        self.RightChild = None  # правый потомок


class BSTFind:  # промежуточный результат поиска

    def __init__(self):
        self.Node = None  # None если
        # в дереве вообще нету узлов

        self.NodeHasKey = False  # True если узел найден
        self.ToLeft = False  # True, если родительскому узлу надо
        # добавить новый узел левым потомком


class BST:

    def __init__(self, node):
        self.Root = node  # корень дерева, или None

    def FindNodeByKey(self, key):
        return self._find_by_key(self.Root, key, None)

    def _find_by_key(self, node: BSTNode, key, parent):
        result = BSTFind()
        if node is None:
            result.Node = parent
            result.NodeHasKey = False
            if parent is not None:
                result.ToLeft = key < parent.NodeKey
            return result

        if key == node.NodeKey:
            result.Node = node
            result.NodeHasKey = True
            return result

        if key < node.NodeKey:
            return self._find_by_key(node.LeftChild, key, node)
        else:
            return self._find_by_key(node.RightChild, key, node)

    def AddKeyValue(self, key, val):
        find_result = self.FindNodeByKey(key)
        if find_result.NodeHasKey:
            return False  # если ключ уже есть
        parent_node = find_result.Node
        new_node = BSTNode(key, val, parent_node)
        if not parent_node:
            self.Root = new_node
            return new_node
        if find_result.ToLeft:
            parent_node.LeftChild = new_node
            return new_node
        parent_node.RightChild = new_node
        return new_node

    def FinMinMax(self, FromNode, FindMax):
        if not self.Root:
            return None
        if not FromNode:
            node = self.Root
        else:
            find_result = self.FindNodeByKey(FromNode.NodeKey)
            if find_result.NodeHasKey:
                node = find_result.Node
            else:
                node = None
        if not node:
            return None
        child = node.RightChild if FindMax else node.LeftChild
        if not child:
            return node
        return self.FinMinMax(child, FindMax)

    def DeleteNodeByKey(self, key):
        find_result = self.FindNodeByKey(key)
        if not find_result.NodeHasKey:
            return False
        return self._recursive_delete(key, 0)

    def _recursive_delete(self, key, recursive_level):
        if self.Root is None:
            return False
        if key < self.Root.NodeKey:
            self.Root.LeftChild = BST(self.Root.LeftChild)._recursive_delete(
                key, recursive_level=recursive_level + 1
            )
        elif key > self.Root.NodeKey:
            self.Root.RightChild = BST(self.Root.RightChild)._recursive_delete(
                key, recursive_level=recursive_level + 1
            )
        else:
            if (
                    recursive_level == 0
                    and self.Root.LeftChild is None
                    and self.Root.RightChild is None
            ):
                temp = self.Root
                self.Root = None
                return temp
            if self.Root.LeftChild is None:
                if self.Root.RightChild:
                    self.Root.RightChild.Parent = self.Root.Parent
                self.Root = self.Root.RightChild
                return self.Root
            elif self.Root.RightChild is None:
                temp = self.Root.LeftChild
                temp.Parent = self.Root.Parent
                self.Root = temp
                return self.Root

            temp = self.FinMinMax(self.Root.RightChild, FindMax=False)

            self.Root.NodeKey = temp.NodeKey

            self.Root.RightChild = BST(self.Root.RightChild)._recursive_delete(
                temp.NodeKey, recursive_level=recursive_level + 1
            )

        return self.Root

    def Count(self):
        if self.Root is None:
            return 0
        return 1 + BST(self.Root.LeftChild).Count() + BST(self.Root.RightChild).Count()

    # 1) Идентичность деревьев
    def IsIdentical(self, other) -> bool:
        if other is None:
            return False
        return self._eq_nodes(self.Root, other.Root)

    def _eq_nodes(self, n1: BSTNode, n2: BSTNode) -> bool:
        if n1 is None and n2 is None:
            return True
        if n1 is None or n2 is None:
            return False
        if n1.NodeKey != n2.NodeKey or n1.NodeValue != n2.NodeValue:
            return False
        return self._eq_nodes(n1.LeftChild, n2.LeftChild) and \
            self._eq_nodes(n1.RightChild, n2.RightChild)
    # здесь ничего сложного (на мой взгляд) не было - просто параллельное
    # прохождение всех узлов каждого дерева и их сопоставление с ранними выходами

    # 2) Пути заданной длины (в узлах) от корня до листьев
    def PathsWithLength(self, length_nodes: int):
        result = []
        if self.Root is None:
            return result
        self._collect_paths_with_length(self.Root, length_nodes, [], result)
        return result

    def _collect_paths_with_length(self, node: BSTNode, target_len: int,
                                   path: list, result: list):
        if node is None:
            return
        path.append(node.NodeKey)
        if node.LeftChild is None and node.RightChild is None:
            if len(path) == target_len:
                result.append(list(path))
        else:
            if len(path) < target_len:
                self._collect_paths_with_length(node.LeftChild, target_len, path, result)
                self._collect_paths_with_length(node.RightChild, target_len, path, result)
        path.pop()

    # 3) Все корне-листовые пути с максимальной суммой NodeValue
    def MaxSumRootToLeafPaths(self):
        if self.Root is None:
            return (None, [])
        return self._max_sum_recursive(self.Root, [], 0)

    def _max_sum_recursive(self, node: BSTNode, path: list, sum_so_far: int):
        if node is None:
            return (None, [])
        new_sum = sum_so_far + node.NodeValue
        path.append(node.NodeKey)

        if node.LeftChild is None and node.RightChild is None:
            res = (new_sum, [list(path)])
            path.pop()
            return res

        left_sum, left_paths = self._max_sum_recursive(node.LeftChild, path, new_sum)
        right_sum, right_paths = self._max_sum_recursive(node.RightChild, path, new_sum)
        path.pop()
        if left_sum is None:
            return (right_sum, right_paths)
        if right_sum is None:
            return (left_sum, left_paths)
        if left_sum > right_sum:
            return (left_sum, left_paths)
        if right_sum > left_sum:
            return (right_sum, right_paths)
        return (left_sum, left_paths + right_paths)

    # 4) Симметричность относительно корня
    def IsSymmetric(self) -> bool:
        if self.Root is None:
            return True
        return self._mirror(self.Root.LeftChild, self.Root.RightChild)

    def _mirror(self, a: BSTNode, b: BSTNode) -> bool:
        if a is None and b is None:
            return True
        if a is None or b is None:
            return False
        if a.NodeKey != b.NodeKey or a.NodeValue != b.NodeValue:
            return False
        return self._mirror(a.LeftChild, b.RightChild) and \
            self._mirror(a.RightChild, b.LeftChild)