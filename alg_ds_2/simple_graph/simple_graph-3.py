import pytest
from simple_graph import SimpleGraph

def fill_vertices(g, n):
    for i in range(n):
        g.AddVertex(f"v{i}")

def test_is_edge_checks_presence():
    g = SimpleGraph(3)
    fill_vertices(g, 3)
    assert g.IsEdge(0, 1) is False
    g.AddEdge(0, 1)
    assert g.IsEdge(0, 1) is True
    assert g.IsEdge(1, 0) is False
    assert g.IsEdge(2, 2) is False

def test_add_vertex_is_isolated():
    g = SimpleGraph(4)
    g.AddVertex("A")
    assert all(x == 0 for x in g.m_adjacency[0])
    assert all(row[0] == 0 for row in g.m_adjacency)

    g.AddVertex("B")  # индекс 1
    assert g.IsEdge(0, 1) is False
    assert g.IsEdge(1, 0) is False

def test_add_edge_changes_state_from_absent_to_present():
    g = SimpleGraph(3)
    fill_vertices(g, 3)
    assert g.IsEdge(0, 2) is False
    g.AddEdge(0, 2)
    assert g.IsEdge(0, 2) is True

def test_remove_edge_changes_state_from_present_to_absent():
    g = SimpleGraph(3)
    fill_vertices(g, 3)
    g.AddEdge(1, 2)
    assert g.IsEdge(1, 2) is True
    g.RemoveEdge(1, 2)
    assert g.IsEdge(1, 2) is False

def test_remove_vertex_clears_all_incident_edges():
    g = SimpleGraph(5)
    fill_vertices(g, 5)
    g.AddEdge(3, 0)  # исходящее от 3
    g.AddEdge(1, 3)  # входящее в 3
    g.AddEdge(2, 3)  # входящее в 3
    g.AddEdge(3, 4)  # исходящее от 3

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
    g.AddVertex("A")           # только 0 существует
    with pytest.raises(Exception):
        g.AddEdge(0, 1)        # вершина 1 ещё не добавлена

def test_index_bounds():
    g = SimpleGraph(2)
    fill_vertices(g, 2)
    with pytest.raises(Exception):
        g.IsEdge(-1, 0)
    with pytest.raises(Exception):
        g.IsEdge(0, 2)
    with pytest.raises(Exception):
        g.RemoveVertex(2)

def test_no_self_loops_on_add():
    g = SimpleGraph(2)
    fill_vertices(g, 2)
    g.AddEdge(1, 1)            # игнорируется
    assert g.IsEdge(1, 1) is False
    assert g.m_adjacency[1][1] == 0
