"""Tests for envsnap.export module."""

import json
import os
import pytest
from pathlib import Path

from envsnap import storage
from envsnap.export import export_snapshot, import_snapshot


@pytest.fixture(autouse=True)
def isolated_snapshot_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "get_snapshot_dir", lambda: tmp_path)
    return tmp_path


SAMPLE = {"FOO": "bar", "BAZ": "qux"}


def _save(name, data=SAMPLE):
    storage.save_snapshot(name, data)


def test_export_json(tmp_path):
    _save("mysnap")
    out = tmp_path / "out.json"
    export_snapshot("mysnap", str(out), fmt="json")
    loaded = json.loads(out.read_text())
    assert loaded == SAMPLE


def test_export_env(tmp_path):
    _save("mysnap")
    out = tmp_path / "out.env"
    export_snapshot("mysnap", str(out), fmt="env")
    content = out.read_text()
    assert "FOO=bar" in content
    assert "BAZ=qux" in content


def test_export_invalid_format(tmp_path):
    _save("mysnap")
    with pytest.raises(ValueError, match="Unsupported format"):
        export_snapshot("mysnap", str(tmp_path / "x.txt"), fmt="toml")


def test_import_json(tmp_path):
    src = tmp_path / "snap.json"
    src.write_text(json.dumps(SAMPLE))
    import_snapshot("imported", str(src))
    assert storage.load_snapshot("imported") == SAMPLE


def test_import_env(tmp_path):
    src = tmp_path / "snap.env"
    src.write_text("FOO=bar\n# comment\nBAZ=qux\n")
    import_snapshot("imported", str(src), fmt="env")
    assert storage.load_snapshot("imported") == SAMPLE


def test_import_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        import_snapshot("x", str(tmp_path / "nope.env"))


def test_import_auto_detects_json(tmp_path):
    src = tmp_path / "snap.json"
    src.write_text(json.dumps(SAMPLE))
    import_snapshot("auto", str(src))  # no fmt arg
    assert storage.load_snapshot("auto") == SAMPLE
