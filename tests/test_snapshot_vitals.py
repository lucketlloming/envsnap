"""Tests for envsnap.snapshot_vitals."""
from __future__ import annotations

from unittest.mock import patch

import pytest

from envsnap.snapshot_vitals import compute_vitals, compute_all_vitals, format_vitals


def _patch(snap_data=None, history=None, pin=None, locked=False, expiry=None, snapshots=None):
    snap_data = snap_data or {"KEY": "val"}
    history = history or []
    snapshots = snapshots or ["snap1"]
    return [
        patch("envsnap.snapshot_vitals.load_snapshot", return_value=snap_data),
        patch("envsnap.snapshot_vitals.list_snapshots", return_value=snapshots),
        patch("envsnap.snapshot_vitals.get_history", return_value=history),
        patch("envsnap.snapshot_vitals.get_pin", return_value=pin),
        patch("envsnap.snapshot_vitals.is_locked", return_value=locked),
        patch("envsnap.snapshot_vitals.get_expiry", return_value=expiry),
    ]


def test_compute_vitals_basic_fields():
    data = {"A": "1", "B": "2", "C": ""}
    with _patch(snap_data=data, history=[{}, {}])[0], \
         _patch(snap_data=data, history=[{}, {}])[2] as mh, \
         _patch(snap_data=data)[0] as ml, \
         patch("envsnap.snapshot_vitals.get_history", return_value=[{}, {}]), \
         patch("envsnap.snapshot_vitals.get_pin", return_value=None), \
         patch("envsnap.snapshot_vitals.is_locked", return_value=False), \
         patch("envsnap.snapshot_vitals.get_expiry", return_value=None), \
         patch("envsnap.snapshot_vitals.load_snapshot", return_value=data):
        result = compute_vitals("snap1")

    assert result.name == "snap1"
    assert result.key_count == 3
    assert result.empty_count == 1
    assert result.event_count == 2
    assert not result.is_pinned
    assert not result.is_locked
    assert result.expiry is None
    assert abs(result.fill_rate - 66.67) < 0.1


def test_compute_vitals_pinned_and_locked():
    data = {"X": "y"}
    with patch("envsnap.snapshot_vitals.load_snapshot", return_value=data), \
         patch("envsnap.snapshot_vitals.get_history", return_value=[]), \
         patch("envsnap.snapshot_vitals.get_pin", return_value="v1"), \
         patch("envsnap.snapshot_vitals.is_locked", return_value=True), \
         patch("envsnap.snapshot_vitals.get_expiry", return_value={"expires_at": "2099-01-01"}):
        result = compute_vitals("snap1")

    assert result.is_pinned
    assert result.is_locked
    assert result.expiry == "2099-01-01"


def test_compute_vitals_empty_snapshot():
    with patch("envsnap.snapshot_vitals.load_snapshot", return_value={}), \
         patch("envsnap.snapshot_vitals.get_history", return_value=[]), \
         patch("envsnap.snapshot_vitals.get_pin", return_value=None), \
         patch("envsnap.snapshot_vitals.is_locked", return_value=False), \
         patch("envsnap.snapshot_vitals.get_expiry", return_value=None):
        result = compute_vitals("empty")

    assert result.key_count == 0
    assert result.fill_rate == 0.0


def test_compute_all_vitals_returns_list():
    data = {"K": "v"}
    with patch("envsnap.snapshot_vitals.list_snapshots", return_value=["a", "b"]), \
         patch("envsnap.snapshot_vitals.load_snapshot", return_value=data), \
         patch("envsnap.snapshot_vitals.get_history", return_value=[]), \
         patch("envsnap.snapshot_vitals.get_pin", return_value=None), \
         patch("envsnap.snapshot_vitals.is_locked", return_value=False), \
         patch("envsnap.snapshot_vitals.get_expiry", return_value=None):
        results = compute_all_vitals()

    assert len(results) == 2
    assert {r.name for r in results} == {"a", "b"}


def test_format_vitals_contains_name():
    data = {"A": "1"}
    with patch("envsnap.snapshot_vitals.load_snapshot", return_value=data), \
         patch("envsnap.snapshot_vitals.get_history", return_value=[]), \
         patch("envsnap.snapshot_vitals.get_pin", return_value=None), \
         patch("envsnap.snapshot_vitals.is_locked", return_value=False), \
         patch("envsnap.snapshot_vitals.get_expiry", return_value=None):
        result = compute_vitals("mysnap")

    text = format_vitals(result)
    assert "mysnap" in text
    assert "Fill rate" in text
    assert "Keys" in text


def test_as_dict_keys():
    data = {"A": "1"}
    with patch("envsnap.snapshot_vitals.load_snapshot", return_value=data), \
         patch("envsnap.snapshot_vitals.get_history", return_value=[]), \
         patch("envsnap.snapshot_vitals.get_pin", return_value=None), \
         patch("envsnap.snapshot_vitals.is_locked", return_value=False), \
         patch("envsnap.snapshot_vitals.get_expiry", return_value=None):
        result = compute_vitals("s")

    d = result.as_dict()
    for key in ("name", "key_count", "empty_count", "event_count",
                "is_pinned", "is_locked", "expiry", "fill_rate"):
        assert key in d
