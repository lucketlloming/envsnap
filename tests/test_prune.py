"""Tests for envsnap.prune."""
import pytest
from pathlib import Path
from unittest.mock import patch
from datetime import datetime, timezone, timedelta

from envsnap.prune import prune_by_age, prune_by_count, PruneError


def _ts(days_ago: float) -> str:
    dt = datetime.now(timezone.utc) - timedelta(days=days_ago)
    return dt.isoformat()


def _patch(names, histories, paths=None):
    """Helper to patch storage and history calls."""
    deleted = []
    fake_paths = {}

    class FakePath:
        def __init__(self, name):
            self.name = name
        def unlink(self, missing_ok=False):
            deleted.append(self.name)

    for n in names:
        fake_paths[n] = FakePath(n)

    p1 = patch("envsnap.prune.list_snapshots", return_value=names)
    p2 = patch("envsnap.prune.get_history", side_effect=lambda n: histories.get(n, []))
    p3 = patch("envsnap.prune.snapshot_path", side_effect=lambda n: fake_paths[n])
    return p1, p2, p3, deleted


def test_prune_by_age_removes_old():
    names = ["old", "new"]
    histories = {
        "old": [{"timestamp": _ts(10)}],
        "new": [{"timestamp": _ts(1)}],
    }
    p1, p2, p3, deleted = _patch(names, histories)
    with p1, p2, p3:
        result = prune_by_age(max_age_days=5)
    assert result == ["old"]
    assert "old" in deleted
    assert "new" not in deleted


def test_prune_by_age_dry_run():
    names = ["old"]
    histories = {"old": [{"timestamp": _ts(20)}]}
    p1, p2, p3, deleted = _patch(names, histories)
    with p1, p2, p3:
        result = prune_by_age(max_age_days=5, dry_run=True)
    assert result == ["old"]
    assert deleted == []


def test_prune_by_age_no_history_skips():
    names = ["nohistory"]
    histories = {}
    p1, p2, p3, deleted = _patch(names, histories)
    with p1, p2, p3:
        result = prune_by_age(max_age_days=1)
    assert result == []


def test_prune_by_count_keeps_most_recent():
    names = ["a", "b", "c"]
    histories = {
        "a": [{"timestamp": _ts(3)}],
        "b": [{"timestamp": _ts(1)}],
        "c": [{"timestamp": _ts(5)}],
    }
    p1, p2, p3, deleted = _patch(names, histories)
    with p1, p2, p3:
        result = prune_by_count(keep=2)
    assert "c" in result
    assert "b" not in result
    assert "a" not in result


def test_prune_by_count_invalid_keep():
    with pytest.raises(PruneError):
        prune_by_count(keep=0)


def test_prune_by_count_dry_run():
    names = ["a", "b", "c"]
    histories = {
        "a": [{"timestamp": _ts(3)}],
        "b": [{"timestamp": _ts(1)}],
        "c": [{"timestamp": _ts(5)}],
    }
    p1, p2, p3, deleted = _patch(names, histories)
    with p1, p2, p3:
        result = prune_by_count(keep=1, dry_run=True)
    assert len(result) == 2
    assert deleted == []
