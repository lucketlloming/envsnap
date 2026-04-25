"""Tests for envsnap.snapshot_mirror."""
from __future__ import annotations

import json
import pytest
from pathlib import Path

from envsnap import storage
from envsnap.snapshot_mirror import push_snapshot, pull_snapshot, sync_status, MirrorError


@pytest.fixture(autouse=True)
def isolated(tmp_path, monkeypatch):
    snap_dir = tmp_path / "snapshots"
    snap_dir.mkdir()
    monkeypatch.setattr(storage, "get_snapshot_dir", lambda: snap_dir)
    monkeypatch.setattr(storage, "snapshot_path", lambda name: snap_dir / f"{name}.json")
    return snap_dir


def _save(name: str, data: dict, snap_dir: Path):
    (snap_dir / f"{name}.json").write_text(json.dumps(data))


def test_push_creates_remote_file(isolated, tmp_path):
    remote = tmp_path / "remote"
    _save("dev", {"A": "1"}, isolated)
    dest = push_snapshot("dev", str(remote))
    assert dest.exists()
    assert json.loads(dest.read_text()) == {"A": "1"}


def test_push_missing_snapshot_raises(isolated, tmp_path):
    remote = tmp_path / "remote"
    with pytest.raises(MirrorError, match="not found"):
        push_snapshot("ghost", str(remote))


def test_push_no_overwrite_raises(isolated, tmp_path):
    remote = tmp_path / "remote"
    remote.mkdir()
    _save("dev", {"A": "1"}, isolated)
    push_snapshot("dev", str(remote))
    with pytest.raises(MirrorError, match="already exists"):
        push_snapshot("dev", str(remote), overwrite=False)


def test_push_with_overwrite_succeeds(isolated, tmp_path):
    remote = tmp_path / "remote"
    _save("dev", {"A": "1"}, isolated)
    push_snapshot("dev", str(remote))
    _save("dev", {"A": "2"}, isolated)
    push_snapshot("dev", str(remote), overwrite=True)
    assert json.loads((remote / "dev.json").read_text()) == {"A": "2"}


def test_pull_copies_to_local(isolated, tmp_path):
    remote = tmp_path / "remote"
    remote.mkdir()
    (remote / "prod.json").write_text(json.dumps({"X": "y"}))
    dest = pull_snapshot("prod", str(remote))
    assert dest.exists()
    assert json.loads(dest.read_text()) == {"X": "y"}


def test_pull_missing_remote_raises(isolated, tmp_path):
    remote = tmp_path / "remote"
    remote.mkdir()
    with pytest.raises(MirrorError, match="not found"):
        pull_snapshot("ghost", str(remote))


def test_sync_status_categories(isolated, tmp_path):
    remote = tmp_path / "remote"
    remote.mkdir()
    _save("local_only", {"A": "1"}, isolated)
    (remote / "remote_only.json").write_text(json.dumps({"B": "2"}))
    _save("synced", {"C": "3"}, isolated)
    (remote / "synced.json").write_text(json.dumps({"C": "3"}))
    _save("diverged", {"D": "4"}, isolated)
    (remote / "diverged.json").write_text(json.dumps({"D": "DIFFERENT"}))

    result = dict(sync_status(str(remote)))
    assert result["local_only"] == "local-only"
    assert result["remote_only"] == "remote-only"
    assert result["synced"] == "synced"
    assert result["diverged"] == "diverged"
