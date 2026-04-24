"""Tests for envsnap.snapshot_timeline."""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from envsnap.snapshot_timeline import build_timeline, format_timeline, TimelineEntry
from envsnap.cli_timeline import timeline_cmd


_HISTORY = {
    "alpha": [
        {"event": "snap", "timestamp": "2024-01-01T10:00:00"},
        {"event": "restore", "timestamp": "2024-01-03T08:00:00"},
    ],
    "beta": [
        {"event": "snap", "timestamp": "2024-01-02T09:00:00"},
        {"event": "delete", "timestamp": "2024-01-04T12:00:00"},
    ],
}


def _patch(names=("alpha", "beta")):
    def _list():
        return list(names)

    def _get_history(name):
        return _HISTORY.get(name, [])

    return (
        patch("envsnap.snapshot_timeline.list_snapshots", _list),
        patch("envsnap.snapshot_timeline.get_history", _get_history),
    )


def test_build_timeline_all_entries():
    with _patch()[0], _patch()[1]:
        entries = build_timeline()
    assert len(entries) == 4
    # Must be sorted by timestamp
    timestamps = [e.timestamp for e in entries]
    assert timestamps == sorted(timestamps)


def test_build_timeline_filtered_by_snapshot():
    with _patch()[0], _patch()[1]:
        entries = build_timeline(snapshot="alpha")
    assert all(e.snapshot == "alpha" for e in entries)
    assert len(entries) == 2


def test_build_timeline_filtered_by_event():
    with _patch()[0], _patch()[1]:
        entries = build_timeline(event_filter="snap")
    assert all(e.event == "snap" for e in entries)
    assert len(entries) == 2


def test_build_timeline_limit():
    with _patch()[0], _patch()[1]:
        entries = build_timeline(limit=2)
    assert len(entries) == 2
    # limit returns the *last* N entries (most recent)
    assert entries[-1].timestamp == "2024-01-04T12:00:00"


def test_format_timeline_text():
    entries = [
        TimelineEntry(snapshot="alpha", event="snap", timestamp="2024-01-01T10:00:00")
    ]
    out = format_timeline(entries, fmt="text")
    assert "alpha" in out
    assert "snap" in out
    assert "2024-01-01 10:00:00" in out


def test_format_timeline_empty():
    out = format_timeline([], fmt="text")
    assert "No timeline" in out


def test_format_timeline_json():
    entries = [
        TimelineEntry(snapshot="beta", event="delete", timestamp="2024-01-04T12:00:00")
    ]
    out = format_timeline(entries, fmt="json")
    data = json.loads(out)
    assert data[0]["snapshot"] == "beta"
    assert data[0]["event"] == "delete"


def test_cli_timeline_show_text():
    runner = CliRunner()
    with _patch()[0], _patch()[1]:
        result = runner.invoke(timeline_cmd, ["show"])
    assert result.exit_code == 0
    assert "snap" in result.output


def test_cli_timeline_show_json():
    runner = CliRunner()
    with _patch()[0], _patch()[1]:
        result = runner.invoke(timeline_cmd, ["show", "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert isinstance(data, list)
    assert len(data) == 4


def test_cli_timeline_events():
    runner = CliRunner()
    result = runner.invoke(timeline_cmd, ["events"])
    assert result.exit_code == 0
    assert "snap" in result.output
    assert "restore" in result.output
