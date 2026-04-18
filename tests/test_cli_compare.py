"""Tests for CLI compare command."""

import json
import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envsnap.cli_compare import compare_cmd


SNAP_A = {"FOO": "1", "SHARED": "yes"}
SNAP_B = {"BAR": "2", "SHARED": "yes"}


def _mock_load(name):
    return SNAP_A if name == "snap_a" else SNAP_B


@patch("envsnap.compare.load_snapshot", side_effect=_mock_load)
def test_compare_cmd_text_output(mock_load):
    runner = CliRunner()
    result = runner.invoke(compare_cmd, ["snap_a", "snap_b"])
    assert result.exit_code == 0
    assert "snap_a" in result.output
    assert "snap_b" in result.output
    assert "FOO" in result.output
    assert "BAR" in result.output


@patch("envsnap.compare.load_snapshot", side_effect=_mock_load)
def test_compare_cmd_json_output(mock_load):
    runner = CliRunner()
    result = runner.invoke(compare_cmd, ["snap_a", "snap_b", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "only_in_a" in data
    assert "only_in_b" in data
    assert "changed" in data
    assert "common" in data


@patch("envsnap.compare.load_snapshot", side_effect=FileNotFoundError("snap_x not found"))
def test_compare_cmd_missing_snapshot(mock_load):
    runner = CliRunner()
    result = runner.invoke(compare_cmd, ["snap_x", "snap_y"])
    assert result.exit_code != 0
    assert "snap_x not found" in result.output
