"""Tests for envsnap.snapshot_velocity."""
from __future__ import annotations

import time
from unittest.mock import patch

import pytest

from envsnap.snapshot_velocity import (
    VelocityResult,
    _level,
    compute_all_velocity,
    compute_velocity,
    format_velocity,
)


def _ts(days_ago: float = 0.0) -> float:
    return time.time() - days_ago * 86400


def _patch(events, snapshots=None):
    """Return context managers patching history and storage."""
    from contextlib import ExitStack

    stack = ExitStack()
    stack.enter_context(
        patch("envsnap.snapshot_velocity.get_history", return_value=events)
    )
    stack.enter_context(
        patch(
            "envsnap.snapshot_velocity.list_snapshots",
            return_value=snapshots or ["snap1"],
        )
    )
    return stack


# --- _level ---

def test_level_high():
    assert _level(3.0) == "high"


def test_level_moderate():
    assert _level(1.0) == "moderate"


def test_level_low():
    assert _level(0.1) == "low"


def test_level_idle():
    assert _level(0.0) == "idle"


# --- compute_velocity ---

def test_compute_velocity_no_events():
    with _patch([]):
        r = compute_velocity("snap1")
    assert r.total_events == 0
    assert r.events_last_7d == 0
    assert r.events_last_30d == 0
    assert r.avg_events_per_day == 0.0
    assert r.level == "idle"


def test_compute_velocity_recent_events():
    events = [{"ts": _ts(1)}, {"ts": _ts(3)}, {"ts": _ts(10)}, {"ts": _ts(40)}]
    with _patch(events):
        r = compute_velocity("snap1")
    assert r.total_events == 4
    assert r.events_last_7d == 2
    assert r.events_last_30d == 3
    assert r.avg_events_per_day == pytest.approx(3 / 30, rel=1e-3)


def test_compute_velocity_level_high():
    events = [{"ts": _ts(i)} for i in range(90)]  # 3/day avg
    with _patch(events):
        r = compute_velocity("snap1")
    assert r.level == "high"


# --- compute_all_velocity ---

def test_compute_all_velocity_returns_list():
    with _patch([], snapshots=["a", "b"]):
        results = compute_all_velocity()
    assert len(results) == 2
    assert all(isinstance(r, VelocityResult) for r in results)


# --- format_velocity ---

def test_format_velocity_contains_fields():
    r = VelocityResult(
        snapshot="mysnap",
        total_events=10,
        events_last_7d=2,
        events_last_30d=5,
        avg_events_per_day=0.167,
        level="low",
    )
    text = format_velocity(r)
    assert "mysnap" in text
    assert "low" in text
    assert "10" in text
    assert "0.167" in text
