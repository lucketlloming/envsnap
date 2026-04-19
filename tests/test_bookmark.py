"""Tests for envsnap.bookmark."""
import json
import pytest
from pathlib import Path

import envsnap.bookmark as bm
import envsnap.storage as storage


@pytest.fixture(autouse=True)
def isolated_snapshot_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "get_snapshot_dir", lambda: tmp_path)
    monkeypatch.setattr(bm, "get_snapshot_dir", lambda: tmp_path)
    return tmp_path


def _make_snapshot(tmp_path: Path, name: str) -> None:
    (tmp_path / f"{name}.json").write_text(json.dumps({"KEY": "val"}))


def test_add_and_list_bookmark(tmp_path):
    _make_snapshot(tmp_path, "dev")
    bm.add_bookmark("dev")
    assert bm.list_bookmarks() == ["dev"]


def test_add_bookmark_deduplicates(tmp_path):
    _make_snapshot(tmp_path, "dev")
    bm.add_bookmark("dev")
    bm.add_bookmark("dev")
    assert bm.list_bookmarks().count("dev") == 1


def test_add_bookmark_missing_snapshot_raises(tmp_path):
    with pytest.raises(KeyError, match="does not exist"):
        bm.add_bookmark("ghost")


def test_remove_bookmark(tmp_path):
    _make_snapshot(tmp_path, "dev")
    bm.add_bookmark("dev")
    bm.remove_bookmark("dev")
    assert bm.list_bookmarks() == []


def test_remove_missing_bookmark_raises(tmp_path):
    with pytest.raises(KeyError, match="not found"):
        bm.remove_bookmark("nope")


def test_list_bookmarks_filters_deleted_snapshots(tmp_path):
    _make_snapshot(tmp_path, "dev")
    bm.add_bookmark("dev")
    # delete the snapshot file
    (tmp_path / "dev.json").unlink()
    assert bm.list_bookmarks() == []


def test_is_bookmarked(tmp_path):
    _make_snapshot(tmp_path, "prod")
    assert not bm.is_bookmarked("prod")
    bm.add_bookmark("prod")
    assert bm.is_bookmarked("prod")
