from simple_graph import SimpleGraph

class SimpleGraph2(SimpleGraph):

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