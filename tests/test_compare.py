"""Tests for envsnap.compare module."""

import pytest
from unittest.mock import patch
from envsnap.compare import compare_snapshots, format_compare_report


SNAP_A = {"FOO": "1", "BAR": "hello", "COMMON": "same"}
SNAP_B = {"BAR": "world", "COMMON": "same", "NEW": "added"}


def _mock_load(name):
    return SNAP_A if name == "a" else SNAP_B


@patch("envsnap.compare.load_snapshot", side_effect=_mock_load)
def test_compare_only_in_a(mock_load):
    result = compare_snapshots("a", "b")
    assert result["only_in_a"] == {"FOO": "1"}


@patch("envsnap.compare.load_snapshot", side_effect=_mock_load)
def test_compare_only_in_b(mock_load):
    result = compare_snapshots("a", "b")
    assert result["only_in_b"] == {"NEW": "added"}


@patch("envsnap.compare.load_snapshot", side_effect=_mock_load)
def test_compare_changed(mock_load):
    result = compare_snapshots("a", "b")
    assert result["changed"] == {"BAR": {"from": "hello", "to": "world"}}


@patch("envsnap.compare.load_snapshot", side_effect=_mock_load)
def test_compare_common(mock_load):
    result = compare_snapshots("a", "b")
    assert result["common"] == {"COMMON": "same"}


@patch("envsnap.compare.load_snapshot", side_effect=_mock_load)
def test_format_report_contains_sections(mock_load):
    result = compare_snapshots("a", "b")
    report = format_compare_report("a", "b", result)
    assert "Only in 'a'" in report
    assert "Only in 'b'" in report
    assert "Changed" in report
    assert "FOO=1" in report
    assert "NEW=added" in report
    assert "BAR: hello -> world" in report


@patch("envsnap.compare.load_snapshot", return_value={"X": "1"})
def test_format_report_identical(mock_load):
    result = compare_snapshots("a", "b")
    report = format_compare_report("a", "b", result)
    assert "identical" in report
