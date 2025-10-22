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

    def is_connected(self) -> bool:
        active = [i for i, v in enumerate(self.vertex) if v is not None]
        if len(active) <= 1:
            return True

        start = active[0]
        seen = set([start])
        stack = [start]

        while stack:
            u = stack.pop()
            for v in active:
                if u == v:
                    continue
                # считаем ребро, если есть дуга в любую сторону
                if (self.m_adjacency[u][v] == 1 or self.m_adjacency[v][u] == 1) and v not in seen:
                    seen.add(v)
                    stack.append(v)

        return len(seen) == len(active)

    def longest_simple_path_length(self) -> int:
        active = [i for i, v in enumerate(self.vertex) if v is not None]
        if not active:
            return 0

        def dfs(u: int, visited: set) -> int:
            # длина наилучшего пути, начинающегося в u (включая u)
            best = 1
            for v in active:
                if self.m_adjacency[u][v] == 1 and v not in visited:
                    visited.add(v)
                    best = max(best, 1 + dfs(v, visited))
                    visited.remove(v)
            return best

        answer = 1
        for s in active:
            answer = max(answer, dfs(s, {s}))
        return answer

