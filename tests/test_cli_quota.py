"""Tests for envsnap.cli_quota."""
from __future__ import annotations

import json

import pytest
from click.testing import CliRunner

from envsnap.cli_quota import quota_cmd
from envsnap.snapshot_quota import set_quota


@pytest.fixture(autouse=True)
def isolated_snapshot_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("envsnap.snapshot_quota.get_snapshot_dir", lambda: tmp_path)
    return tmp_path


@pytest.fixture()
def runner():
    return CliRunner()


def test_quota_set_text(runner):
    result = runner.invoke(quota_cmd, ["set", "myproject", "5"])
    assert result.exit_code == 0
    assert "myproject" in result.output
    assert "5" in result.output


def test_quota_set_json(runner):
    result = runner.invoke(quota_cmd, ["set", "myproject", "5", "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["scope"] == "myproject"
    assert data["max_snapshots"] == 5


def test_quota_set_invalid(runner):
    result = runner.invoke(quota_cmd, ["set", "myproject", "0"])
    assert result.exit_code != 0


def test_quota_show_text(runner):
    set_quota("proj", 8)
    result = runner.invoke(quota_cmd, ["show", "proj"])
    assert result.exit_code == 0
    assert "8" in result.output


def test_quota_show_missing(runner):
    result = runner.invoke(quota_cmd, ["show", "ghost"])
    assert result.exit_code == 0
    assert "No quota" in result.output


def test_quota_remove(runner):
    set_quota("proj", 4)
    result = runner.invoke(quota_cmd, ["remove", "proj"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_quota_remove_missing(runner):
    result = runner.invoke(quota_cmd, ["remove", "ghost"])
    assert result.exit_code != 0


def test_quota_list_empty(runner):
    result = runner.invoke(quota_cmd, ["list"])
    assert result.exit_code == 0
    assert "No quotas" in result.output


def test_quota_list_json(runner):
    set_quota("a", 2)
    set_quota("b", 9)
    result = runner.invoke(quota_cmd, ["list", "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "a" in data
    assert "b" in data
