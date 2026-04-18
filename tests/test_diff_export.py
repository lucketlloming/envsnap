"""Tests for envsnap.diff_export."""
from __future__ import annotations
import json
import pytest
from unittest.mock import patch

from envsnap.diff_export import export_diff

_RESULT = {
    "only_in_a": {"FOO": "1"},
    "only_in_b": {"BAR": "2"},
    "changed": {"BAZ": ("old", "new")},
    "common": {"QUX": "same"},
}


def _patch(monkeypatch):
    monkeypatch.setattr("envsnap.diff_export.compare_snapshots", lambda a, b: _RESULT)


def test_export_diff_text(monkeypatch):
    _patch(monkeypatch)
    output = export_diff("snap_a", "snap_b", fmt="text")
    assert "snap_a" in output
    assert "snap_b" in output
    assert isinstance(output, str)


def test_export_diff_json(monkeypatch):
    _patch(monkeypatch)
    output = export_diff("snap_a", "snap_b", fmt="json")
    data = json.loads(output)
    assert data["snapshot_a"] == "snap_a"
    assert data["snapshot_b"] == "snap_b"
    assert data["only_in_a"] == {"FOO": "1"}
    assert data["only_in_b"] == {"BAR": "2"}
    assert "changed" in data
    assert "common" in data


def test_export_diff_invalid_format(monkeypatch):
    _patch(monkeypatch)
    with pytest.raises(ValueError, match="Unsupported format"):
        export_diff("snap_a", "snap_b", fmt="csv")  # type: ignore[arg-type]


def test_export_diff_writes_file(monkeypatch, tmp_path):
    _patch(monkeypatch)
    out_file = tmp_path / "diff.txt"
    export_diff("snap_a", "snap_b", fmt="text", output_path=str(out_file))
    assert out_file.exists()
    content = out_file.read_text(encoding="utf-8")
    assert "snap_a" in content


def test_export_diff_json_writes_file(monkeypatch, tmp_path):
    _patch(monkeypatch)
    out_file = tmp_path / "diff.json"
    export_diff("snap_a", "snap_b", fmt="json", output_path=str(out_file))
    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert data["snapshot_a"] == "snap_a"


def test_export_diff_no_file_returns_string(monkeypatch):
    _patch(monkeypatch)
    result = export_diff("snap_a", "snap_b", fmt="json")
    assert result  # non-empty string
