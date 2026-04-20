"""Tests for envsnap.priority."""
from __future__ import annotations

import json
import pytest
from click.testing import CliRunner
from pathlib import Path
from unittest.mock import patch

from envsnap.priority import (
    DEFAULT_PRIORITY,
    InvalidPriorityError,
    SnapshotNotFoundError,
    get_priority,
    list_by_priority,
    remove_priority,
    set_priority,
)
from envsnap.cli_priority import priority_cmd


@pytest.fixture()
def isolated_snapshot_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("envsnap.priority.get_snapshot_dir", lambda: tmp_path)
    monkeypatch.setattr("envsnap.storage.get_snapshot_dir", lambda: tmp_path)
    return tmp_path


def _make_snapshot(tmp_path: Path, name: str) -> None:
    (tmp_path / f"{name}.json").write_text(json.dumps({"KEY": "val"}))


def test_set_and_get_priority(isolated_snapshot_dir):
    _make_snapshot(isolated_snapshot_dir, "dev")
    set_priority("dev", "high")
    assert get_priority("dev") == "high"


def test_get_priority_default(isolated_snapshot_dir):
    _make_snapshot(isolated_snapshot_dir, "dev")
    assert get_priority("dev") == DEFAULT_PRIORITY


def test_set_priority_invalid_raises(isolated_snapshot_dir):
    _make_snapshot(isolated_snapshot_dir, "dev")
    with pytest.raises(InvalidPriorityError):
        set_priority("dev", "ultra")


def test_set_priority_missing_snapshot_raises(isolated_snapshot_dir):
    with pytest.raises(SnapshotNotFoundError):
        set_priority("ghost", "high")


def test_remove_priority_resets_to_default(isolated_snapshot_dir):
    _make_snapshot(isolated_snapshot_dir, "dev")
    set_priority("dev", "critical")
    remove_priority("dev")
    assert get_priority("dev") == DEFAULT_PRIORITY


def test_list_by_priority_groups_correctly(isolated_snapshot_dir):
    for name in ["a", "b", "c"]:
        _make_snapshot(isolated_snapshot_dir, name)
    set_priority("a", "high")
    set_priority("b", "low")
    grouped = list_by_priority()
    assert "a" in grouped["high"]
    assert "b" in grouped["low"]
    assert "c" in grouped["normal"]


def test_list_by_priority_filtered(isolated_snapshot_dir):
    _make_snapshot(isolated_snapshot_dir, "x")
    set_priority("x", "critical")
    result = list_by_priority("critical")
    assert list(result.keys()) == ["critical"]
    assert "x" in result["critical"]


# CLI tests

@pytest.fixture()
def runner():
    return CliRunner()


def _patch(tmp_path):
    return [
        patch("envsnap.priority.get_snapshot_dir", return_value=tmp_path),
        patch("envsnap.storage.get_snapshot_dir", return_value=tmp_path),
    ]


def test_cli_priority_set(tmp_path, runner):
    _make_snapshot(tmp_path, "prod")
    with patch("envsnap.priority.get_snapshot_dir", return_value=tmp_path), \
         patch("envsnap.priority.list_snapshots", return_value=["prod"]):
        result = runner.invoke(priority_cmd, ["set", "prod", "critical"])
    assert result.exit_code == 0
    assert "critical" in result.output


def test_cli_priority_show_json(tmp_path, runner):
    _make_snapshot(tmp_path, "prod")
    with patch("envsnap.priority.get_snapshot_dir", return_value=tmp_path), \
         patch("envsnap.priority.list_snapshots", return_value=["prod"]):
        set_priority("prod", "high")
        result = runner.invoke(priority_cmd, ["show", "prod", "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["priority"] == "high"


def test_cli_priority_list_text(tmp_path, runner):
    for name in ["a", "b"]:
        _make_snapshot(tmp_path, name)
    with patch("envsnap.priority.get_snapshot_dir", return_value=tmp_path), \
         patch("envsnap.priority.list_snapshots", return_value=["a", "b"]):
        set_priority("a", "high")
        result = runner.invoke(priority_cmd, ["list"])
    assert result.exit_code == 0
    assert "HIGH" in result.output
