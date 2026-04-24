"""Tests for envsnap.snapshot_trend."""
from __future__ import annotations

from unittest.mock import patch

import pytest
from click.testing import CliRunner

from envsnap.snapshot_trend import (
    TrendPoint,
    TrendResult,
    build_trend,
    build_all_trends,
    format_trend,
)
from envsnap.cli_trend import trend_cmd


_EVENTS = [
    {"action": "snap", "snapshot": "dev", "timestamp": "2024-01-01T10:00:00"},
    {"action": "snap", "snapshot": "dev", "timestamp": "2024-01-01T15:00:00"},
    {"action": "snap", "snapshot": "dev", "timestamp": "2024-01-02T09:00:00"},
    {"action": "restore", "snapshot": "dev", "timestamp": "2024-01-02T11:00:00"},
]


def _patch(events=None, snapshots=None):
    evs = events if events is not None else _EVENTS
    snaps = snapshots if snapshots is not None else ["dev", "prod"]
    return [
        patch("envsnap.snapshot_trend.get_history", return_value=evs),
        patch("envsnap.snapshot_trend.list_snapshots", return_value=snaps),
    ]


def test_build_trend_counts_by_day():
    patches = _patch()
    for p in patches:
        p.start()
    try:
        result = build_trend("dev", event_type="snap")
        assert result.total == 3
        assert len(result.points) == 2
        dates = [p.date for p in result.points]
        assert "2024-01-01" in dates
        assert "2024-01-02" in dates
    finally:
        for p in patches:
            p.stop()


def test_build_trend_peak():
    patches = _patch()
    for p in patches:
        p.start()
    try:
        result = build_trend("dev", event_type="snap")
        assert result.peak_date == "2024-01-01"
        assert result.peak_count == 2
    finally:
        for p in patches:
            p.stop()


def test_build_trend_filters_event_type():
    patches = _patch()
    for p in patches:
        p.start()
    try:
        result = build_trend("dev", event_type="restore")
        assert result.total == 1
        assert result.points[0].date == "2024-01-02"
    finally:
        for p in patches:
            p.stop()


def test_build_trend_empty():
    patches = _patch(events=[])
    for p in patches:
        p.start()
    try:
        result = build_trend("dev")
        assert result.total == 0
        assert result.points == []
        assert result.peak_date is None
    finally:
        for p in patches:
            p.stop()


def test_build_all_trends():
    patches = _patch()
    for p in patches:
        p.start()
    try:
        results = build_all_trends(event_type="snap")
        assert len(results) == 2
    finally:
        for p in patches:
            p.stop()


def test_format_trend_contains_dates():
    result = TrendResult(
        snapshot="dev",
        event_type="snap",
        points=[TrendPoint("2024-01-01", 2), TrendPoint("2024-01-02", 1)],
        peak_date="2024-01-01",
        peak_count=2,
        total=3,
    )
    text = format_trend(result)
    assert "2024-01-01" in text
    assert "Total events" in text
    assert "Peak date" in text


def test_cli_trend_show_text():
    runner = CliRunner()
    patches = _patch()
    for p in patches:
        p.start()
    try:
        result = runner.invoke(trend_cmd, ["show", "dev"])
        assert result.exit_code == 0
        assert "Trend for" in result.output
    finally:
        for p in patches:
            p.stop()


def test_cli_trend_show_json():
    runner = CliRunner()
    patches = _patch()
    for p in patches:
        p.start()
    try:
        result = runner.invoke(trend_cmd, ["show", "dev", "--format", "json"])
        assert result.exit_code == 0
        import json
        data = json.loads(result.output)
        assert "points" in data
        assert data["event_type"] == "snap"
    finally:
        for p in patches:
            p.stop()


def test_cli_trend_all_no_data():
    runner = CliRunner()
    patches = _patch(events=[], snapshots=["dev"])
    for p in patches:
        p.start()
    try:
        result = runner.invoke(trend_cmd, ["all", "--min-total", "1"])
        assert result.exit_code == 0
        assert "No trend data" in result.output
    finally:
        for p in patches:
            p.stop()
