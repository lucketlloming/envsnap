"""Tests for envsnap.snapshot_digest and envsnap.cli_digest."""
from __future__ import annotations

import json
import os
import pytest
from click.testing import CliRunner
from unittest.mock import patch

from envsnap.snapshot_digest import compute_digest, verify_digest, compare_digests, digest_all
from envsnap.cli_digest import digest_cmd


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def isolated_snapshot_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVSNAP_DIR", str(tmp_path))
    return tmp_path


def _save(name: str, data: dict, base: object) -> None:
    from envsnap.storage import save_snapshot
    save_snapshot(name, data)


# ---------------------------------------------------------------------------
# Unit tests for snapshot_digest module
# ---------------------------------------------------------------------------

def test_compute_digest_is_deterministic(isolated_snapshot_dir):
    _save("snap1", {"B": "2", "A": "1"}, isolated_snapshot_dir)
    d1 = compute_digest("snap1")
    d2 = compute_digest("snap1")
    assert d1 == d2
    assert len(d1) == 64  # SHA-256 hex


def test_compute_digest_changes_with_data(isolated_snapshot_dir):
    _save("snap1", {"KEY": "old"}, isolated_snapshot_dir)
    d1 = compute_digest("snap1")
    _save("snap1", {"KEY": "new"}, isolated_snapshot_dir)
    d2 = compute_digest("snap1")
    assert d1 != d2


def test_verify_digest_match(isolated_snapshot_dir):
    _save("snap1", {"X": "1"}, isolated_snapshot_dir)
    digest = compute_digest("snap1")
    assert verify_digest("snap1", digest) is True


def test_verify_digest_mismatch(isolated_snapshot_dir):
    _save("snap1", {"X": "1"}, isolated_snapshot_dir)
    assert verify_digest("snap1", "deadbeef" * 8) is False


def test_compare_digests_match(isolated_snapshot_dir):
    _save("a", {"K": "v"}, isolated_snapshot_dir)
    _save("b", {"K": "v"}, isolated_snapshot_dir)
    result = compare_digests("a", "b")
    assert result["match"] is True
    assert result["a"] == result["b"]


def test_compare_digests_differ(isolated_snapshot_dir):
    _save("a", {"K": "v1"}, isolated_snapshot_dir)
    _save("b", {"K": "v2"}, isolated_snapshot_dir)
    result = compare_digests("a", "b")
    assert result["match"] is False


def test_digest_all_returns_all(isolated_snapshot_dir):
    _save("snap1", {"A": "1"}, isolated_snapshot_dir)
    _save("snap2", {"B": "2"}, isolated_snapshot_dir)
    all_digests = digest_all()
    assert set(all_digests.keys()) == {"snap1", "snap2"}
    assert all(len(v) == 64 for v in all_digests.values())


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------

@pytest.fixture()
def runner():
    return CliRunner()


def test_cli_digest_show_text(isolated_snapshot_dir, runner):
    _save("mysnap", {"FOO": "bar"}, isolated_snapshot_dir)
    result = runner.invoke(digest_cmd, ["show", "mysnap"])
    assert result.exit_code == 0
    assert "mysnap:" in result.output


def test_cli_digest_show_json(isolated_snapshot_dir, runner):
    _save("mysnap", {"FOO": "bar"}, isolated_snapshot_dir)
    result = runner.invoke(digest_cmd, ["show", "--format", "json", "mysnap"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["snapshot"] == "mysnap"
    assert len(data["digest"]) == 64


def test_cli_digest_verify_ok(isolated_snapshot_dir, runner):
    _save("mysnap", {"FOO": "bar"}, isolated_snapshot_dir)
    digest = compute_digest("mysnap")
    result = runner.invoke(digest_cmd, ["verify", "mysnap", digest])
    assert result.exit_code == 0
    assert "OK" in result.output


def test_cli_digest_verify_mismatch(isolated_snapshot_dir, runner):
    _save("mysnap", {"FOO": "bar"}, isolated_snapshot_dir)
    result = runner.invoke(digest_cmd, ["verify", "mysnap", "0" * 64])
    assert result.exit_code != 0
    assert "MISMATCH" in result.output


def test_cli_digest_compare_text(isolated_snapshot_dir, runner):
    _save("a", {"K": "v"}, isolated_snapshot_dir)
    _save("b", {"K": "v"}, isolated_snapshot_dir)
    result = runner.invoke(digest_cmd, ["compare", "a", "b"])
    assert result.exit_code == 0
    assert "MATCH" in result.output


def test_cli_digest_all_text(isolated_snapshot_dir, runner):
    _save("s1", {"A": "1"}, isolated_snapshot_dir)
    _save("s2", {"B": "2"}, isolated_snapshot_dir)
    result = runner.invoke(digest_cmd, ["all"])
    assert result.exit_code == 0
    assert "s1:" in result.output
    assert "s2:" in result.output
