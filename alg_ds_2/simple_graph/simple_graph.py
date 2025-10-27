class Vertex:

    def __init__(self, val):
        self.Value = val
        self.Hit = False

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
                v.Hit = False
        if VFrom == VTo:
            self.vertex[VFrom].Hit = True
            return [self.vertex[VFrom]]
        stack = [VFrom]
        self.vertex[VFrom].Hit = True
        while stack:
            current = stack[-1]
            moved = False
            for nxt in range(self.max_vertex):
                if self.m_adjacency[current][nxt] == 1 and self.vertex[nxt] is not None and not self.vertex[nxt].Hit:
                    self.vertex[nxt].Hit = True
                    stack.append(nxt)
                    if nxt == VTo:
                        return [self.vertex[i] for i in stack]
                    moved = True
                    break
            if not moved:
                stack.pop()
        return []

    def BreadthFirstSearch(self, VFrom, VTo):
        self._check_exists(VFrom)
        self._check_exists(VTo)
        for v in self.vertex:
            if v is not None:
                v.Hit = False
        if VFrom == VTo:
            self.vertex[VFrom].Hit = True
            return [self.vertex[VFrom]]
        parent = [None] * self.max_vertex
        q = [VFrom]
        self.vertex[VFrom].Hit = True
        while q:
            u = q.pop(0)
            if u == VTo:
                break
            for v in range(self.max_vertex):
                if self.m_adjacency[u][v] == 1 and self.vertex[v] is not None and not self.vertex[v].Hit:
                    self.vertex[v].Hit = True
                    parent[v] = u
                    q.append(v)
        if not self.vertex[VTo].Hit:
            return []
        path = []
        cur = VTo
        while cur is not None:
            path.append(self.vertex[cur])
            cur = parent[cur]
        return list(reversed(path))

    def WeakVertices(self):
        weak = []
        for i in range(self.max_vertex):
            if self.vertex[i] is None:
                continue
            neighbors = [
                j for j in range(self.max_vertex)
                if (
                        j != i
                        and self.m_adjacency[i][j] == 1
                        and self.vertex[j] is not None
                )
            ]
            found_triangle = False
            for a in range(len(neighbors)):
                for b in range(a + 1, len(neighbors)):
                    if self.m_adjacency[neighbors[a]][neighbors[b]] == 1:
                        found_triangle = True
                        break
                if found_triangle:
                    break
            if not found_triangle:
                weak.append(self.vertex[i])
        return weak
