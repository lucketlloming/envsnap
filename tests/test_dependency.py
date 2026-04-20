"""Tests for envsnap.dependency."""

from __future__ import annotations

import pytest

from envsnap.dependency import (
    add_dependency,
    remove_dependency,
    get_dependencies,
    get_dependents,
    all_dependencies,
    DependencyError,
    SnapshotNotFoundError,
    CircularDependencyError,
)
from envsnap.storage import save_snapshot, get_snapshot_dir


@pytest.fixture(autouse=True)
def isolated_snapshot_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("envsnap.dependency.get_snapshot_dir", lambda: tmp_path)
    monkeypatch.setattr("envsnap.dependency.list_snapshots", lambda: list(_existing))
    monkeypatch.setattr("envsnap.storage.get_snapshot_dir", lambda: tmp_path)


_existing = set()


def _make(name: str):
    _existing.add(name)
    (pytest.importorskip("pathlib").Path.__new__(type(None))  # noqa: just ensure import)
    import pathlib
    (tmp := pathlib.Path("/tmp/envsnap_test"))
    # We rely on the monkeypatched list_snapshots


@pytest.fixture(autouse=True)
def reset_existing():
    _existing.clear()
    yield
    _existing.clear()


def _add_snap(*names):
    for n in names:
        _existing.add(n)


def test_add_and_get_dependency(tmp_path, monkeypatch):
    monkeypatch.setattr("envsnap.dependency.list_snapshots", lambda: list(_existing))
    monkeypatch.setattr("envsnap.dependency.get_snapshot_dir", lambda: tmp_path)
    _add_snap("a", "b")
    add_dependency("a", "b")
    assert get_dependencies("a") == ["b"]


def test_add_dependency_deduplicates(tmp_path, monkeypatch):
    monkeypatch.setattr("envsnap.dependency.list_snapshots", lambda: list(_existing))
    monkeypatch.setattr("envsnap.dependency.get_snapshot_dir", lambda: tmp_path)
    _add_snap("a", "b")
    add_dependency("a", "b")
    add_dependency("a", "b")
    assert get_dependencies("a") == ["b"]


def test_add_dependency_missing_snapshot_raises(tmp_path, monkeypatch):
    monkeypatch.setattr("envsnap.dependency.list_snapshots", lambda: list(_existing))
    monkeypatch.setattr("envsnap.dependency.get_snapshot_dir", lambda: tmp_path)
    _add_snap("a")
    with pytest.raises(SnapshotNotFoundError):
        add_dependency("a", "ghost")


def test_circular_dependency_raises(tmp_path, monkeypatch):
    monkeypatch.setattr("envsnap.dependency.list_snapshots", lambda: list(_existing))
    monkeypatch.setattr("envsnap.dependency.get_snapshot_dir", lambda: tmp_path)
    _add_snap("a", "b", "c")
    add_dependency("a", "b")
    add_dependency("b", "c")
    with pytest.raises(CircularDependencyError):
        add_dependency("c", "a")


def test_remove_dependency(tmp_path, monkeypatch):
    monkeypatch.setattr("envsnap.dependency.list_snapshots", lambda: list(_existing))
    monkeypatch.setattr("envsnap.dependency.get_snapshot_dir", lambda: tmp_path)
    _add_snap("a", "b")
    add_dependency("a", "b")
    remove_dependency("a", "b")
    assert get_dependencies("a") == []


def test_remove_missing_dependency_raises(tmp_path, monkeypatch):
    monkeypatch.setattr("envsnap.dependency.list_snapshots", lambda: list(_existing))
    monkeypatch.setattr("envsnap.dependency.get_snapshot_dir", lambda: tmp_path)
    _add_snap("a", "b")
    with pytest.raises(DependencyError):
        remove_dependency("a", "b")


def test_get_dependents(tmp_path, monkeypatch):
    monkeypatch.setattr("envsnap.dependency.list_snapshots", lambda: list(_existing))
    monkeypatch.setattr("envsnap.dependency.get_snapshot_dir", lambda: tmp_path)
    _add_snap("a", "b", "c")
    add_dependency("a", "b")
    add_dependency("c", "b")
    assert sorted(get_dependents("b")) == ["a", "c"]


def test_all_dependencies(tmp_path, monkeypatch):
    monkeypatch.setattr("envsnap.dependency.list_snapshots", lambda: list(_existing))
    monkeypatch.setattr("envsnap.dependency.get_snapshot_dir", lambda: tmp_path)
    _add_snap("a", "b", "c")
    add_dependency("a", "b")
    add_dependency("a", "c")
    result = all_dependencies()
    assert result == {"a": ["b", "c"]}
