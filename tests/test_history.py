"""Tests for envsnap.history module."""

import pytest
from unittest.mock import patch
from pathlib import Path
import tempfile

from envsnap import history as hist


@pytest.fixture(autouse=True)
def isolated_snapshot_dir(tmp_path):
    with patch("envsnap.history.get_snapshot_dir", return_value=tmp_path):
        yield tmp_path


def test_record_and_get_history():
    hist.record_event("mysnap", "create")
    hist.record_event("mysnap", "restore")
    entries = hist.get_history("mysnap")
    assert len(entries) == 2
    assert entries[0]["action"] == "create"
    assert entries[1]["action"] == "restore"


def test_get_history_all():
    hist.record_event("snap1", "create")
    hist.record_event("snap2", "create")
    entries = hist.get_history()
    assert len(entries) == 2


def test_get_history_filtered():
    hist.record_event("snap1", "create")
    hist.record_event("snap2", "create")
    entries = hist.get_history("snap1")
    assert len(entries) == 1
    assert entries[0]["snapshot"] == "snap1"


def test_clear_history_specific():
    hist.record_event("snap1", "create")
    hist.record_event("snap2", "create")
    removed = hist.clear_history("snap1")
    assert removed == 1
    assert len(hist.get_history()) == 1


def test_clear_history_all():
    hist.record_event("snap1", "create")
    hist.record_event("snap2", "create")
    removed = hist.clear_history()
    assert removed == 2
    assert hist.get_history() == []


def test_format_history_report_empty():
    report = hist.format_history_report([])
    assert report == "No history found."


def test_format_history_report_entries():
    hist.record_event("mysnap", "create")
    entries = hist.get_history()
    report = hist.format_history_report(entries)
    assert "create" in report
    assert "mysnap" in report
