"""Tests for envsnap.cli_report."""
import json
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from envsnap.cli_report import report_cmd
from envsnap.snapshot_report import SnapshotReport


@pytest.fixture()
def runner():
    return CliRunner()


def _fake_report(name="snap1"):
    return SnapshotReport(
        name=name,
        key_count=3,
        tags=["ci"],
        pinned=True,
        locked=False,
        rating=4,
        note="test note",
        stats={"event_count": 2},
    )


def test_report_show_text(runner, monkeypatch):
    monkeypatch.setattr("envsnap.cli_report.load_snapshot", lambda name: {"A": "1"})
    monkeypatch.setattr("envsnap.cli_report.build_report", lambda name: _fake_report(name))
    result = runner.invoke(report_cmd, ["show", "snap1"])
    assert result.exit_code == 0
    assert "snap1" in result.output
    assert "ci" in result.output
    assert "yes" in result.output  # pinned


def test_report_show_json(runner, monkeypatch):
    monkeypatch.setattr("envsnap.cli_report.load_snapshot", lambda name: {"A": "1"})
    monkeypatch.setattr("envsnap.cli_report.build_report", lambda name: _fake_report(name))
    result = runner.invoke(report_cmd, ["show", "snap1", "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["name"] == "snap1"
    assert data["rating"] == 4


def test_report_show_missing_snapshot(runner, monkeypatch):
    monkeypatch.setattr("envsnap.cli_report.load_snapshot", lambda name: (_ for _ in ()).throw(FileNotFoundError()))
    result = runner.invoke(report_cmd, ["show", "ghost"])
    assert result.exit_code != 0
    assert "not found" in result.output.lower()


def test_report_all_text(runner, monkeypatch):
    monkeypatch.setattr("envsnap.cli_report.build_all_reports", lambda: [_fake_report("a"), _fake_report("b")])
    result = runner.invoke(report_cmd, ["all"])
    assert result.exit_code == 0
    assert "snap" in result.output  # both entries contain 'snap' prefix in name


def test_report_all_json(runner, monkeypatch):
    monkeypatch.setattr("envsnap.cli_report.build_all_reports", lambda: [_fake_report("x")])
    result = runner.invoke(report_cmd, ["all", "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert isinstance(data, list)
    assert data[0]["name"] == "x"


def test_report_all_empty(runner, monkeypatch):
    monkeypatch.setattr("envsnap.cli_report.build_all_reports", lambda: [])
    result = runner.invoke(report_cmd, ["all"])
    assert result.exit_code == 0
    assert "No snapshots" in result.output
