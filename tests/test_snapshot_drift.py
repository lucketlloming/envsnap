"""Tests for envsnap.snapshot_drift."""

import pytest
from unittest.mock import patch

from envsnap.snapshot_drift import detect_drift, format_drift, DriftResult


SNAP_DATA = {"FOO": "bar", "BAZ": "qux", "SHARED": "same"}


def _patch(snap_data):
    return patch("envsnap.snapshot_drift.load_snapshot", return_value=dict(snap_data))


def test_no_drift_when_identical():
    live = {"FOO": "bar", "BAZ": "qux", "SHARED": "same"}
    with _patch(SNAP_DATA):
        result = detect_drift("mysnap", live_env=live)
    assert not result.has_drift
    assert len(result.unchanged) == 3


def test_detects_added_key():
    live = dict(SNAP_DATA)
    live["NEW_KEY"] = "newval"
    with _patch(SNAP_DATA):
        result = detect_drift("mysnap", live_env=live)
    assert "NEW_KEY" in result.added
    assert result.added["NEW_KEY"] == "newval"
    assert result.has_drift


def test_detects_removed_key():
    live = {"FOO": "bar"}  # BAZ and SHARED missing
    with _patch(SNAP_DATA):
        result = detect_drift("mysnap", live_env=live)
    assert "BAZ" in result.removed
    assert "SHARED" in result.removed
    assert result.has_drift


def test_detects_changed_value():
    live = dict(SNAP_DATA)
    live["FOO"] = "changed"
    with _patch(SNAP_DATA):
        result = detect_drift("mysnap", live_env=live)
    assert "FOO" in result.changed
    snap_val, live_val = result.changed["FOO"]
    assert snap_val == "bar"
    assert live_val == "changed"


def test_key_filter_restricts_comparison():
    live = {"FOO": "different", "BAZ": "qux", "SHARED": "same"}
    with _patch(SNAP_DATA):
        result = detect_drift("mysnap", live_env=live, keys=["BAZ", "SHARED"])
    # FOO is excluded
    assert "FOO" not in result.changed
    assert not result.has_drift


def test_as_dict_structure():
    live = dict(SNAP_DATA)
    live["EXTRA"] = "x"
    with _patch(SNAP_DATA):
        result = detect_drift("mysnap", live_env=live)
    d = result.as_dict()
    assert d["snapshot"] == "mysnap"
    assert d["has_drift"] is True
    assert "EXTRA" in d["added"]


def test_format_drift_text_no_drift():
    result = DriftResult(snapshot_name="clean")
    output = format_drift(result, fmt="text")
    assert "No drift" in output
    assert "clean" in output


def test_format_drift_text_with_changes():
    result = DriftResult(
        snapshot_name="mysnap",
        added={"NEW": "1"},
        removed={"OLD": "2"},
        changed={"KEY": ("old", "new")},
    )
    output = format_drift(result, fmt="text")
    assert "+ NEW=1" in output
    assert "- OLD=2" in output
    assert "~ KEY" in output


def test_format_drift_json():
    import json
    result = DriftResult(snapshot_name="mysnap", added={"X": "y"})
    output = format_drift(result, fmt="json")
    data = json.loads(output)
    assert data["snapshot"] == "mysnap"
    assert data["has_drift"] is True
    assert "X" in data["added"]
