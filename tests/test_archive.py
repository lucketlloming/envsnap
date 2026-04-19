"""Tests for envsnap.archive."""

import pytest
from pathlib import Path

from envsnap.archive import export_archive, import_archive, ArchiveError
from envsnap.storage import save_snapshot, load_snapshot, list_snapshots


@pytest.fixture(autouse=True)
def isolated_snapshot_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("envsnap.storage.get_snapshot_dir", lambda: tmp_path)
    monkeypatch.setattr("envsnap.archive.list_snapshots", lambda: list_snapshots())
    return tmp_path


def _save(name, data):
    save_snapshot(name, data)


def test_export_and_import_roundtrip(tmp_path):
    _save("snap1", {"A": "1", "B": "2"})
    _save("snap2", {"X": "9"})
    archive = tmp_path / "bundle.zip"
    included = export_archive(["snap1", "snap2"], archive)
    assert set(included) == {"snap1", "snap2"}
    assert archive.exists()

    # wipe and re-import
    save_snapshot("snap1", {})
    save_snapshot("snap2", {})
    imported = import_archive(archive, overwrite=True)
    assert set(imported) == {"snap1", "snap2"}
    assert load_snapshot("snap1") == {"A": "1", "B": "2"}


def test_export_all_when_no_names_given(tmp_path):
    _save("alpha", {"K": "v"})
    archive = tmp_path / "all.zip"
    included = export_archive([], archive)
    assert "alpha" in included


def test_export_missing_snapshot_raises(tmp_path):
    archive = tmp_path / "out.zip"
    with pytest.raises(ArchiveError, match="not found"):
        export_archive(["ghost"], archive)


def test_export_no_snapshots_raises(tmp_path):
    archive = tmp_path / "empty.zip"
    with pytest.raises(ArchiveError, match="No snapshots"):
        export_archive([], archive)


def test_import_missing_archive_raises(tmp_path):
    with pytest.raises(ArchiveError, match="Archive not found"):
        import_archive(tmp_path / "nope.zip")


def test_import_no_overwrite_raises(tmp_path):
    _save("existing", {"K": "old"})
    archive = tmp_path / "bundle.zip"
    export_archive(["existing"], archive)
    with pytest.raises(ArchiveError, match="already exists"):
        import_archive(archive, overwrite=False)
