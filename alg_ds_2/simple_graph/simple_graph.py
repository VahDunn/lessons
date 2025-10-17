class Vertex:

    def __init__(self, val):
        self.Value = val

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