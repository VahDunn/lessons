
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

    def WideAllNodes(self):
        res = []
        if self.Root is None:
            return res

        q = [self.Root]
        i = 0
        while i < len(q):
            node = q[i]
            res.append(node)
            if node.LeftChild:
                q.append(node.LeftChild)
            if node.RightChild:
                q.append(node.RightChild)
            i += 1
        return res

    def DeepAllNodes(self, order):
        res = []
        match order:
            case 0:
                self._inorder(self.Root, res)
            case 1:
                self._postorder(self.Root, res)
            case 2:
                self._preorder(self.Root, res)
            case _:
                raise ValueError("order must be 0 (in-order), 1 (post-order), or 2 (pre-order)")
        return res

    def _inorder(self, node, res):
        if node is None:
            return
        self._inorder(node.LeftChild, res)
        res.append(node)
        self._inorder(node.RightChild, res)

    def _postorder(self, node, res):
        if node is None:
            return
        self._postorder(node.LeftChild, res)
        self._postorder(node.RightChild, res)
        res.append(node)

    def _preorder(self, node, res):
        if node is None:
            return
        res.append(node)
        self._preorder(node.LeftChild, res)
        self._preorder(node.RightChild, res)

    def Invert(self):
        self._invert(self.Root)

    def MaxLevelSum(self, by_key=True):
        if self.Root is None:
            return (-1, 0)

        q = [self.Root]
        i = 0
        level = 0
        best_level = 0
        best_sum = float("-inf")

        while i < len(q):
            level_size = len(q) - i
            cur_sum = 0

            for _ in range(level_size):
                node = q[i]
                i += 1

                if by_key:
                    cur_sum += node.NodeKey
                else:
                    val = node.NodeValue
                    if not isinstance(val, (int, float)):
                        raise TypeError("NodeValue должен быть числом, либо используйте by_key=True")
                    cur_sum += val

                if node.LeftChild:
                    q.append(node.LeftChild)
                if node.RightChild:
                    q.append(node.RightChild)

            if cur_sum > best_sum:
                best_sum = cur_sum
                best_level = level

            level += 1
        return (best_level, best_sum)

    def _invert(self, node):
        if node is None:
            return
        node.LeftChild, node.RightChild = node.RightChild, node.LeftChild
        self._invert(node.LeftChild)
        self._invert(node.RightChild)

def build(preL, preR, inL, inR, parent=None):
    if preL > preR:
        return None
    root_val = preorder[preL]
    in_pos = idx[root_val]
    left_size = in_pos - inL

    root = BSTNode(root_val, root_val, parent)
    root.LeftChild = build(preL + 1, preL + left_size, inL, in_pos - 1, root)
    root.RightChild = build(preL + left_size + 1, preR, in_pos + 1, inR, root)

    return root

def build_tree_from_pre_in(preorder, inorder):
    if len(preorder) != len(inorder):
        raise ValueError("Длины preorder и inorder должны совпадать")
    if not preorder:
        return None

    idx = {}
    for i, v in enumerate(inorder):
        if v in idx:
            raise ValueError("Нужны уникальные значения узлов для однозначного восстановления")
        idx[v] = i
    return build(0, len(preorder) - 1, 0, len(inorder) - 1, None)