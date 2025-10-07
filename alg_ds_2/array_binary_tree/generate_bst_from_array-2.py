class BSTNode:
    def __init__(self, key, parent):
        self.NodeKey = key
        self.Parent = parent
        self.LeftChild = None
        self.RightChild = None
        self.Level = 0


class BalancedBST:
    def __init__(self):
        self.Root = None  # корень дерева

    def GenerateTree(self, a):
        if not a:
            self.Root = None
            return

        arr = sorted(a)
        self.Root = self._build(arr, 0, len(arr) - 1, parent=None, level=0)

    def IsBSTValid(self, root_node=None):
        root = root_node if root_node is not None else self.Root
        return self._is_bst_valid(root, lo=None, hi=None)

    def IsBalanced(self, root_node=None):
        root = root_node if root_node is not None else self.Root
        _, ok = self._height_and_balance(root)
        return ok


    def _build(self, arr, lo, hi, parent, level):
        if lo > hi:
            return None

        mid = (lo + hi) // 2
        node = BSTNode(arr[mid], parent)
        node.Level = level

        node.LeftChild = self._build(arr, lo, mid - 1, node, level + 1)
        node.RightChild = self._build(arr, mid + 1, hi, node, level + 1)
        return node

    def _is_bst_valid(self, node, lo, hi):
        if node is None:
            return True

        x = node.NodeKey
        if (lo is not None and x < lo) or (hi is not None and not (x < hi)):
            return False

        return (self._is_bst_valid(node.LeftChild, lo, x) and
                self._is_bst_valid(node.RightChild, x, hi))

    def _height_and_balance(self, node):
        if node is None:
            return -1, True
        hl, ok_l = self._height_and_balance(node.LeftChild)
        hr, ok_r = self._height_and_balance(node.RightChild)
        height = 1 + max(hl, hr)
        balanced_here = ok_l and ok_r and abs(hl - hr) <= 1
        return height, balanced_here
