import pytest
from simple_graph import SimpleGraph

def fill_vertices(g, n):
    for i in range(n):
        g.AddVertex(f"v{i}")

def indices_of(g, verts):
    index_map = {v: i for i, v in enumerate(g.vertex)}
    return [index_map[v] for v in verts]

def is_valid_path(g, path, v_from, v_to):
    if v_from is None or v_to is None:
        return False
    if not path:
        return False
    idx_path = indices_of(g, path)
    if idx_path[0] != v_from or idx_path[-1] != v_to:
        return False
    for a, b in zip(idx_path, idx_path[1:]):
        if not g.IsEdge(a, b):
            return False
    return True

def test_is_edge_checks_presence():
    g = SimpleGraph(3)
    fill_vertices(g, 3)
    assert g.IsEdge(0, 1) is False
    g.AddEdge(0, 1)
    assert g.IsEdge(0, 1) is True
    assert g.IsEdge(1, 0) is True
    assert g.IsEdge(2, 2) is False

def test_add_vertex_is_isolated():
    g = SimpleGraph(4)
    g.AddVertex("A")
    assert all(x == 0 for x in g.m_adjacency[0])
    assert all(row[0] == 0 for row in g.m_adjacency)
    g.AddVertex("B")
    assert g.IsEdge(0, 1) is False
    assert g.IsEdge(1, 0) is False

def test_add_edge_changes_state_from_absent_to_present():
    g = SimpleGraph(3)
    fill_vertices(g, 3)
    assert g.IsEdge(0, 2) is False
    g.AddEdge(0, 2)
    assert g.IsEdge(0, 2) is True
    assert g.IsEdge(2, 0) is True

def test_remove_edge_changes_state_from_present_to_absent():
    g = SimpleGraph(3)
    fill_vertices(g, 3)
    g.AddEdge(1, 2)
    assert g.IsEdge(1, 2) is True
    assert g.IsEdge(2, 1) is True
    g.RemoveEdge(1, 2)
    assert g.IsEdge(1, 2) is False
    assert g.IsEdge(2, 1) is False

def test_remove_vertex_clears_all_incident_edges():
    g = SimpleGraph(5)
    fill_vertices(g, 5)
    g.AddEdge(3, 0)
    g.AddEdge(1, 3)
    g.AddEdge(2, 3)
    g.AddEdge(3, 4)
    assert g.IsEdge(3, 0) and g.IsEdge(3, 4)
    assert g.IsEdge(1, 3) and g.IsEdge(2, 3)
    g.RemoveVertex(3)
    for i in range(g.max_vertex):
        assert g.m_adjacency[3][i] == 0
        assert g.m_adjacency[i][3] == 0
    assert g.IsEdge(3, 0) is False
    assert g.IsEdge(3, 4) is False
    assert g.IsEdge(1, 3) is False
    assert g.IsEdge(2, 3) is False

def test_add_edge_requires_existing_vertices():
    g = SimpleGraph(3)
    g.AddVertex("A")
    with pytest.raises(Exception):
        g.AddEdge(0, 1)

def test_index_bounds():
    g = SimpleGraph(2)
    fill_vertices(g, 2)
    with pytest.raises(Exception):
        g.IsEdge(-1, 0)
    with pytest.raises(Exception):
        g.IsEdge(0, 2)
    with pytest.raises(Exception):
        g.RemoveVertex(2)

def test_self_loop_on_add():
    g = SimpleGraph(2)
    fill_vertices(g, 2)
    g.AddEdge(1, 1)
    assert g.IsEdge(1, 1) is True
    assert g.m_adjacency[1][1] == 1

# ---------- DFS ----------

def test_dfs_same_vertex_returns_singleton():
    g = SimpleGraph(1)
    g.AddVertex("A")
    path = g.DepthFirstSearch(0, 0)
    assert len(path) == 1
    assert path[0] is g.vertex[0]

def test_dfs_linear_path_found():
    g = SimpleGraph(4)
    fill_vertices(g, 4)
    g.AddEdge(0, 1)
    g.AddEdge(1, 2)
    g.AddEdge(2, 3)
    path = g.DepthFirstSearch(0, 3)
    assert is_valid_path(g, path, 0, 3)
    assert [g.vertex[i] for i in [0, 1, 2, 3]] == path

def test_dfs_no_path_returns_empty():
    g = SimpleGraph(3)
    fill_vertices(g, 3)
    g.AddEdge(0, 1)
    path = g.DepthFirstSearch(0, 2)
    assert path == []

def test_dfs_handles_cycles_without_infinite_loop():
    g = SimpleGraph(4)
    fill_vertices(g, 4)
    g.AddEdge(0, 1)
    g.AddEdge(1, 2)
    g.AddEdge(2, 0)
    g.AddEdge(2, 3)
    path = g.DepthFirstSearch(0, 3)
    assert is_valid_path(g, path, 0, 3)

def test_dfs_resets_hits_between_runs():
    g = SimpleGraph(4)
    fill_vertices(g, 4)
    g.AddEdge(0, 1)
    g.AddEdge(0, 2)
    g.AddEdge(2, 3)
    p1 = g.DepthFirstSearch(0, 3)
    assert is_valid_path(g, p1, 0, 3)
    p2 = g.DepthFirstSearch(1, 3)
    assert is_valid_path(g, p2, 1, 3)

def test_dfs_invalid_indices_raise():
    g = SimpleGraph(3)
    fill_vertices(g, 2)
    with pytest.raises(Exception):
        g.DepthFirstSearch(-1, 1)
    with pytest.raises(Exception):
        g.DepthFirstSearch(0, 3)
    with pytest.raises(Exception):
        g.DepthFirstSearch(0, 2)

# ---------- BFS ----------

def test_bfs_same_vertex_returns_singleton():
    g = SimpleGraph(1)
    g.AddVertex("A")
    path = g.BreadthFirstSearch(0, 0)
    assert len(path) == 1
    assert path[0] is g.vertex[0]

def test_bfs_linear_path_is_shortest():
    g = SimpleGraph(5)
    fill_vertices(g, 5)
    g.AddEdge(0, 1)
    g.AddEdge(1, 2)
    g.AddEdge(2, 3)
    g.AddEdge(3, 4)
    path = g.BreadthFirstSearch(0, 4)
    assert is_valid_path(g, path, 0, 4)
    assert len(path) == 5

def test_bfs_picks_shortest_in_branching():
    g = SimpleGraph(6)
    fill_vertices(g, 6)
    g.AddEdge(0, 1)
    g.AddEdge(1, 5)
    g.AddEdge(0, 2)
    g.AddEdge(2, 3)
    g.AddEdge(3, 4)
    g.AddEdge(4, 5)
    path = g.BreadthFirstSearch(0, 5)
    assert is_valid_path(g, path, 0, 5)
    assert len(path) == 3

def test_bfs_no_path_returns_empty():
    g = SimpleGraph(4)
    fill_vertices(g, 4)
    g.AddEdge(0, 1)
    g.AddEdge(2, 3)
    path = g.BreadthFirstSearch(0, 3)
    assert path == []

def test_bfs_handles_cycles_without_infinite_loop():
    g = SimpleGraph(4)
    fill_vertices(g, 4)
    g.AddEdge(0, 1)
    g.AddEdge(1, 2)
    g.AddEdge(2, 0)
    g.AddEdge(1, 3)
    path = g.BreadthFirstSearch(0, 3)
    assert is_valid_path(g, path, 0, 3)
    assert len(path) == 3

def test_bfs_resets_hits_between_runs():
    g = SimpleGraph(5)
    fill_vertices(g, 5)
    g.AddEdge(0, 1)
    g.AddEdge(0, 2)
    g.AddEdge(2, 3)
    g.AddEdge(3, 4)
    p1 = g.BreadthFirstSearch(0, 4)
    assert is_valid_path(g, p1, 0, 4)
    p2 = g.BreadthFirstSearch(1, 4)
    assert is_valid_path(g, p2, 1, 4)

def test_bfs_invalid_indices_raise():
    g = SimpleGraph(3)
    fill_vertices(g, 2)
    with pytest.raises(Exception):
        g.BreadthFirstSearch(-1, 1)
    with pytest.raises(Exception):
        g.BreadthFirstSearch(0, 3)
    with pytest.raises(Exception):
        g.BreadthFirstSearch(0, 2)
