"""Tests for envsnap.alias."""

import pytest
from pathlib import Path

from envsnap import alias as alias_mod
from envsnap.storage import save_snapshot


@pytest.fixture(autouse=True)
def isolated_snapshot_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("envsnap.storage.get_snapshot_dir", lambda: tmp_path)
    monkeypatch.setattr("envsnap.alias.get_snapshot_dir", lambda: tmp_path)
    monkeypatch.setattr("envsnap.alias.snapshot_path", lambda name: tmp_path / f"{name}.json")
    return tmp_path


def _make_snapshot(name: str, data: dict | None = None) -> None:
    save_snapshot(name, data or {"KEY": "val"})


def test_set_and_resolve_alias(isolated_snapshot_dir):
    _make_snapshot("prod-2024")
    alias_mod.set_alias("prod", "prod-2024")
    assert alias_mod.resolve_alias("prod") == "prod-2024"


def test_set_alias_missing_snapshot_raises(isolated_snapshot_dir):
    with pytest.raises(FileNotFoundError):
        alias_mod.set_alias("ghost", "nonexistent")


def test_remove_alias(isolated_snapshot_dir):
    _make_snapshot("snap1")
    alias_mod.set_alias("s1", "snap1")
    alias_mod.remove_alias("s1")
    assert alias_mod.resolve_alias("s1") is None


def test_remove_alias_missing_raises(isolated_snapshot_dir):
    with pytest.raises(KeyError):
        alias_mod.remove_alias("nope")


def test_list_aliases(isolated_snapshot_dir):
    _make_snapshot("a")
    _make_snapshot("b")
    alias_mod.set_alias("alpha", "a")
    alias_mod.set_alias("beta", "b")
    result = alias_mod.list_aliases()
    assert result == {"alpha": "a", "beta": "b"}


def test_overwrite_alias(isolated_snapshot_dir):
    _make_snapshot("v1")
    _make_snapshot("v2")
    alias_mod.set_alias("current", "v1")
    alias_mod.set_alias("current", "v2")
    assert alias_mod.resolve_alias("current") == "v2"
