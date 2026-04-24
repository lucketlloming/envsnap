"""Tests for envsnap.snapshot_graph."""
import json
import pytest
from unittest.mock import patch

from envsnap.snapshot_graph import build_graph, format_graph, GraphNode
from envsnap.dependency import SnapshotNotFoundError


ALL_SNAPS = ["alpha", "beta", "gamma"]

DEPS = {
    "alpha": [],
    "beta": ["alpha"],
    "gamma": ["alpha", "beta"],
}


def _patch(monkeypatch):
    monkeypatch.setattr("envsnap.snapshot_graph.list_snapshots", lambda: list(ALL_SNAPS))
    monkeypatch.setattr(
        "envsnap.snapshot_graph.get_dependencies",
        lambda name: DEPS.get(name, []),
    )


def test_build_graph_all_nodes(monkeypatch):
    _patch(monkeypatch)
    graph = build_graph()
    assert set(graph.keys()) == {"alpha", "beta", "gamma"}


def test_build_graph_dependencies_populated(monkeypatch):
    _patch(monkeypatch)
    graph = build_graph()
    assert graph["beta"].dependencies == ["alpha"]
    assert graph["gamma"].dependencies == ["alpha", "beta"]
    assert graph["alpha"].dependencies == []


def test_build_graph_dependents_populated(monkeypatch):
    _patch(monkeypatch)
    graph = build_graph()
    dependents_of_alpha = sorted(graph["alpha"].dependents)
    assert dependents_of_alpha == ["beta", "gamma"]
    assert sorted(graph["beta"].dependents) == ["gamma"]
    assert graph["gamma"].dependents == []


def test_build_graph_filtered_by_snapshot(monkeypatch):
    _patch(monkeypatch)
    graph = build_graph(snapshot_name="beta")
    # beta depends on alpha; gamma depends on beta — all three reachable
    assert "alpha" in graph
    assert "beta" in graph
    assert "gamma" in graph


def test_build_graph_isolated_snapshot(monkeypatch):
    monkeypatch.setattr("envsnap.snapshot_graph.list_snapshots", lambda: ["solo"])
    monkeypatch.setattr("envsnap.snapshot_graph.get_dependencies", lambda name: [])
    graph = build_graph(snapshot_name="solo")
    assert list(graph.keys()) == ["solo"]
    assert graph["solo"].dependencies == []
    assert graph["solo"].dependents == []


def test_build_graph_missing_snapshot_raises(monkeypatch):
    _patch(monkeypatch)
    with pytest.raises(SnapshotNotFoundError):
        build_graph(snapshot_name="nonexistent")


def test_format_graph_text(monkeypatch):
    _patch(monkeypatch)
    graph = build_graph()
    output = format_graph(graph, fmt="text")
    assert "[alpha]" in output
    assert "[beta]" in output
    assert "depends on" in output
    assert "required by" in output


def test_format_graph_json(monkeypatch):
    _patch(monkeypatch)
    graph = build_graph()
    output = format_graph(graph, fmt="json")
    data = json.loads(output)
    assert "alpha" in data
    assert data["beta"]["dependencies"] == ["alpha"]


def test_format_graph_empty():
    output = format_graph({}, fmt="text")
    assert "No snapshots" in output


def test_graph_node_as_dict():
    node = GraphNode(name="x", dependencies=["y"], dependents=["z"])
    d = node.as_dict()
    assert d == {"name": "x", "dependencies": ["y"], "dependents": ["z"]}
