"""Tests for envsnap.snapshot_coverage."""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from envsnap.snapshot_coverage import (
    CoverageResult,
    compute_coverage,
    coverage_all,
    format_coverage,
)


def _patch(snap_data: dict, all_names=None):
    """Return a context manager that mocks load_snapshot and list_snapshots."""
    import contextlib

    @contextlib.contextmanager
    def _ctx():
        with patch("envsnap.snapshot_coverage.load_snapshot", return_value=snap_data), \
             patch("envsnap.snapshot_coverage.list_snapshots", return_value=all_names or []):
            yield

    return _ctx()


def test_compute_coverage_full():
    data = {"A": "1", "B": "2", "C": "3"}
    with _patch(data):
        result = compute_coverage("mysnap", ["A", "B", "C"])
    assert result.coverage_pct == 100.0
    assert result.missing == []
    assert sorted(result.present) == ["A", "B", "C"]


def test_compute_coverage_partial():
    data = {"A": "1", "C": "3"}
    with _patch(data):
        result = compute_coverage("mysnap", ["A", "B", "C"])
    assert result.coverage_pct == pytest.approx(66.67, abs=0.1)
    assert result.missing == ["B"]
    assert result.present == ["A", "C"]


def test_compute_coverage_none_present():
    data = {"X": "1"}
    with _patch(data):
        result = compute_coverage("mysnap", ["A", "B"])
    assert result.coverage_pct == 0.0
    assert sorted(result.missing) == ["A", "B"]
    assert result.present == []


def test_compute_coverage_empty_expected():
    data = {"A": "1"}
    with _patch(data):
        result = compute_coverage("mysnap", [])
    assert result.coverage_pct == 100.0
    assert result.missing == []


def test_coverage_all_returns_one_per_snapshot():
    data = {"A": "1"}
    with _patch(data, all_names=["snap1", "snap2"]):
        results = coverage_all(["A", "B"])
    assert len(results) == 2
    assert {r.snapshot for r in results} == {"snap1", "snap2"}


def test_format_coverage_text():
    result = CoverageResult(
        snapshot="dev",
        expected=["A", "B"],
        present=["A"],
        missing=["B"],
        coverage_pct=50.0,
    )
    text = format_coverage(result, fmt="text")
    assert "50.0%" in text
    assert "B" in text
    assert "dev" in text


def test_format_coverage_json():
    result = CoverageResult(
        snapshot="dev",
        expected=["A", "B"],
        present=["A", "B"],
        missing=[],
        coverage_pct=100.0,
    )
    output = format_coverage(result, fmt="json")
    parsed = json.loads(output)
    assert parsed["coverage_pct"] == 100.0
    assert parsed["snapshot"] == "dev"
    assert parsed["missing"] == []
