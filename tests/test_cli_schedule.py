"""Tests for CLI schedule commands."""

import json
import pytest
from click.testing import CliRunner
from envsnap.cli_schedule import schedule_cmd
from envsnap import schedule as sched


@pytest.fixture(autouse=True)
def isolated_snapshot_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("envsnap.schedule._schedule_path", lambda: tmp_path / "schedules.json")
    yield tmp_path


@pytest.fixture
def runner():
    return CliRunner()


def test_schedule_set(runner):
    result = runner.invoke(schedule_cmd, ["set", "proj", "--interval", "daily"])
    assert result.exit_code == 0
    assert "proj" in result.output
    assert "daily" in result.output


def test_schedule_set_with_keys(runner):
    result = runner.invoke(schedule_cmd, ["set", "proj", "--interval", "hourly", "--keys", "API_KEY,DB_URL"])
    assert result.exit_code == 0
    entry = sched.get_schedule("proj")
    assert entry["keys"] == ["API_KEY", "DB_URL"]


def test_schedule_remove(runner):
    sched.set_schedule("proj", "weekly")
    result = runner.invoke(schedule_cmd, ["remove", "proj"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_schedule_remove_missing(runner):
    result = runner.invoke(schedule_cmd, ["remove", "ghost"])
    assert result.exit_code == 1


def test_schedule_list_empty(runner):
    result = runner.invoke(schedule_cmd, ["list"])
    assert result.exit_code == 0
    assert "No schedules" in result.output


def test_schedule_list_text(runner):
    sched.set_schedule("a", "daily", keys=["X"])
    result = runner.invoke(schedule_cmd, ["list"])
    assert "a" in result.output
    assert "daily" in result.output


def test_schedule_list_json(runner):
    sched.set_schedule("b", "weekly")
    result = runner.invoke(schedule_cmd, ["list", "--json"])
    data = json.loads(result.output)
    assert "b" in data


def test_schedule_show(runner):
    sched.set_schedule("proj", "hourly")
    result = runner.invoke(schedule_cmd, ["show", "proj"])
    data = json.loads(result.output)
    assert data["interval"] == "hourly"


def test_schedule_show_missing(runner):
    result = runner.invoke(schedule_cmd, ["show", "nope"])
    assert result.exit_code == 1
