"""Tests for envsnap.snapshot_ownership."""

from __future__ import annotations

import json
import pytest

from envsnap import snapshot_ownership as own
from envsnap.storage import save_snapshot


@pytest.fixture(autouse=True)
def isolated_snapshot_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("envsnap.storage._SNAPSHOT_DIR", tmp_path)
    monkeypatch.setattr("envsnap.snapshot_ownership.get_snapshot_dir", lambda: tmp_path)
    monkeypatch.setattr(
        "envsnap.snapshot_ownership.list_snapshots",
        lambda: [p.stem for p in tmp_path.glob("*.json") if not p.name.startswith("_")],
    )
    return tmp_path


def _make_snapshot(name: str, isolated_snapshot_dir) -> None:
    (isolated_snapshot_dir / f"{name}.json").write_text(json.dumps({"KEY": "val"}))


def test_set_and_get_owner(isolated_snapshot_dir):
    _make_snapshot("prod", isolated_snapshot_dir)
    own.set_owner("prod", "alice")
    assert own.get_owner("prod") == "alice"


def test_get_owner_unset_returns_none(isolated_snapshot_dir):
    _make_snapshot("dev", isolated_snapshot_dir)
    assert own.get_owner("dev") is None


def test_set_owner_missing_snapshot_raises(isolated_snapshot_dir):
    with pytest.raises(own.SnapshotNotFoundError, match="ghost"):
        own.set_owner("ghost", "bob")


def test_remove_owner(isolated_snapshot_dir):
    _make_snapshot("staging", isolated_snapshot_dir)
    own.set_owner("staging", "carol")
    own.remove_owner("staging")
    assert own.get_owner("staging") is None


def test_remove_owner_missing_raises(isolated_snapshot_dir):
    _make_snapshot("staging", isolated_snapshot_dir)
    with pytest.raises(own.OwnershipError, match="No ownership record"):
        own.remove_owner("staging")


def test_list_owned_returns_correct_snapshots(isolated_snapshot_dir):
    for name in ("a", "b", "c"):
        _make_snapshot(name, isolated_snapshot_dir)
    own.set_owner("a", "alice")
    own.set_owner("b", "bob")
    own.set_owner("c", "alice")
    assert sorted(own.list_owned("alice")) == ["a", "c"]
    assert own.list_owned("bob") == ["b"]


def test_list_owned_no_matches_returns_empty(isolated_snapshot_dir):
    assert own.list_owned("nobody") == []


def test_all_ownership_returns_full_map(isolated_snapshot_dir):
    for name in ("x", "y"):
        _make_snapshot(name, isolated_snapshot_dir)
    own.set_owner("x", "alice")
    own.set_owner("y", "bob")
    result = own.all_ownership()
    assert result == {"x": "alice", "y": "bob"}


def test_overwrite_owner(isolated_snapshot_dir):
    _make_snapshot("snap", isolated_snapshot_dir)
    own.set_owner("snap", "alice")
    own.set_owner("snap", "bob")
    assert own.get_owner("snap") == "bob"
