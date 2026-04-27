"""Tests for envsnap.snapshot_freshness."""
from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from envsnap.snapshot_freshness import (
    FreshnessResult,
    _level,
    compute_freshness,
    compute_all_freshness,
    format_freshness,
)
from envsnap.cli_freshness import freshness_cmd


# ---------------------------------------------------------------------------
# unit tests for _level helper
# ---------------------------------------------------------------------------

def test_level_fresh():
    assert _level(0) == "fresh"
    assert _level(7) == "fresh"


def test_level_stale():
    assert _level(8) == "stale"
    assert _level(30) == "stale"


def test_level_aged():
    assert _level(31) == "aged"
    assert _level(365) == "aged"


def test_level_unknown():
    assert _level(None) == "unknown"


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _ts(days_ago: float) -> str:
    dt = datetime.now(timezone.utc) - timedelta(days=days_ago)
    return dt.isoformat()


def _patch(names=None, events_map=None):
    names = names or []
    events_map = events_map or {}
    return [
        patch("envsnap.snapshot_freshness.list_snapshots", return_value=names),
        patch("envsnap.snapshot_freshness.snapshot_path",
              side_effect=lambda n: type("P", (), {"exists": lambda self: True})()),
        patch("envsnap.snapshot_freshness.get_history",
              side_effect=lambda n: events_map.get(n, [])),
    ]


# ---------------------------------------------------------------------------
# compute_freshness
# ---------------------------------------------------------------------------

def test_compute_freshness_fresh():
    events = [{"timestamp": _ts(2)}]
    patches = _patch(["s1"], {"s1": events})
    with patches[0], patches[1], patches[2]:
        r = compute_freshness("s1")
    assert r.level == "fresh"
    assert r.age_days is not None and r.age_days < 3


def test_compute_freshness_aged():
    events = [{"timestamp": _ts(60)}]
    patches = _patch(["s1"], {"s1": events})
    with patches[0], patches[1], patches[2]:
        r = compute_freshness("s1")
    assert r.level == "aged"


def test_compute_freshness_no_history():
    patches = _patch(["s1"], {})
    with patches[0], patches[1], patches[2]:
        r = compute_freshness("s1")
    assert r.level == "unknown"
    assert r.age_days is None


def test_compute_freshness_missing_snapshot():
    with patch("envsnap.snapshot_freshness.snapshot_path",
               side_effect=lambda n: type("P", (), {"exists": lambda self: False})()):
        with pytest.raises(FileNotFoundError):
            compute_freshness("ghost")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

runner = CliRunner()


def test_freshness_show_text():
    events = [{"timestamp": _ts(3)}]
    patches = _patch(["s1"], {"s1": events})
    with patches[0], patches[1], patches[2]:
        result = runner.invoke(freshness_cmd, ["show", "s1"])
    assert result.exit_code == 0
    assert "fresh" in result.output


def test_freshness_show_json():
    events = [{"timestamp": _ts(3)}]
    patches = _patch(["s1"], {"s1": events})
    with patches[0], patches[1], patches[2]:
        result = runner.invoke(freshness_cmd, ["show", "s1", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["name"] == "s1"
    assert "level" in data


def test_freshness_all_with_level_filter():
    events_map = {
        "a": [{"timestamp": _ts(2)}],
        "b": [{"timestamp": _ts(45)}],
    }
    patches = _patch(["a", "b"], events_map)
    with patches[0], patches[1], patches[2]:
        result = runner.invoke(freshness_cmd, ["all", "--level", "fresh"])
    assert result.exit_code == 0
    assert "a" in result.output
    assert "b" not in result.output
