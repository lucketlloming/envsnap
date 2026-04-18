"""Tests for envsnap.notes."""

import pytest
from pathlib import Path

from envsnap.notes import set_note, get_note, remove_note, list_notes
from envsnap.storage import save_snapshot


@pytest.fixture
def isolated_snapshot_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVSNAP_DIR", str(tmp_path))
    import envsnap.storage as st
    monkeypatch.setattr(st, "get_snapshot_dir", lambda: tmp_path)
    import envsnap.notes as nm
    monkeypatch.setattr(nm, "get_snapshot_dir", lambda: tmp_path)
    monkeypatch.setattr(nm, "snapshot_path", lambda name, d=None: tmp_path / f"{name}.json")
    return tmp_path


def _make_snapshot(name: str, d: Path) -> None:
    save_snapshot(name, {"KEY": "val"}, snapshot_dir=d)


def test_set_and_get_note(isolated_snapshot_dir):
    d = isolated_snapshot_dir
    _make_snapshot("snap1", d)
    set_note("snap1", "my note", d)
    assert get_note("snap1", d) == "my note"


def test_get_note_missing_returns_none(isolated_snapshot_dir):
    d = isolated_snapshot_dir
    _make_snapshot("snap1", d)
    assert get_note("snap1", d) is None


def test_set_note_missing_snapshot_raises(isolated_snapshot_dir):
    d = isolated_snapshot_dir
    with pytest.raises(FileNotFoundError, match="snap_x"):
        set_note("snap_x", "note", d)


def test_remove_note(isolated_snapshot_dir):
    d = isolated_snapshot_dir
    _make_snapshot("snap1", d)
    set_note("snap1", "to remove", d)
    remove_note("snap1", d)
    assert get_note("snap1", d) is None


def test_remove_note_missing_raises(isolated_snapshot_dir):
    d = isolated_snapshot_dir
    _make_snapshot("snap1", d)
    with pytest.raises(KeyError, match="snap1"):
        remove_note("snap1", d)


def test_list_notes(isolated_snapshot_dir):
    d = isolated_snapshot_dir
    _make_snapshot("a", d)
    _make_snapshot("b", d)
    set_note("a", "note a", d)
    set_note("b", "note b", d)
    notes = list_notes(d)
    assert notes == {"a": "note a", "b": "note b"}


def test_overwrite_note(isolated_snapshot_dir):
    d = isolated_snapshot_dir
    _make_snapshot("snap1", d)
    set_note("snap1", "first", d)
    set_note("snap1", "second", d)
    assert get_note("snap1", d) == "second"
