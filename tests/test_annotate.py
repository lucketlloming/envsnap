"""Tests for envsnap.annotate."""
import json
import pytest

from envsnap import annotate
from envsnap.storage import save_snapshot


@pytest.fixture(autouse=True)
def isolated_snapshot_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("envsnap.storage.get_snapshot_dir", lambda: tmp_path)
    monkeypatch.setattr("envsnap.annotate.get_snapshot_dir", lambda: tmp_path)
    monkeypatch.setattr("envsnap.annotate.list_snapshots", lambda: ["snap1", "snap2"])
    return tmp_path


def test_set_and_get_annotation(isolated_snapshot_dir):
    annotate.set_annotation("snap1", "author", "alice")
    result = annotate.get_annotations("snap1")
    assert result["author"] == "alice"


def test_set_multiple_annotations(isolated_snapshot_dir):
    annotate.set_annotation("snap1", "author", "alice")
    annotate.set_annotation("snap1", "env", "production")
    result = annotate.get_annotations("snap1")
    assert result == {"author": "alice", "env": "production"}


def test_get_annotations_missing_snapshot_returns_empty(isolated_snapshot_dir):
    result = annotate.get_annotations("nonexistent")
    assert result == {}


def test_set_annotation_missing_snapshot_raises(isolated_snapshot_dir):
    with pytest.raises(KeyError, match="ghost"):
        annotate.set_annotation("ghost", "k", "v")


def test_remove_annotation(isolated_snapshot_dir):
    annotate.set_annotation("snap1", "author", "alice")
    annotate.set_annotation("snap1", "env", "dev")
    annotate.remove_annotation("snap1", "author")
    result = annotate.get_annotations("snap1")
    assert "author" not in result
    assert result["env"] == "dev"


def test_remove_annotation_cleans_empty_entry(isolated_snapshot_dir):
    annotate.set_annotation("snap1", "k", "v")
    annotate.remove_annotation("snap1", "k")
    data = json.loads((isolated_snapshot_dir / "annotations.json").read_text())
    assert "snap1" not in data


def test_clear_annotations(isolated_snapshot_dir):
    annotate.set_annotation("snap1", "a", "1")
    annotate.set_annotation("snap1", "b", "2")
    annotate.clear_annotations("snap1")
    assert annotate.get_annotations("snap1") == {}


def test_all_annotations(isolated_snapshot_dir):
    annotate.set_annotation("snap1", "x", "1")
    annotate.set_annotation("snap2", "y", "2")
    result = annotate.all_annotations()
    assert result["snap1"] == {"x": "1"}
    assert result["snap2"] == {"y": "2"}
