from alg_ds_2.simple_tree.simple_tree import SimpleTree, SimpleTreeNode


class SimpleTree2(SimpleTree):

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
