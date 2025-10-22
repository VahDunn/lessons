class Vertex:

    def __init__(self, val):
        self.Value = val
        self.hit = False

class SimpleGraph:

    def __init__(self, size):
        self.max_vertex = size
        self.m_adjacency = [[0] * size for _ in range(size)]
        self.vertex = [None] * size

    def AddVertex(self, v):
        for i in range(self.max_vertex):
            if self.vertex[i] is None:
                self.vertex[i] = Vertex(v)
                return
        raise Exception(f"Graph of size {self.max_vertex} is full")

    def RemoveVertex(self, v):
        self._check_index(v)
        self.vertex[v] = None
        for i in range(self.max_vertex):
            self.m_adjacency[v][i] = 0
            self.m_adjacency[i][v] = 0

    def IsEdge(self, v1, v2):
        self._check_index(v1)
        self._check_index(v2)
        return self.m_adjacency[v1][v2] != 0

    def AddEdge(self, v1, v2):
        self._check_exists(v1)
        self._check_exists(v2)
        self.m_adjacency[v1][v2] = 1
        self.m_adjacency[v2][v1] = 1


    def RemoveEdge(self, v1, v2):
        self._check_index(v1)
        self._check_index(v2)
        self.m_adjacency[v1][v2] = 0
        self.m_adjacency[v2][v1] = 0

    def _check_exists(self, v):
        self._check_index(v)
        if self.vertex[v] is None:
            raise Exception(f"Vertex {v} does not exist")

    def _check_index(self, v):
        if not (0 <= v < self.max_vertex):
            raise Exception(f"Vertex {v} is out of range")

    def DepthFirstSearch(self, VFrom, VTo):
        self._check_exists(VFrom)
        self._check_exists(VTo)

        for v in self.vertex:
            if v is not None:
                v.hit = False

        if VFrom == VTo:
            self.vertex[VFrom].hit = True
            return [self.vertex[VFrom]]

        stack = []
        self.vertex[VFrom].hit = True
        stack.append(VFrom)

        while stack:
            current = stack[-1]

            moved = False
            for nxt in range(self.max_vertex):
                if self.m_adjacency[current][nxt] == 1 and self.vertex[nxt] is not None and not self.vertex[nxt].hit:
                    self.vertex[nxt].hit = True
                    stack.append(nxt)
                    if nxt == VTo:
                        return [self.vertex[i] for i in stack]
                    moved = True
                    break

            if not moved:
                stack.pop()

        return []
