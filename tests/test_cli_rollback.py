"""Tests for envsnap.cli_rollback."""
import json
import pytest
from unittest.mock import patch
from click.testing import CliRunner

from envsnap.cli_rollback import rollback_cmd
from envsnap.rollback import RollbackError


@pytest.fixture()
def runner():
    return CliRunner()


_POINTS = [
    {"event": "snap", "timestamp": "2024-01-01T00:00:00", "data": {"X": "1"}},
    {"event": "snap", "timestamp": "2024-01-02T00:00:00", "data": {"X": "2"}},
]


def test_rollback_run_success(runner):
    with patch("envsnap.cli_rollback.rollback_snapshot", return_value={"A": "1", "B": "2"}) as m:
        result = runner.invoke(rollback_cmd, ["run", "mysnap", "--yes"])
    assert result.exit_code == 0
    assert "mysnap" in result.output
    assert "2 key(s)" in result.output
    m.assert_called_once_with("mysnap", steps=1)


def test_rollback_run_with_steps(runner):
    with patch("envsnap.cli_rollback.rollback_snapshot", return_value={"A": "1"}):
        result = runner.invoke(rollback_cmd, ["run", "mysnap", "--steps", "3", "--yes"])
    assert result.exit_code == 0


def test_rollback_run_error(runner):
    with patch("envsnap.cli_rollback.rollback_snapshot", side_effect=RollbackError("no hist")):
        result = runner.invoke(rollback_cmd, ["run", "mysnap", "--yes"])
    assert result.exit_code != 0
    assert "no hist" in result.output


def test_rollback_points_text(runner):
    with patch("envsnap.cli_rollback.get_rollback_points", return_value=_POINTS):
        result = runner.invoke(rollback_cmd, ["points", "mysnap"])
    assert result.exit_code == 0
    assert "snap" in result.output


def test_rollback_points_json(runner):
    with patch("envsnap.cli_rollback.get_rollback_points", return_value=_POINTS):
        result = runner.invoke(rollback_cmd, ["points", "mysnap", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert len(data) == 2


def test_rollback_points_empty(runner):
    with patch("envsnap.cli_rollback.get_rollback_points", return_value=[]):
        result = runner.invoke(rollback_cmd, ["points", "mysnap"])
    assert result.exit_code == 0
    assert "No rollback points" in result.output
