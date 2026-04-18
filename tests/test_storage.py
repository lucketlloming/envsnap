"""Tests for envsnap.storage module."""

import json
import pytest
from pathlib import Path
from envsnap.storage import save_snapshot, load_snapshot, list_snapshots, delete_snapshot


@pytest.fixture(autouse=True)
def isolated_snapshot_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVSNAP_DIR", str(tmp_path))


def test_save_and_load_snapshot():
    data = {"FOO": "bar", "BAZ": "qux"}
    save_snapshot("mysnap", data)
    loaded = load_snapshot("mysnap")
    assert loaded["name"] == "mysnap"
    assert loaded["variables"] == data
    assert "created_at" in loaded


def test_load_missing_snapshot_raises():
    with pytest.raises(FileNotFoundError, match="missing"):
        load_snapshot("missing")


def test_list_snapshots_empty():
    assert list_snapshots() == []


def test_list_snapshots_returns_names():
    save_snapshot("alpha", {"A": "1"})
    save_snapshot("beta", {"B": "2"})
    names = list_snapshots()
    assert set(names) == {"alpha", "beta"}


def test_delete_snapshot():
    save_snapshot("todelete", {"X": "y"})
    delete_snapshot("todelete")
    assert "todelete" not in list_snapshots()


def test_delete_missing_snapshot_raises():
    with pytest.raises(FileNotFoundError):
        delete_snapshot("ghost")
