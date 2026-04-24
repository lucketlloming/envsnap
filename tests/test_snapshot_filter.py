"""Tests for envsnap.snapshot_filter."""
from __future__ import annotations

import pytest

from envsnap import storage
from envsnap.snapshot_filter import (
    filter_by_key_count,
    filter_by_key_prefix,
    filter_by_value_pattern,
    filter_snapshots,
)


@pytest.fixture(autouse=True)
def isolated_snapshot_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "get_snapshot_dir", lambda: tmp_path)
    return tmp_path


def _save(name: str, data: dict) -> None:
    storage.save_snapshot(name, data)


def test_filter_by_key_prefix_matches():
    _save("snap_a", {"AWS_KEY": "abc", "AWS_SECRET": "xyz"})
    _save("snap_b", {"DB_HOST": "localhost"})
    result = filter_by_key_prefix("AWS_")
    assert "snap_a" in result
    assert "snap_b" not in result


def test_filter_by_key_prefix_no_match():
    _save("snap_a", {"DB_HOST": "localhost"})
    result = filter_by_key_prefix("NONEXISTENT_")
    assert result == []


def test_filter_by_key_count_min():
    _save("small", {"A": "1"})
    _save("large", {"A": "1", "B": "2", "C": "3"})
    result = filter_by_key_count(min_keys=2)
    assert "large" in result
    assert "small" not in result


def test_filter_by_key_count_max():
    _save("small", {"A": "1"})
    _save("large", {"A": "1", "B": "2", "C": "3"})
    result = filter_by_key_count(max_keys=2)
    assert "small" in result
    assert "large" not in result


def test_filter_by_value_pattern_matches():
    _save("snap_a", {"URL": "https://example.com"})
    _save("snap_b", {"URL": "http://internal"})
    result = filter_by_value_pattern("example")
    assert "snap_a" in result
    assert "snap_b" not in result


def test_filter_snapshots_combined():
    _save("match", {"AWS_KEY": "abc", "AWS_SECRET": "xyz"})
    _save("no_prefix", {"DB_HOST": "localhost"})
    _save("too_small", {"AWS_KEY": "abc"})
    result = filter_snapshots(key_prefix="AWS_", min_keys=2)
    assert result == ["match"]


def test_filter_snapshots_empty_store():
    result = filter_snapshots()
    assert result == []
