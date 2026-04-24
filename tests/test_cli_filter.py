"""Tests for envsnap.cli_filter."""
from __future__ import annotations

from unittest.mock import patch

import pytest
from click.testing import CliRunner

from envsnap.cli_filter import filter_cmd


@pytest.fixture()
def runner():
    return CliRunner()


def _patch(results):
    return patch("envsnap.cli_filter.filter_snapshots", return_value=results)


def test_filter_run_text_output(runner):
    with _patch(["snap_a", "snap_b"]):
        result = runner.invoke(filter_cmd, ["run", "--key-prefix", "AWS_"])
    assert result.exit_code == 0
    assert "snap_a" in result.output
    assert "snap_b" in result.output


def test_filter_run_json_output(runner):
    import json

    with _patch(["snap_a"]):
        result = runner.invoke(filter_cmd, ["run", "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data == ["snap_a"]


def test_filter_run_no_results(runner):
    with _patch([]):
        result = runner.invoke(filter_cmd, ["run"])
    assert result.exit_code == 0
    assert "No snapshots matched" in result.output


def test_filter_run_passes_all_options(runner):
    with patch("envsnap.cli_filter.filter_snapshots", return_value=[]) as mock_fn:
        runner.invoke(
            filter_cmd,
            [
                "run",
                "--key-prefix", "DB_",
                "--min-keys", "2",
                "--max-keys", "10",
                "--value-pattern", "prod",
            ],
        )
        mock_fn.assert_called_once_with(
            key_prefix="DB_",
            min_keys=2,
            max_keys=10,
            value_pattern="prod",
        )
