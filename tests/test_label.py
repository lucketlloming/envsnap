"""Tests for envsnap.label and envsnap.cli_label."""
from __future__ import annotations

import json
import pytest
from click.testing import CliRunner

from envsnap.cli_label import label_cmd
from envsnap.label import (
    SnapshotNotFoundError,
    add_label,
    clear_labels,
    get_labels,
    remove_label,
    snapshots_with_label,
)
from envsnap.storage import save_snapshot


@pytest.fixture(autouse=True)
def isolated_snapshot_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("envsnap.storage.get_snapshot_dir", lambda: tmp_path)
    monkeypatch.setattr("envsnap.label.get_snapshot_dir", lambda: tmp_path)
    monkeypatch.setattr("envsnap.label.list_snapshots", lambda: ["snap1", "snap2"])
    return tmp_path


@pytest.fixture()
def runner():
    return CliRunner()


def _make_snapshot(name: str, tmp_path) -> None:
    save_snapshot(name, {"KEY": "value"})


# --- unit tests for label.py ---

def test_add_and_get_label(isolated_snapshot_dir):
    add_label("snap1", "production")
    assert "production" in get_labels("snap1")


def test_add_label_deduplicates(isolated_snapshot_dir):
    add_label("snap1", "staging")
    add_label("snap1", "staging")
    assert get_labels("snap1").count("staging") == 1


def test_add_label_missing_snapshot_raises(isolated_snapshot_dir):
    with pytest.raises(SnapshotNotFoundError):
        add_label("nonexistent", "x")


def test_remove_label(isolated_snapshot_dir):
    add_label("snap1", "wip")
    remove_label("snap1", "wip")
    assert "wip" not in get_labels("snap1")


def test_remove_label_cleans_empty_entry(isolated_snapshot_dir):
    add_label("snap1", "solo")
    remove_label("snap1", "solo")
    data = json.loads((isolated_snapshot_dir / "labels.json").read_text())
    assert "snap1" not in data


def test_snapshots_with_label(isolated_snapshot_dir):
    add_label("snap1", "prod")
    add_label("snap2", "prod")
    result = snapshots_with_label("prod")
    assert "snap1" in result and "snap2" in result


def test_clear_labels(isolated_snapshot_dir):
    add_label("snap1", "a")
    add_label("snap1", "b")
    clear_labels("snap1")
    assert get_labels("snap1") == []


# --- CLI tests ---

def test_cli_label_add(runner, isolated_snapshot_dir):
    result = runner.invoke(label_cmd, ["add", "snap1", "production"])
    assert result.exit_code == 0
    assert "added" in result.output


def test_cli_label_add_missing_snapshot(runner, isolated_snapshot_dir):
    result = runner.invoke(label_cmd, ["add", "ghost", "x"])
    assert result.exit_code == 1
    assert "not found" in result.output


def test_cli_label_list_json(runner, isolated_snapshot_dir):
    add_label("snap1", "beta")
    result = runner.invoke(label_cmd, ["list", "snap1", "--format", "json"])
    assert result.exit_code == 0
    assert "beta" in json.loads(result.output)


def test_cli_label_find(runner, isolated_snapshot_dir):
    add_label("snap2", "archive")
    result = runner.invoke(label_cmd, ["find", "archive"])
    assert result.exit_code == 0
    assert "snap2" in result.output


def test_cli_label_clear(runner, isolated_snapshot_dir):
    add_label("snap1", "tmp")
    result = runner.invoke(label_cmd, ["clear", "snap1"])
    assert result.exit_code == 0
    assert get_labels("snap1") == []
