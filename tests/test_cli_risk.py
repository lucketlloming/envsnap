"""Tests for envsnap.cli_risk."""
from __future__ import annotations

import json
from unittest.mock import patch, MagicMock

import pytest
from click.testing import CliRunner

from envsnap.cli_risk import risk_cmd
from envsnap.snapshot_risk import RiskResult


@pytest.fixture()
def runner():
    return CliRunner()


def _fake_result(name="snap", score=0.3, level="medium", factors=None):
    return RiskResult(
        snapshot=name,
        score=score,
        level=level,
        factors=factors or ["some factor"],
    )


def test_risk_show_text(runner):
    result = _fake_result()
    with patch("envsnap.cli_risk.assess_risk", return_value=result):
        out = runner.invoke(risk_cmd, ["show", "snap"])
    assert out.exit_code == 0
    assert "snap" in out.output
    assert "MEDIUM" in out.output


def test_risk_show_json(runner):
    result = _fake_result(score=0.6, level="high")
    with patch("envsnap.cli_risk.assess_risk", return_value=result):
        out = runner.invoke(risk_cmd, ["show", "snap", "--format", "json"])
    assert out.exit_code == 0
    data = json.loads(out.output)
    assert data["level"] == "high"
    assert "score" in data


def test_risk_show_missing_snapshot(runner):
    with patch("envsnap.cli_risk.assess_risk", side_effect=FileNotFoundError("not found")):
        out = runner.invoke(risk_cmd, ["show", "missing"])
    assert out.exit_code != 0
    assert "not found" in out.output


def test_risk_all_text(runner):
    results = [_fake_result("a", 0.8, "critical"), _fake_result("b", 0.1, "low")]
    with patch("envsnap.cli_risk.list_snapshots", return_value=["a", "b"]), \
         patch("envsnap.cli_risk.assess_all_risk", return_value=results):
        out = runner.invoke(risk_cmd, ["all"])
    assert out.exit_code == 0
    assert "a" in out.output


def test_risk_all_json(runner):
    results = [_fake_result("a", 0.8, "critical")]
    with patch("envsnap.cli_risk.list_snapshots", return_value=["a"]), \
         patch("envsnap.cli_risk.assess_all_risk", return_value=results):
        out = runner.invoke(risk_cmd, ["all", "--format", "json"])
    assert out.exit_code == 0
    data = json.loads(out.output)
    assert isinstance(data, list)
    assert data[0]["snapshot"] == "a"


def test_risk_all_no_snapshots(runner):
    with patch("envsnap.cli_risk.list_snapshots", return_value=[]):
        out = runner.invoke(risk_cmd, ["all"])
    assert out.exit_code == 0
    assert "No snapshots" in out.output


def test_risk_all_min_level_filters(runner):
    results = [_fake_result("a", 0.1, "low"), _fake_result("b", 0.6, "high")]
    with patch("envsnap.cli_risk.list_snapshots", return_value=["a", "b"]), \
         patch("envsnap.cli_risk.assess_all_risk", return_value=results):
        out = runner.invoke(risk_cmd, ["all", "--min-level", "high"])
    assert out.exit_code == 0
    assert "b" in out.output
    assert "a" not in out.output
