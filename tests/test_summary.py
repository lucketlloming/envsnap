"""Tests for envsnap.summary and envsnap.cli_summary."""
import pytest
import json
from unittest.mock import patch
from click.testing import CliRunner
from envsnap.cli_summary import summary_cmd

SNAP_DATA = {"HOME": "/home/user", "PATH": "/usr/bin"}


def _patch(name="mysnap", data=SNAP_DATA, tags=None, note="hello", pinned=False):
    tags = tags or ["prod"]
    return (
        patch("envsnap.summary.load_snapshot", return_value=data),
        patch("envsnap.summary.get_tags", return_value=tags),
        patch("envsnap.summary.get_note", return_value=note),
        patch("envsnap.summary.get_pin", return_value=name if pinned else None),
    )


@pytest.fixture
def runner():
    return CliRunner()


def test_summarize_snapshot_fields():
    from envsnap.summary import summarize_snapshot
    patches = _patch()
    with patches[0], patches[1], patches[2], patches[3]:
        s = summarize_snapshot("mysnap")
    assert s["name"] == "mysnap"
    assert s["key_count"] == 2
    assert set(s["keys"]) == {"HOME", "PATH"}
    assert s["tags"] == ["prod"]
    assert s["note"] == "hello"
    assert s["pinned"] is False


def test_summarize_snapshot_pinned():
    from envsnap.summary import summarize_snapshot
    patches = _patch(pinned=True)
    with patches[0], patches[1], patches[2], patches[3]:
        s = summarize_snapshot("mysnap")
    assert s["pinned"] is True


def test_summary_show_text(runner):
    patches = _patch()
    with patches[0], patches[1], patches[2], patches[3]:
        result = runner.invoke(summary_cmd, ["show", "mysnap"])
    assert result.exit_code == 0
    assert "mysnap" in result.output
    assert "prod" in result.output
    assert "hello" in result.output


def test_summary_show_json(runner):
    patches = _patch()
    with patches[0], patches[1], patches[2], patches[3]:
        result = runner.invoke(summary_cmd, ["show", "mysnap", "--format", "json"])
    assert result.exit_code == 0
    obj = json.loads(result.output)
    assert obj["name"] == "mysnap"
    assert obj["key_count"] == 2


def test_summary_show_missing(runner):
    from envsnap.storage import SnapshotNotFoundError
    with patch("envsnap.summary.load_snapshot", side_effect=SnapshotNotFoundError("mysnap")):
        result = runner.invoke(summary_cmd, ["show", "mysnap"])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_summary_all_empty(runner):
    with patch("envsnap.summary.list_snapshots", return_value=[]):
        result = runner.invoke(summary_cmd, ["all"])
    assert result.exit_code == 0
    assert "No snapshots" in result.output
