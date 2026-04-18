"""Tests for cli_history commands."""

import json
import pytest
from unittest.mock import patch
from click.testing import CliRunner

from envsnap.cli_history import history_cmd, clear_history_cmd
from envsnap import history as hist


@pytest.fixture(autouse=True)
def isolated_snapshot_dir(tmp_path):
    with patch("envsnap.history.get_snapshot_dir", return_value=tmp_path):
        yield tmp_path


@pytest.fixture
def runner():
    return CliRunner()


def test_history_cmd_text_empty(runner):
    result = runner.invoke(history_cmd, [])
    assert result.exit_code == 0
    assert "No history found" in result.output


def test_history_cmd_text_with_entries(runner):
    hist.record_event("mysnap", "create")
    result = runner.invoke(history_cmd, ["mysnap"])
    assert result.exit_code == 0
    assert "create" in result.output
    assert "mysnap" in result.output


def test_history_cmd_json_output(runner):
    hist.record_event("mysnap", "restore")
    result = runner.invoke(history_cmd, ["--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert isinstance(data, list)
    assert data[0]["action"] == "restore"


def test_clear_history_cmd_with_yes(runner):
    hist.record_event("snap1", "create")
    result = runner.invoke(clear_history_cmd, ["snap1", "--yes"])
    assert result.exit_code == 0
    assert "1" in result.output
    assert hist.get_history("snap1") == []


def test_clear_history_cmd_all_with_yes(runner):
    hist.record_event("snap1", "create")
    hist.record_event("snap2", "create")
    result = runner.invoke(clear_history_cmd, ["--yes"])
    assert result.exit_code == 0
    assert "2" in result.output
