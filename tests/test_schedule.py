"""Tests for envsnap.schedule."""

import pytest
from unittest.mock import patch
from pathlib import Path

from envsnap import schedule as sched


@pytest.fixture(autouse=True)
def isolated_snapshot_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("envsnap.storage.get_snapshot_dir", lambda: tmp_path)
    monkeypatch.setattr("envsnap.schedule._schedule_path", lambda: tmp_path / "schedules.json")
    yield tmp_path


def test_set_and_get_schedule():
    sched.set_schedule("myproject", "daily", keys=["API_KEY"])
    entry = sched.get_schedule("myproject")
    assert entry["interval"] == "daily"
    assert entry["keys"] == ["API_KEY"]
    assert entry["last_run"] is None


def test_set_schedule_invalid_interval():
    with pytest.raises(ValueError, match="interval must be one of"):
        sched.set_schedule("bad", "minutely")


def test_remove_schedule():
    sched.set_schedule("proj", "hourly")
    sched.remove_schedule("proj")
    with pytest.raises(KeyError):
        sched.get_schedule("proj")


def test_remove_missing_schedule_raises():
    with pytest.raises(KeyError):
        sched.remove_schedule("nonexistent")


def test_list_schedules_empty():
    assert sched.list_schedules() == {}


def test_list_schedules_returns_all():
    sched.set_schedule("a", "daily")
    sched.set_schedule("b", "weekly")
    result = sched.list_schedules()
    assert set(result.keys()) == {"a", "b"}


def test_update_last_run():
    sched.set_schedule("proj", "daily")
    sched.update_last_run("proj", "2024-01-01T00:00:00")
    entry = sched.get_schedule("proj")
    assert entry["last_run"] == "2024-01-01T00:00:00"


def test_update_last_run_missing_raises():
    with pytest.raises(KeyError):
        sched.update_last_run("ghost")
