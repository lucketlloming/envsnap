"""Tests for envsnap.namespace."""
from __future__ import annotations

import json
import pytest

from envsnap import storage
from envsnap.namespace import (
    NamespaceError,
    SnapshotNotFoundError,
    add_to_namespace,
    delete_namespace,
    get_namespace,
    list_namespaces,
    remove_from_namespace,
)


@pytest.fixture(autouse=True)
def isolated_snapshot_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "get_snapshot_dir", lambda: tmp_path)
    return tmp_path


def _make_snapshot(tmp_path, name: str) -> None:
    snap_file = tmp_path / f"{name}.json"
    snap_file.write_text(json.dumps({"KEY": "val"}))


def test_add_and_get_namespace(tmp_path):
    _make_snapshot(tmp_path, "snap1")
    add_to_namespace("dev", "snap1")
    assert get_namespace("dev") == ["snap1"]


def test_add_deduplicates(tmp_path):
    _make_snapshot(tmp_path, "snap1")
    add_to_namespace("dev", "snap1")
    add_to_namespace("dev", "snap1")
    assert get_namespace("dev") == ["snap1"]


def test_add_missing_snapshot_raises(tmp_path):
    with pytest.raises(SnapshotNotFoundError):
        add_to_namespace("dev", "ghost")


def test_add_empty_namespace_raises(tmp_path):
    _make_snapshot(tmp_path, "snap1")
    with pytest.raises(NamespaceError):
        add_to_namespace("  ", "snap1")


def test_remove_from_namespace(tmp_path):
    _make_snapshot(tmp_path, "snap1")
    add_to_namespace("dev", "snap1")
    remove_from_namespace("dev", "snap1")
    assert get_namespace("dev") == []


def test_remove_cleans_empty_namespace(tmp_path):
    _make_snapshot(tmp_path, "snap1")
    add_to_namespace("dev", "snap1")
    remove_from_namespace("dev", "snap1")
    assert "dev" not in list_namespaces()


def test_remove_not_member_raises(tmp_path):
    _make_snapshot(tmp_path, "snap1")
    with pytest.raises(NamespaceError):
        remove_from_namespace("dev", "snap1")


def test_list_namespaces(tmp_path):
    _make_snapshot(tmp_path, "snap1")
    _make_snapshot(tmp_path, "snap2")
    add_to_namespace("dev", "snap1")
    add_to_namespace("prod", "snap2")
    names = list_namespaces()
    assert set(names) == {"dev", "prod"}


def test_delete_namespace(tmp_path):
    _make_snapshot(tmp_path, "snap1")
    add_to_namespace("dev", "snap1")
    delete_namespace("dev")
    assert "dev" not in list_namespaces()


def test_delete_missing_namespace_raises():
    with pytest.raises(NamespaceError):
        delete_namespace("nonexistent")
