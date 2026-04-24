"""Tests for snapshot lifecycle state management."""
import pytest
from unittest.mock import patch
from click.testing import CliRunner

from envsnap.snapshot_lifecycle import (
    set_state,
    transition,
    get_state,
    list_by_state,
    LifecycleError,
    SnapshotNotFoundError,
)
from envsnap.cli_lifecycle import lifecycle_cmd


@pytest.fixture(autouse=True)
def isolated_snapshot_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("envsnap.snapshot_lifecycle.get_snapshot_dir", lambda: tmp_path)
    monkeypatch.setattr("envsnap.snapshot_lifecycle.list_snapshots", lambda: ["snap1", "snap2"])
    yield tmp_path


def test_get_state_default_is_draft():
    assert get_state("snap1") == "draft"


def test_set_state_changes_state():
    set_state("snap1", "active")
    assert get_state("snap1") == "active"


def test_set_state_invalid_raises():
    with pytest.raises(LifecycleError, match="Invalid state"):
        set_state("snap1", "nonexistent")


def test_set_state_missing_snapshot_raises():
    with pytest.raises(SnapshotNotFoundError):
        set_state("ghost", "active")


def test_transition_valid():
    set_state("snap1", "draft")
    transition("snap1", "active")
    assert get_state("snap1") == "active"


def test_transition_invalid_raises():
    set_state("snap1", "draft")
    with pytest.raises(LifecycleError, match="Cannot transition"):
        transition("snap1", "archived")


def test_transition_from_archived_raises():
    set_state("snap1", "active")
    transition("snap1", "archived")
    with pytest.raises(LifecycleError, match="Cannot transition"):
        transition("snap1", "active")


def test_list_by_state():
    set_state("snap1", "active")
    set_state("snap2", "draft")
    assert list_by_state("active") == ["snap1"]
    assert list_by_state("draft") == ["snap2"]


@pytest.fixture
def runner():
    return CliRunner()


def test_cli_lifecycle_set(runner):
    result = runner.invoke(lifecycle_cmd, ["set", "snap1", "active"])
    assert result.exit_code == 0
    assert "active" in result.output


def test_cli_lifecycle_transition(runner):
    set_state("snap1", "active")
    result = runner.invoke(lifecycle_cmd, ["transition", "snap1", "deprecated"])
    assert result.exit_code == 0
    assert "deprecated" in result.output


def test_cli_lifecycle_show_json(runner):
    set_state("snap1", "active")
    result = runner.invoke(lifecycle_cmd, ["show", "snap1", "--format", "json"])
    import json
    data = json.loads(result.output)
    assert data["state"] == "active"


def test_cli_lifecycle_list(runner):
    set_state("snap1", "active")
    set_state("snap2", "active")
    result = runner.invoke(lifecycle_cmd, ["list", "active"])
    assert "snap1" in result.output
    assert "snap2" in result.output


def test_cli_lifecycle_list_empty(runner):
    result = runner.invoke(lifecycle_cmd, ["list", "archived"])
    assert "No snapshots" in result.output
