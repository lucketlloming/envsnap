import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envsnap.cli_copy import copy_cmd
from envsnap.copy import SnapshotNotFoundError


@pytest.fixture
def runner():
    return CliRunner()


def test_copy_keys_basic(runner):
    with patch("envsnap.cli_copy.copy_keys") as mock_copy:
        result = runner.invoke(copy_cmd, ["run", "snap_a", "snap_b", "--keys", "FOO", "--keys", "BAR"])
        assert result.exit_code == 0
        mock_copy.assert_called_once_with("snap_a", "snap_b", ["FOO", "BAR"], overwrite=False)
        assert "Copied" in result.output


def test_copy_keys_with_overwrite(runner):
    with patch("envsnap.cli_copy.copy_keys") as mock_copy:
        result = runner.invoke(copy_cmd, ["run", "snap_a", "snap_b", "--keys", "FOO", "--overwrite"])
        assert result.exit_code == 0
        mock_copy.assert_called_once_with("snap_a", "snap_b", ["FOO"], overwrite=True)


def test_copy_missing_source(runner):
    with patch("envsnap.cli_copy.copy_keys", side_effect=SnapshotNotFoundError("snap_a")):
        result = runner.invoke(copy_cmd, ["run", "snap_a", "snap_b", "--keys", "FOO"])
        assert result.exit_code != 0
        assert "snap_a" in result.output


def test_copy_no_keys_shows_error(runner):
    result = runner.invoke(copy_cmd, ["run", "snap_a", "snap_b"])
    assert result.exit_code != 0
