"""Tests for envsnap.snapshot_index and envsnap.cli_index."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from envsnap.cli_index import index_cmd


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SNAP_A = {"FOO": "bar", "BAZ": "qux"}
_SNAP_B = {"ALPHA": "1"}


def _patch(snapshots: dict, tags: dict | None = None, pins: dict | None = None, notes: dict | None = None):
    """Context manager that patches storage / metadata helpers."""
    tags = tags or {}
    pins = pins or {}
    notes = notes or {}

    def _list():
        return list(snapshots.keys())

    def _load(name):
        if name not in snapshots:
            raise FileNotFoundError(name)
        return snapshots[name]

    return patch.multiple(
        "envsnap.snapshot_index",
        list_snapshots=_list,
        load_snapshot=_load,
        get_tags=lambda name: tags.get(name, []),
        get_pin=lambda name: pins.get(name),
        get_note=lambda name: notes.get(name),
    )


@pytest.fixture()
def runner():
    return CliRunner()


# ---------------------------------------------------------------------------
# Unit tests for build_index / query_index
# ---------------------------------------------------------------------------

def test_build_index_returns_metadata():
    from envsnap.snapshot_index import build_index

    with _patch({"snap_a": _SNAP_A, "snap_b": _SNAP_B}, tags={"snap_a": ["prod"]}, pins={"snap_b": "v1"}):
        index = build_index()

    assert set(index.keys()) == {"snap_a", "snap_b"}
    assert index["snap_a"]["key_count"] == 2
    assert index["snap_a"]["tags"] == ["prod"]
    assert index["snap_a"]["pinned"] is False
    assert index["snap_b"]["pinned"] is True


def test_query_index_filter_by_tag():
    from envsnap.snapshot_index import query_index

    index = {
        "a": {"key_count": 2, "tags": ["prod"], "pinned": False, "note": None},
        "b": {"key_count": 1, "tags": [], "pinned": False, "note": None},
    }
    assert query_index(index, tag="prod") == ["a"]


def test_query_index_filter_by_pinned():
    from envsnap.snapshot_index import query_index

    index = {
        "a": {"key_count": 2, "tags": [], "pinned": True, "note": None},
        "b": {"key_count": 1, "tags": [], "pinned": False, "note": None},
    }
    assert query_index(index, pinned=True) == ["a"]


def test_query_index_filter_by_key_count():
    from envsnap.snapshot_index import query_index

    index = {
        "a": {"key_count": 5, "tags": [], "pinned": False, "note": None},
        "b": {"key_count": 1, "tags": [], "pinned": False, "note": None},
    }
    assert query_index(index, min_keys=3) == ["a"]
    assert query_index(index, max_keys=2) == ["b"]


def test_query_index_filter_has_note():
    from envsnap.snapshot_index import query_index

    index = {
        "a": {"key_count": 1, "tags": [], "pinned": False, "note": "hello"},
        "b": {"key_count": 1, "tags": [], "pinned": False, "note": None},
    }
    assert query_index(index, has_note=True) == ["a"]
    assert query_index(index, has_note=False) == ["b"]


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------

def test_index_refresh_text(runner):
    with _patch({"snap_a": _SNAP_A}):
        with patch("envsnap.snapshot_index.save_index"):
            result = runner.invoke(index_cmd, ["refresh"])
    assert result.exit_code == 0
    assert "1 snapshot" in result.output


def test_index_refresh_json(runner):
    with _patch({"snap_a": _SNAP_A}):
        with patch("envsnap.snapshot_index.save_index"):
            result = runner.invoke(index_cmd, ["refresh", "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "snap_a" in data["refreshed"]


def test_index_query_no_results(runner):
    fake_index = {"snap_a": {"key_count": 1, "tags": [], "pinned": False, "note": None}}
    with patch("envsnap.cli_index.load_index", return_value=fake_index):
        result = runner.invoke(index_cmd, ["query", "--tag", "missing"])
    assert result.exit_code == 0
    assert "No snapshots matched" in result.output


def test_index_show_text(runner):
    fake_index = {"snap_a": {"key_count": 3, "tags": ["dev"], "pinned": True, "note": "my note", "keys": []}}
    with patch("envsnap.cli_index.load_index", return_value=fake_index):
        result = runner.invoke(index_cmd, ["show", "snap_a"])
    assert result.exit_code == 0
    assert "snap_a" in result.output
    assert "3" in result.output
    assert "dev" in result.output


def test_index_show_missing(runner):
    with patch("envsnap.cli_index.load_index", return_value={}):
        result = runner.invoke(index_cmd, ["show", "ghost"])
    assert result.exit_code != 0
