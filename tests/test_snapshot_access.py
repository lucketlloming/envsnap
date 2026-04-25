"""Tests for envsnap.snapshot_access."""
from __future__ import annotations

import json
import pytest
from pathlib import Path
from unittest.mock import patch

import envsnap.snapshot_access as access_mod


@pytest.fixture()
def isolated_snapshot_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("envsnap.storage.get_snapshot_dir", lambda: tmp_path)
    monkeypatch.setattr(access_mod, "get_snapshot_dir", lambda: tmp_path)
    return tmp_path


def _make_snapshot(tmp_path: Path, name: str) -> None:
    (tmp_path / f"{name}.json").write_text(json.dumps({"KEY": "val"}))


def test_record_and_get_access(isolated_snapshot_dir):
    _make_snapshot(isolated_snapshot_dir, "mysnap")
    access_mod.record_access("mysnap")
    access_mod.record_access("mysnap", action="restore")

    log = access_mod.get_access_log("mysnap")
    assert len(log) == 2
    assert log[0]["action"] == "read"
    assert log[1]["action"] == "restore"
    assert "timestamp" in log[0]


def test_get_access_log_missing_snapshot_returns_empty(isolated_snapshot_dir):
    log = access_mod.get_access_log("nonexistent")
    assert log == []


def test_get_last_accessed_returns_latest(isolated_snapshot_dir):
    _make_snapshot(isolated_snapshot_dir, "snap1")
    access_mod.record_access("snap1")
    access_mod.record_access("snap1")

    log = access_mod.get_access_log("snap1")
    last = access_mod.get_last_accessed("snap1")
    assert last == log[-1]["timestamp"]


def test_get_last_accessed_no_events_returns_none(isolated_snapshot_dir):
    assert access_mod.get_last_accessed("ghost") is None


def test_access_summary_includes_all_snapshots(isolated_snapshot_dir):
    _make_snapshot(isolated_snapshot_dir, "a")
    _make_snapshot(isolated_snapshot_dir, "b")
    access_mod.record_access("a")
    access_mod.record_access("a")

    with patch("envsnap.snapshot_access.list_snapshots", return_value=["a", "b"]):
        summary = access_mod.access_summary()

    names = {row["snapshot"] for row in summary}
    assert names == {"a", "b"}
    a_row = next(r for r in summary if r["snapshot"] == "a")
    b_row = next(r for r in summary if r["snapshot"] == "b")
    assert a_row["access_count"] == 2
    assert b_row["access_count"] == 0
    assert b_row["last_accessed"] is None


def test_clear_access_log(isolated_snapshot_dir):
    _make_snapshot(isolated_snapshot_dir, "snap")
    access_mod.record_access("snap")
    assert len(access_mod.get_access_log("snap")) == 1

    access_mod.clear_access_log("snap")
    assert access_mod.get_access_log("snap") == []


def test_clear_access_log_nonexistent_is_noop(isolated_snapshot_dir):
    access_mod.clear_access_log("does_not_exist")  # should not raise
