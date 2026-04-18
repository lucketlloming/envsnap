"""Tests for envsnap.pin module."""

import pytest
from unittest.mock import patch
from pathlib import Path

from envsnap import pin as pin_mod
from envsnap.storage import save_snapshot


@pytest.fixture(autouse=True)
def isolated_snapshot_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("envsnap.storage._SNAPSHOT_DIR", tmp_path)
    monkeypatch.setattr("envsnap.pin.get_snapshot_dir", lambda: tmp_path)
    yield tmp_path


def _make_snapshot(name: str, data: dict | None = None):
    save_snapshot(name, data or {"KEY": "val"})


def test_set_and_get_pin(isolated_snapshot_dir):
    _make_snapshot("snap1")
    pin_mod.set_pin("default", "snap1")
    assert pin_mod.get_pin("default") == "snap1"


def test_set_pin_missing_snapshot_raises(isolated_snapshot_dir):
    with pytest.raises(Exception):
        pin_mod.set_pin("default", "nonexistent")


def test_remove_pin(isolated_snapshot_dir):
    _make_snapshot("snap1")
    pin_mod.set_pin("default", "snap1")
    pin_mod.remove_pin("default")
    assert pin_mod.get_pin("default") is None


def test_remove_missing_pin_raises(isolated_snapshot_dir):
    with pytest.raises(KeyError):
        pin_mod.remove_pin("ghost")


def test_list_pins(isolated_snapshot_dir):
    _make_snapshot("s1")
    _make_snapshot("s2")
    pin_mod.set_pin("a", "s1")
    pin_mod.set_pin("b", "s2")
    result = pin_mod.list_pins()
    assert result == {"a": "s1", "b": "s2"}


def test_resolve_pin(isolated_snapshot_dir):
    _make_snapshot("snap1", {"FOO": "bar"})
    pin_mod.set_pin("prod", "snap1")
    data = pin_mod.resolve_pin("prod")
    assert data["FOO"] == "bar"


def test_resolve_missing_pin_raises(isolated_snapshot_dir):
    with pytest.raises(KeyError):
        pin_mod.resolve_pin("missing")
