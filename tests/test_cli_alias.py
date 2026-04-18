"""Tests for envsnap.cli_alias."""

import pytest
from click.testing import CliRunner

from envsnap.cli_alias import alias_cmd
from envsnap.storage import save_snapshot


@pytest.fixture(autouse=True)
def isolated_snapshot_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("envsnap.storage.get_snapshot_dir", lambda: tmp_path)
    monkeypatch.setattr("envsnap.alias.get_snapshot_dir", lambda: tmp_path)
    monkeypatch.setattr("envsnap.alias.snapshot_path", lambda name: tmp_path / f"{name}.json")
    return tmp_path


@pytest.fixture()
def runner():
    return CliRunner()


def _snap(name):
    save_snapshot(name, {"X": "1"})


def test_alias_set(runner, isolated_snapshot_dir):
    _snap("prod-snap")
    result = runner.invoke(alias_cmd, ["set", "prod", "prod-snap"])
    assert result.exit_code == 0
    assert "prod" in result.output


def test_alias_set_missing_snapshot(runner, isolated_snapshot_dir):
    result = runner.invoke(alias_cmd, ["set", "ghost", "missing"])
    assert result.exit_code != 0
    assert "does not exist" in result.output


def test_alias_show(runner, isolated_snapshot_dir):
    _snap("s1")
    runner.invoke(alias_cmd, ["set", "myalias", "s1"])
    result = runner.invoke(alias_cmd, ["show", "myalias"])
    assert result.exit_code == 0
    assert "s1" in result.output


def test_alias_show_missing(runner, isolated_snapshot_dir):
    result = runner.invoke(alias_cmd, ["show", "nope"])
    assert result.exit_code != 0


def test_alias_remove(runner, isolated_snapshot_dir):
    _snap("s2")
    runner.invoke(alias_cmd, ["set", "a2", "s2"])
    result = runner.invoke(alias_cmd, ["remove", "a2"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_alias_remove_missing(runner, isolated_snapshot_dir):
    """Removing a non-existent alias should fail with a meaningful message."""
    result = runner.invoke(alias_cmd, ["remove", "nonexistent"])
    assert result.exit_code != 0
    assert "nonexistent" in result.output


def test_alias_list(runner, isolated_snapshot_dir):
    _snap("x")
    _snap("y")
    runner.invoke(alias_cmd, ["set", "ax", "x"])
    runner.invoke(alias_cmd, ["set", "ay", "y"])
    result = runner.invoke(alias_cmd, ["list"])
    assert "ax -> x" in result.output
    assert "ay -> y" in result.output


def test_alias_list_empty(runner, isolated_snapshot_dir):
    """Listing aliases when none are defined should succeed and produce no alias entries."""
    result = runner.invoke(alias_cmd, ["list"])
    assert result.exit_code == 0
    assert "->" not in result.output
