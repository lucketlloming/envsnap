"""Tests for envsnap.cli_score."""
from __future__ import annotations

import json
from unittest.mock import patch, MagicMock

import pytest
from click.testing import CliRunner

from envsnap.cli_score import score_cmd
from envsnap.snapshot_score import ScoreResult


@pytest.fixture()
def runner():
    return CliRunner()


def _fake_result(name="snap1", score=85):
    return ScoreResult(
        snapshot=name,
        score=score,
        breakdown={"lint_penalty": 5, "validate_penalty": 0, "empty_penalty": 10},
        penalties=["lint:KEY:suspicious"],
    )


def test_score_show_text(runner):
    with patch("envsnap.cli_score.score_snapshot", return_value=_fake_result()) as m:
        result = runner.invoke(score_cmd, ["show", "snap1"])
    assert result.exit_code == 0
    assert "snap1" in result.output
    assert "85/100" in result.output


def test_score_show_json(runner):
    with patch("envsnap.cli_score.score_snapshot", return_value=_fake_result()):
        result = runner.invoke(score_cmd, ["show", "snap1", "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["score"] == 85
    assert data["snapshot"] == "snap1"
    assert "breakdown" in data


def test_score_show_missing_snapshot(runner):
    with patch("envsnap.cli_score.score_snapshot", side_effect=FileNotFoundError):
        result = runner.invoke(score_cmd, ["show", "ghost"])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_score_all_text(runner):
    with patch("envsnap.cli_score.list_snapshots", return_value=["a", "b"]), \
         patch("envsnap.cli_score.score_snapshot", side_effect=[
             _fake_result("a", 90), _fake_result("b", 60)]):
        result = runner.invoke(score_cmd, ["all"])
    assert result.exit_code == 0
    assert "a" in result.output
    assert "b" in result.output
    assert "90" in result.output


def test_score_all_json(runner):
    with patch("envsnap.cli_score.list_snapshots", return_value=["x"]), \
         patch("envsnap.cli_score.score_snapshot", return_value=_fake_result("x", 77)):
        result = runner.invoke(score_cmd, ["all", "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data[0]["snapshot"] == "x"
    assert data[0]["score"] == 77


def test_score_all_no_snapshots(runner):
    with patch("envsnap.cli_score.list_snapshots", return_value=[]):
        result = runner.invoke(score_cmd, ["all"])
    assert result.exit_code == 0
    assert "No snapshots" in result.output


def test_score_all_min_score_filter(runner):
    with patch("envsnap.cli_score.list_snapshots", return_value=["a", "b"]), \
         patch("envsnap.cli_score.score_snapshot", side_effect=[
             _fake_result("a", 40), _fake_result("b", 90)]):
        result = runner.invoke(score_cmd, ["all", "--min-score", "70"])
    assert result.exit_code == 0
    assert "b" in result.output
    assert "a" not in result.output
