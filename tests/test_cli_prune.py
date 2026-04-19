"""Tests for envsnap.cli_prune."""
import json
from unittest.mock import patch
from click.testing import CliRunner
from envsnap.cli_prune import prune_cmd
from envsnap.prune import PruneError


runner = CliRunner()


def test_prune_age_text_output():
    with patch("envsnap.cli_prune.prune_by_age", return_value=["snap1", "snap2"]) as m:
        result = runner.invoke(prune_cmd, ["age", "7"])
    assert result.exit_code == 0
    assert "Pruned: snap1" in result.output
    assert "Pruned: snap2" in result.output
    m.assert_called_once_with(max_age_days=7.0, dry_run=False)


def test_prune_age_dry_run():
    with patch("envsnap.cli_prune.prune_by_age", return_value=["old"]) as m:
        result = runner.invoke(prune_cmd, ["age", "3", "--dry-run"])
    assert result.exit_code == 0
    assert "Would prune: old" in result.output
    m.assert_called_once_with(max_age_days=3.0, dry_run=True)


def test_prune_age_nothing_to_prune():
    with patch("envsnap.cli_prune.prune_by_age", return_value=[]):
        result = runner.invoke(prune_cmd, ["age", "30"])
    assert result.exit_code == 0
    assert "Nothing to prune" in result.output


def test_prune_age_json_output():
    with patch("envsnap.cli_prune.prune_by_age", return_value=["x"]):
        result = runner.invoke(prune_cmd, ["age", "5", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["pruned"] == ["x"]
    assert data["dry_run"] is False


def test_prune_count_basic():
    with patch("envsnap.cli_prune.prune_by_count", return_value=["old1"]) as m:
        result = runner.invoke(prune_cmd, ["count", "5"])
    assert result.exit_code == 0
    assert "Pruned: old1" in result.output
    m.assert_called_once_with(keep=5, dry_run=False)


def test_prune_count_invalid_keep():
    with patch("envsnap.cli_prune.prune_by_count", side_effect=PruneError("keep must be >= 1")):
        result = runner.invoke(prune_cmd, ["count", "0"])
    assert result.exit_code != 0
    assert "keep must be >= 1" in result.output
