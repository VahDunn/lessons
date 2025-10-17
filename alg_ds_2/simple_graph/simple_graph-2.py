from simple_graph import SimpleGraph

class SimpleGraph2(SimpleGraph):

    def AddEdge(self, v1, v2):
        # проверяем, что обе вершины существуют
        self._check_exists(v1)
        self._check_exists(v2)
        if v1 == v2:
            return
        if self.m_adjacency[v1][v2] == 0:
            self.m_adjacency[v1][v2] = 1


    def RemoveEdge(self, v1, v2):
        self._check_index(v1)
        self._check_index(v2)
        if v1 == v2:
            return
        if self.m_adjacency[v1][v2] != 0:
            self.m_adjacency[v1][v2] = 0

    def is_cyclic(self) -> bool:
        WHITE, GRAY, BLACK = 0, 1, 2
        color = [WHITE] * self.max_vertex
        active = [i for i, v in enumerate(self.vertex) if v is not None]

        def dfs(u: int) -> bool:
            color[u] = GRAY
            for v in active:
                if self.m_adjacency[u][v] == 0:
                    continue
                if color[v] == GRAY:
                    return True
                if color[v] == WHITE and dfs(v):
                    return True
            color[u] = BLACK
            return False

        for u in active:
            if color[u] == WHITE and dfs(u):
                return True
        return False