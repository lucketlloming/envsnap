"""Tests for envsnap.cli_profiles."""

import pytest
from click.testing import CliRunner

from envsnap.cli_profiles import profile_cmd
from envsnap import profiles
from envsnap import storage


@pytest.fixture(autouse=True)
def isolated_snapshot_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("envsnap.storage._SNAPSHOT_DIR", tmp_path)
    monkeypatch.setattr("envsnap.profiles.get_snapshot_dir", lambda: tmp_path)
    monkeypatch.setattr("envsnap.cli_profiles.list_snapshots", lambda: ["snap1", "snap2"])
    yield tmp_path


@pytest.fixture
def runner():
    return CliRunner()


def test_profile_add(runner):
    result = runner.invoke(profile_cmd, ["add", "work", "snap1"])
    assert result.exit_code == 0
    assert "Added 'snap1' to profile 'work'" in result.output
    assert "snap1" in profiles.get_profile("work")


def test_profile_add_missing_snapshot(runner):
    result = runner.invoke(profile_cmd, ["add", "work", "missing"])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_profile_remove(runner):
    profiles.add_to_profile("work", "snap1")
    result = runner.invoke(profile_cmd, ["remove", "work", "snap1"])
    assert result.exit_code == 0
    assert "snap1" not in profiles.get_profile("work")


def test_profile_list_all(runner):
    profiles.add_to_profile("a", "snap1")
    profiles.add_to_profile("b", "snap2")
    result = runner.invoke(profile_cmd, ["list"])
    assert "a" in result.output
    assert "b" in result.output


def test_profile_list_specific(runner):
    profiles.add_to_profile("dev", "snap1")
    profiles.add_to_profile("dev", "snap2")
    result = runner.invoke(profile_cmd, ["list", "dev"])
    assert "snap1" in result.output
    assert "snap2" in result.output


def test_profile_delete(runner):
    profiles.add_to_profile("old", "snap1")
    result = runner.invoke(profile_cmd, ["delete", "old"])
    assert result.exit_code == 0
    assert "old" not in profiles.list_profiles()
