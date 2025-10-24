from simple_graph import SimpleGraph

class SimpleGraph2(SimpleGraph):

    def AddEdge(self, v1, v2):
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
                if (self.m_adjacency[u][v] == 1 or self.m_adjacency[v][u] == 1) and v not in seen:
                    seen.add(v)
                    stack.append(v)

        return len(seen) == len(active)

    def longest_simple_path_length(self) -> int:
        active = [i for i, v in enumerate(self.vertex) if v is not None]
        if not active:
            return 0

        def dfs(u: int, visited: set) -> int:
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

    def tree_diameter_bfs(self) -> int:
        active = [i for i, v in enumerate(self.vertex) if v is not None]
        if len(active) <= 1:
            return 0

        def bfs_far(src: int):
            dist = {i: -1 for i in active}
            q = [src]
            dist[src] = 0
            while q:
                u = q.pop(0)
                for v in active:
                    if (self.m_adjacency[u][v] == 1 or self.m_adjacency[v][u] == 1) and dist[v] == -1:
                        dist[v] = dist[u] + 1
                        q.append(v)
            far = max(active, key=lambda x: dist[x])
            return far, dist

        a = active[0]
        u, _ = bfs_far(a)
        v, dist = bfs_far(u)
        return max(dist.values())

    def find_cycles_bfs(self):
        active = [i for i, v in enumerate(self.vertex) if v is not None]
        seen = set()
        cycles_set = set()
        cycles = []

        for start in active:
            if start in seen:
                continue
            parent = {start: None}
            dist = {start: 0}
            q = [start]
            seen.add(start)
            while q:
                u = q.pop(0)
                for v in active:
                    if not (self.m_adjacency[u][v] == 1 or self.m_adjacency[v][u] == 1):
                        continue
                    if v not in parent:
                        parent[v] = u
                        dist[v] = dist[u] + 1
                        q.append(v)
                        seen.add(v)
                    elif parent[u] != v and dist[v] < dist[u]:
                        key = self._reconstruct_cycle(u, v, parent)
                        if key not in cycles_set:
                            cycles_set.add(key)
                            cycles.append(list(key))
        return cycles

    @staticmethod
    def _reconstruct_cycle(u, v, parent):
        pu = []
        s = set()
        x = u
        while x is not None:
            pu.append(x)
            s.add(x)
            x = parent[x]
        pv = []
        y = v
        while y not in s:
            pv.append(y)
            y = parent[y]
        lca = y
        edges = []
        x = u
        while x != lca:
            p = parent[x]
            a, b = (x, p) if x < p else (p, x)
            edges.append((a, b))
            x = p
        path_down = list(reversed(pv))
        cur = lca
        for node in path_down:
            a, b = (cur, node) if cur < node else (node, cur)
            edges.append((a, b))
            cur = node
        a, b = (u, v) if u < v else (v, u)
        edges.append((a, b))
        return tuple(sorted(edges))

