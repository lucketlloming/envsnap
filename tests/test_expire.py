"""Tests for envsnap.expire."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from envsnap import expire as exp


@pytest.fixture
def isolated_snapshot_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("envsnap.expire.get_snapshot_dir", lambda: tmp_path)
    monkeypatch.setattr("envsnap.expire.snapshot_path", lambda name, d=None: (d or tmp_path) / f"{name}.json")
    return tmp_path


def _make_snapshot(d: Path, name: str):
    (d / f"{name}.json").write_text(json.dumps({"A": "1"}))


def test_set_and_get_expiry(isolated_snapshot_dir):
    _make_snapshot(isolated_snapshot_dir, "snap1")
    exp.set_expiry("snap1", "2099-01-01", isolated_snapshot_dir)
    assert exp.get_expiry("snap1", isolated_snapshot_dir) == "2099-01-01"


def test_set_expiry_missing_snapshot_raises(isolated_snapshot_dir):
    with pytest.raises(exp.SnapshotNotFoundError):
        exp.set_expiry("ghost", "2099-01-01", isolated_snapshot_dir)


def test_set_expiry_invalid_date_raises(isolated_snapshot_dir):
    _make_snapshot(isolated_snapshot_dir, "snap1")
    with pytest.raises(ValueError, match="Invalid date format"):
        exp.set_expiry("snap1", "01-01-2099", isolated_snapshot_dir)


def test_remove_expiry(isolated_snapshot_dir):
    _make_snapshot(isolated_snapshot_dir, "snap1")
    exp.set_expiry("snap1", "2099-01-01", isolated_snapshot_dir)
    exp.remove_expiry("snap1", isolated_snapshot_dir)
    assert exp.get_expiry("snap1", isolated_snapshot_dir) is None


def test_remove_missing_expiry_raises(isolated_snapshot_dir):
    with pytest.raises(exp.ExpiryNotFoundError):
        exp.remove_expiry("ghost", isolated_snapshot_dir)


def test_list_expiry(isolated_snapshot_dir):
    _make_snapshot(isolated_snapshot_dir, "a")
    _make_snapshot(isolated_snapshot_dir, "b")
    exp.set_expiry("a", "2099-06-01", isolated_snapshot_dir)
    exp.set_expiry("b", "2099-12-31", isolated_snapshot_dir)
    result = exp.list_expiry(isolated_snapshot_dir)
    assert result == {"a": "2099-06-01", "b": "2099-12-31"}


def test_get_expired_returns_past_dates(isolated_snapshot_dir):
    _make_snapshot(isolated_snapshot_dir, "old")
    _make_snapshot(isolated_snapshot_dir, "future")
    exp.set_expiry("old", "2000-01-01", isolated_snapshot_dir)
    exp.set_expiry("future", "2099-01-01", isolated_snapshot_dir)
    expired = exp.get_expired(isolated_snapshot_dir)
    assert "old" in expired
    assert "future" not in expired


def test_get_expired_empty(isolated_snapshot_dir):
    assert exp.get_expired(isolated_snapshot_dir) == []
