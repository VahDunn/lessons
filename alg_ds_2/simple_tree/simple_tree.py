class SimpleTreeNode:

    def __init__(self, val, parent):
        self.NodeValue = val  # значение в узле
        self.Parent = parent  # родитель или None для корня
        self.Children = []  # список дочерних узлов
        self.NodeLevel = 0


class SimpleTree:

    def __init__(self, root):
        self.Root = root  # корень, может быть None

    def AddChild(
            self,
            ParentNode: SimpleTreeNode,
            NewChild: SimpleTreeNode,
    ):
        ParentNode.Children.append(NewChild)
        NewChild.Parent = ParentNode

    def DeleteNode(self, NodeToDelete):
        NodeToDelete.Parent.Children.remove(
            NodeToDelete
        )
        NodeToDelete.Parent = None

    def GetAllNodes(self):
        result = []
        node = self.Root
        self.find_nodes(node, result)
        return result
    
    def find_nodes(self, node, result):
        result.append(node)
        for children_node in node.Children:
            self.find_nodes(children_node, result)

    def FindNodesByValue(self, val):
        result = []
        self._find_nodes_by_value(self.Root, val, result)
        return result

    def _find_nodes_by_value(self, node, val, result):
        if node.NodeValue == val:
            result.append(node)
        for child in node.Children:
            self._find_nodes_by_value(child, val, result)

    def MoveNode(self, OriginalNode, NewParent):
        OriginalNode.Parent.Children.remove(OriginalNode)
        OriginalNode.Parent = NewParent
        NewParent.Children.append(OriginalNode)
        

    def Count(self):
        return len(self.GetAllNodes())

    def LeafCount(self):
        return self._count_leaves(self.Root)
    
    def _count_leaves(self, node):
        if node is None:
            return 0
        if len(node.Children) == 0:
            return 1
        res = 0
        for child in node.Children:
            res += self._count_leaves(child)
        return res
    
    def enum_nodes_levels(self):
        return self._count_levels(self.Root)
        
    def _count_levels(self, node, level=0):
        if node is None:
            return
        node.NodeLevel = level
        level += 1
        for child in node.Children:
            self._count_levels(child, level)