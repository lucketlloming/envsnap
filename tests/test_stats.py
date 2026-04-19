"""Tests for envsnap.stats."""
import pytest
from unittest.mock import patch

from envsnap import stats as stats_mod


SNAPS = {
    "dev": {"HOME": "/home/dev", "PATH": "/usr/bin"},
    "prod": {"HOME": "/home/prod"},
}

HISTORY = {
    "dev": [
        {"event": "snap", "timestamp": "2024-01-01T00:00:00"},
        {"event": "restore", "timestamp": "2024-01-02T00:00:00"},
        {"event": "restore", "timestamp": "2024-01-03T00:00:00"},
    ],
    "prod": [
        {"event": "snap", "timestamp": "2024-02-01T00:00:00"},
    ],
}


def _patch(name):
    return patch(
        f"envsnap.stats.load_snapshot", side_effect=lambda n: SNAPS[n]
    ), patch(
        f"envsnap.stats.list_snapshots", return_value=list(SNAPS)
    ), patch(
        f"envsnap.stats.get_history", side_effect=lambda n: HISTORY.get(n, [])
    ), patch(
        f"envsnap.stats.get_tags", return_value=[]
    ), patch(
        f"envsnap.stats.get_pin", return_value=None
    )


def test_snapshot_stats_key_count():
    patches = _patch("dev")
    with patches[0], patches[1], patches[2], patches[3], patches[4]:
        s = stats_mod.snapshot_stats("dev")
    assert s["key_count"] == 2
    assert s["restore_count"] == 2
    assert s["created_at"] == "2024-01-01T00:00:00"
    assert s["last_restored"] == "2024-01-03T00:00:00"
    assert s["pinned"] is False


def test_snapshot_stats_no_history():
    patches = _patch("prod")
    with patches[0], patches[1], patches[2], patches[3], patches[4]:
        s = stats_mod.snapshot_stats("prod")
    assert s["restore_count"] == 0
    assert s["last_restored"] is None


def test_global_stats_totals():
    patches = _patch(None)
    with patches[0], patches[1], patches[2], patches[3], patches[4]:
        g = stats_mod.global_stats()
    assert g["total_snapshots"] == 2
    assert g["total_keys"] == 3
    assert g["most_restored"] == "dev"
    assert g["pinned_count"] == 0


def test_global_stats_empty():
    with patch("envsnap.stats.list_snapshots", return_value=[]):
        g = stats_mod.global_stats()
    assert g["total_snapshots"] == 0
    assert g["most_restored"] is None


def test_format_stats_returns_string():
    result = stats_mod.format_stats({"total_snapshots": 2, "pinned_count": 1})
    assert "Total snapshots: 2" in result
    assert "Pinned count: 1" in result
