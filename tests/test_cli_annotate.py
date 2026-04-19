"""Tests for envsnap.cli_annotate."""
import json
import pytest
from click.testing import CliRunner

from envsnap.cli_annotate import annotate_cmd
from envsnap import annotate


@pytest.fixture(autouse=True)
def isolated_snapshot_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("envsnap.annotate.get_snapshot_dir", lambda: tmp_path)
    monkeypatch.setattr("envsnap.annotate.list_snapshots", lambda: ["snap1", "snap2"])
    return tmp_path


@pytest.fixture
def runner():
    return CliRunner()


def test_annotate_set(runner):
    result = runner.invoke(annotate_cmd, ["set", "snap1", "author", "alice"])
    assert result.exit_code == 0
    assert "set on 'snap1'" in result.output
    assert annotate.get_annotations("snap1")["author"] == "alice"


def test_annotate_set_missing_snapshot(runner):
    result = runner.invoke(annotate_cmd, ["set", "ghost", "k", "v"])
    assert result.exit_code == 1
    assert "ghost" in result.output


def test_annotate_get_text(runner):
    annotate.set_annotation("snap1", "env", "prod")
    result = runner.invoke(annotate_cmd, ["get", "snap1"])
    assert "env: prod" in result.output


def test_annotate_get_json(runner):
    annotate.set_annotation("snap1", "env", "prod")
    result = runner.invoke(annotate_cmd, ["get", "--format", "json", "snap1"])
    data = json.loads(result.output)
    assert data["env"] == "prod"


def test_annotate_get_empty(runner):
    result = runner.invoke(annotate_cmd, ["get", "snap1"])
    assert "No annotations" in result.output


def test_annotate_remove(runner):
    annotate.set_annotation("snap1", "x", "1")
    result = runner.invoke(annotate_cmd, ["remove", "snap1", "x"])
    assert result.exit_code == 0
    assert annotate.get_annotations("snap1") == {}


def test_annotate_remove_missing_key(runner):
    """Removing a key that does not exist should exit with an error."""
    result = runner.invoke(annotate_cmd, ["remove", "snap1", "nonexistent"])
    assert result.exit_code == 1
    assert "nonexistent" in result.output


def test_annotate_clear(runner):
    annotate.set_annotation("snap1", "a", "1")
    annotate.set_annotation("snap1", "b", "2")
    result = runner.invoke(annotate_cmd, ["clear", "snap1"])
    assert result.exit_code == 0
    assert annotate.get_annotations("snap1") == {}


def test_annotate_list_json(runner):
    annotate.set_annotation("snap1", "k", "v")
    result = runner.invoke(annotate_cmd, ["list", "--format", "json"])
    data = json.loads(result.output)
    assert data["snap1"]["k"] == "v"
