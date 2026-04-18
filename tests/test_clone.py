"""Tests for envsnap.clone."""

from __future__ import annotations

import pytest

from envsnap.clone import clone_snapshot, SnapshotNotFoundError, SnapshotAlreadyExistsError
from envsnap.storage import save_snapshot, load_snapshot


@pytest.fixture(autouse=True)
def isolated_snapshot_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVSNAP_DIR", str(tmp_path))
    return tmp_path


def _save(name: str, data: dict) -> None:
    save_snapshot(name, data)


def test_clone_basic():
    _save("original", {"FOO": "bar", "BAZ": "qux"})
    result = clone_snapshot("original", "copy")
    assert result == {"FOO": "bar", "BAZ": "qux"}
    assert load_snapshot("copy") == {"FOO": "bar", "BAZ": "qux"}


def test_clone_with_overrides():
    _save("base", {"A": "1", "B": "2"})
    result = clone_snapshot("base", "derived", overrides={"B": "99", "C": "3"})
    assert result == {"A": "1", "B": "99", "C": "3"}
    assert load_snapshot("derived") == {"A": "1", "B": "99", "C": "3"}


def test_clone_missing_source_raises():
    with pytest.raises(SnapshotNotFoundError, match="'ghost'"):
        clone_snapshot("ghost", "copy")


def test_clone_destination_exists_raises():
    _save("src", {"X": "1"})
    _save("dst", {"Y": "2"})
    with pytest.raises(SnapshotAlreadyExistsError, match="'dst'"):
        clone_snapshot("src", "dst")


def test_clone_destination_exists_overwrite():
    _save("src", {"X": "1"})
    _save("dst", {"Y": "2"})
    result = clone_snapshot("src", "dst", overwrite=True)
    assert result == {"X": "1"}
    assert load_snapshot("dst") == {"X": "1"}


def test_clone_does_not_mutate_source():
    _save("source", {"K": "v"})
    clone_snapshot("source", "clone", overrides={"K": "changed"})
    assert load_snapshot("source") == {"K": "v"}
