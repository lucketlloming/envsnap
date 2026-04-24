"""Tests for envsnap.cli_forecast."""
from __future__ import annotations

from unittest.mock import patch

import pytest
from click.testing import CliRunner

from envsnap.cli_forecast import forecast_cmd
from envsnap.snapshot_forecast import ForecastResult


@pytest.fixture()
def runner():
    return CliRunner()


def _fake_result(name="mysnap"):
    return ForecastResult(
        snapshot_name=name,
        total_events=10,
        snap_count=7,
        restore_count=2,
        delete_count=1,
        avg_events_per_day=0.333,
        projected_30d_events=10,
        trend="stable",
        notes=[],
    )


def test_forecast_show_text(runner):
    with (
        patch("envsnap.cli_forecast.list_snapshots", return_value=["mysnap"]),
        patch("envsnap.cli_forecast.forecast_snapshot", return_value=_fake_result()),
    ):
        result = runner.invoke(forecast_cmd, ["show", "mysnap"])
    assert result.exit_code == 0
    assert "stable" in result.output
    assert "mysnap" in result.output


def test_forecast_show_json(runner):
    import json

    with (
        patch("envsnap.cli_forecast.list_snapshots", return_value=["mysnap"]),
        patch("envsnap.cli_forecast.forecast_snapshot", return_value=_fake_result()),
    ):
        result = runner.invoke(forecast_cmd, ["show", "mysnap", "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["snapshot"] == "mysnap"
    assert data["trend"] == "stable"


def test_forecast_show_missing_snapshot(runner):
    with patch("envsnap.cli_forecast.list_snapshots", return_value=[]):
        result = runner.invoke(forecast_cmd, ["show", "ghost"])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_forecast_all_text(runner):
    results = [_fake_result("a"), _fake_result("b")]
    with (
        patch("envsnap.cli_forecast.list_snapshots", return_value=["a", "b"]),
        patch("envsnap.cli_forecast.forecast_all", return_value=results),
    ):
        result = runner.invoke(forecast_cmd, ["all"])
    assert result.exit_code == 0
    assert "a" in result.output
    assert "b" in result.output


def test_forecast_all_empty(runner):
    with patch("envsnap.cli_forecast.list_snapshots", return_value=[]):
        result = runner.invoke(forecast_cmd, ["all"])
    assert result.exit_code == 0
    assert "No snapshots" in result.output
