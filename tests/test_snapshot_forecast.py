"""Tests for envsnap.snapshot_forecast."""
from __future__ import annotations

from unittest.mock import patch

import pytest

from envsnap.snapshot_forecast import (
    ForecastResult,
    forecast_all,
    forecast_snapshot,
    format_forecast,
)


def _events(*pairs):
    """Build a minimal event list from (event_name, ...) tuples."""
    return [{"event": p, "snapshot": "s"} for p in pairs]


def _patch(events, snapshots=("s",)):
    return (
        patch("envsnap.snapshot_forecast.get_history", return_value=events),
        patch("envsnap.snapshot_forecast.list_snapshots", return_value=list(snapshots)),
    )


def test_forecast_counts_events():
    events = _events("snap", "snap", "restore", "delete")
    p1, p2 = _patch(events)
    with p1, p2:
        r = forecast_snapshot("s", window_days=30)
    assert r.snap_count == 2
    assert r.restore_count == 1
    assert r.delete_count == 1
    assert r.total_events == 4


def test_forecast_trend_growing():
    events = _events(*(["snap"] * 90))  # 90 events in 30 days -> 3/day
    p1, p2 = _patch(events)
    with p1, p2:
        r = forecast_snapshot("s", window_days=30)
    assert r.trend == "growing"


def test_forecast_trend_declining():
    events = _events("snap")  # 1 event in 30 days -> 0.033/day
    p1, p2 = _patch(events)
    with p1, p2:
        r = forecast_snapshot("s", window_days=30)
    assert r.trend == "declining"


def test_forecast_trend_stable():
    events = _events(*(["snap"] * 20))  # 20 events / 30 days -> 0.67/day
    p1, p2 = _patch(events)
    with p1, p2:
        r = forecast_snapshot("s", window_days=30)
    assert r.trend == "stable"


def test_forecast_note_never_restored():
    events = _events("snap", "snap")
    p1, p2 = _patch(events)
    with p1, p2:
        r = forecast_snapshot("s")
    assert any("Never restored" in n for n in r.notes)


def test_forecast_note_more_deletes_than_snaps():
    events = _events("snap", "delete", "delete", "delete")
    p1, p2 = _patch(events)
    with p1, p2:
        r = forecast_snapshot("s")
    assert any("volatile" in n for n in r.notes)


def test_forecast_projected_30d():
    # 60 events in 30-day window -> avg 2/day -> projected 60
    events = _events(*(["snap"] * 60))
    p1, p2 = _patch(events)
    with p1, p2:
        r = forecast_snapshot("s", window_days=30)
    assert r.projected_30d_events == 60


def test_forecast_all_returns_one_per_snapshot():
    events = _events("snap")
    p1, p2 = _patch(events, snapshots=("a", "b", "c"))
    with p1, p2:
        results = forecast_all()
    assert len(results) == 3


def test_format_forecast_contains_trend():
    r = ForecastResult(
        snapshot_name="demo",
        total_events=5,
        snap_count=3,
        restore_count=1,
        delete_count=1,
        avg_events_per_day=0.167,
        projected_30d_events=5,
        trend="stable",
        notes=["Test note."],
    )
    out = format_forecast(r)
    assert "stable" in out
    assert "demo" in out
    assert "Test note." in out


def test_as_dict_keys():
    r = ForecastResult("x", 0, 0, 0, 0, 0.0, 0, "declining")
    d = r.as_dict()
    assert "snapshot" in d
    assert "trend" in d
    assert "projected_30d_events" in d
