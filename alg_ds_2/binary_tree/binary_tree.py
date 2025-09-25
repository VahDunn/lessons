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