"""Tests for envsnap.workflow and envsnap.cli_workflow."""
from __future__ import annotations

import json
import pytest
from click.testing import CliRunner

from envsnap.cli_workflow import workflow_cmd


@pytest.fixture(autouse=True)
def isolated_snapshot_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("envsnap.workflow.get_snapshot_dir", lambda: tmp_path)
    monkeypatch.setattr("envsnap.workflow.list_snapshots", lambda: ["snap_a", "snap_b", "snap_c"])
    return tmp_path


@pytest.fixture()
def runner():
    return Runner()


class Runner:
    def __init__(self):
        self._r = CliRunner()

    def invoke(self, *args, **kwargs):
        return self._r.invoke(workflow_cmd, *args, **kwargs)


# ── unit tests for the module ─────────────────────────────────────────────────

def test_create_and_get_workflow(isolated_snapshot_dir):
    from envsnap.workflow import create_workflow, get_workflow
    create_workflow("deploy", ["snap_a", "snap_b"], description="deploy flow")
    wf = get_workflow("deploy")
    assert wf["steps"] == ["snap_a", "snap_b"]
    assert wf["description"] == "deploy flow"


def test_create_workflow_missing_snapshot_raises(isolated_snapshot_dir):
    from envsnap.workflow import create_workflow, SnapshotNotFoundError
    with pytest.raises(SnapshotNotFoundError):
        create_workflow("bad", ["snap_a", "nonexistent"])


def test_list_workflows(isolated_snapshot_dir):
    from envsnap.workflow import create_workflow, list_workflows
    create_workflow("w1", ["snap_a"])
    create_workflow("w2", ["snap_b"])
    assert list_workflows() == ["w1", "w2"]


def test_delete_workflow(isolated_snapshot_dir):
    from envsnap.workflow import create_workflow, delete_workflow, list_workflows
    create_workflow("temp", ["snap_a"])
    delete_workflow("temp")
    assert "temp" not in list_workflows()


def test_delete_missing_workflow_raises(isolated_snapshot_dir):
    from envsnap.workflow import delete_workflow, WorkflowNotFoundError
    with pytest.raises(WorkflowNotFoundError):
        delete_workflow("ghost")


def test_append_step(isolated_snapshot_dir):
    from envsnap.workflow import create_workflow, append_step, get_workflow
    create_workflow("pipe", ["snap_a"])
    append_step("pipe", "snap_b")
    assert get_workflow("pipe")["steps"] == ["snap_a", "snap_b"]


# ── CLI tests ─────────────────────────────────────────────────────────────────

def test_workflow_create_text(runner):
    result = runner.invoke(["create", "deploy", "snap_a", "snap_b"])
    assert result.exit_code == 0
    assert "created" in result.output


def test_workflow_create_json(runner):
    result = runner.invoke(["create", "deploy", "snap_a", "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["workflow"] == "deploy"


def test_workflow_show_text(runner):
    runner.invoke(["create", "myflow", "snap_a", "snap_b", "--description", "test"])
    result = runner.invoke(["show", "myflow"])
    assert result.exit_code == 0
    assert "snap_a" in result.output
    assert "test" in result.output


def test_workflow_list_text(runner):
    runner.invoke(["create", "alpha", "snap_a"])
    runner.invoke(["create", "beta", "snap_b"])
    result = runner.invoke(["list"])
    assert "alpha" in result.output
    assert "beta" in result.output


def test_workflow_delete_cmd(runner):
    runner.invoke(["create", "todrop", "snap_a"])
    result = runner.invoke(["delete", "todrop"])
    assert result.exit_code == 0
    assert "deleted" in result.output


def test_workflow_show_missing(runner):
    result = runner.invoke(["show", "nope"])
    assert result.exit_code != 0
    assert "Error" in result.output
