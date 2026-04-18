"""Tests for envsnap.cli_rename."""
import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envsnap.cli_rename import rename_cmd
from envsnap.rename import SnapshotNotFoundError, SnapshotAlreadyExistsError


@pytest.fixture
def runner():
    return CliRunner()


def test_rename_run_success(runner):
    with patch("envsnap.cli_rename.rename_snapshot") as mock_rename:
        result = runner.invoke(rename_cmd, ["run", "old", "new"])
        assert result.exit_code == 0
        assert "Renamed 'old' -> 'new'" in result.output
        mock_rename.assert_called_once_with("old", "new")


def test_rename_run_missing_snapshot(runner):
    with patch("envsnap.cli_rename.rename_snapshot",
               side_effect=SnapshotNotFoundError("Snapshot 'old' not found.")):
        result = runner.invoke(rename_cmd, ["run", "old", "new"])
        assert result.exit_code != 0
        assert "not found" in result.output


def test_rename_run_destination_exists(runner):
    with patch("envsnap.cli_rename.rename_snapshot",
               side_effect=SnapshotAlreadyExistsError("Snapshot 'new' already exists.")):
        result = runner.invoke(rename_cmd, ["run", "old", "new"])
        assert result.exit_code != 0
        assert "already exists" in result.output
