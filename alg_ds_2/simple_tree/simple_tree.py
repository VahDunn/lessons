class SimpleTreeNode:
    def __init__(self, val, parent):
        self.NodeValue = val
        self.Parent = parent
        self.Children = []
        self.NodeLevel = 0


class SimpleTree:
    def __init__(self, root):
        self.Root = root

    def AddChild(self, ParentNode: SimpleTreeNode, NewChild: SimpleTreeNode):
        if ParentNode is None or NewChild is None:
            return
        NewChild.Parent = ParentNode
        ParentNode.Children.append(NewChild)

    def DeleteNode(self, NodeToDelete):
        if NodeToDelete is None:
            return
        if NodeToDelete.Parent is None:
            self.Root = None
            return
        p = NodeToDelete.Parent
        if NodeToDelete in p.Children:
            p.Children.remove(NodeToDelete)
        NodeToDelete.Parent = None

    def GetAllNodes(self):
        if self.Root is None:
            return []
        res = []
        stack = [self.Root]
        while stack:
            v = stack.pop()
            res.append(v)
            for c in reversed(v.Children):
                stack.append(c)
        return res

    def FindNodesByValue(self, val):
        return [n for n in self.GetAllNodes() if n.NodeValue == val]

    def MoveNode(self, OriginalNode, NewParent):
        if OriginalNode is None or NewParent is None or OriginalNode is NewParent:
            return
        p = NewParent
        while p is not None:
            if p is OriginalNode:
                return
            p = p.Parent
        if OriginalNode.Parent is not None:
            if OriginalNode in OriginalNode.Parent.Children:
                OriginalNode.Parent.Children.remove(OriginalNode)
        OriginalNode.Parent = NewParent
        NewParent.Children.append(OriginalNode)

    def Count(self):
        return len(self.GetAllNodes())

    def LeafCount(self):
        return sum(1 for n in self.GetAllNodes() if len(n.Children) == 0)

    def enum_nodes_levels(self):
        self._count_levels(self.Root)

    def _count_levels(self, node, level=0):
        if node is None:
            return
        node.NodeLevel = level
        for child in node.Children:
            self._count_levels(child, level + 1)

    def EvenTrees(self):
        if self.Root is None:
            return []
        if self.Count() % 2 == 1:
            return []
        cuts = []
        self._dfs_even(self.Root, cuts)
        return cuts

    def _dfs_even(self, node, cuts):
        size = 1
        for ch in node.Children:
            s = self._dfs_even(ch, cuts)
            if s % 2 == 0:
                cuts.append(node)
                cuts.append(ch)
            else:
                size += s
        return size

    def BalanceEvenBinary(self):
        if self.Root is None:
            return False
        nodes = self.GetAllNodes()
        if len(nodes) % 2 == 1:
            return False
        try:
            nodes_sorted = sorted(nodes, key=lambda n: int(n.NodeValue))
        except Exception:
            nodes_sorted = nodes[:]
        for n in nodes_sorted:
            n.Children = []
            n.Parent = None
        self.Root = nodes_sorted[0]
        for i, n in enumerate(nodes_sorted):
            li = 2 * i + 1
            ri = 2 * i + 2
            if li < len(nodes_sorted):
                left = nodes_sorted[li]
                left.Parent = n
                n.Children.append(left)
            if ri < len(nodes_sorted):
                right = nodes_sorted[ri]
                right.Parent = n
                n.Children.append(right)
        self.enum_nodes_levels()
        return True

    def EvenSubtreeCount(self, sub_root: SimpleTreeNode):
        if sub_root is None:
            return 0
        cnt = [0]
        self._dfs_even_count(sub_root, cnt)
        return cnt[0]

    def _dfs_even_count(self, node, cnt_box):
        size = 1
        for ch in node.Children:
            size += self._dfs_even_count(ch, cnt_box)
        if size % 2 == 0:
            cnt_box[0] += 1
        return size
