"""Tests for envsnap.lock and envsnap.cli_lock."""
from __future__ import annotations

import json
import pytest
from click.testing import CliRunner
from unittest.mock import patch

from envsnap.cli_lock import lock_cmd


@pytest.fixture()
def isolated_snapshot_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVSNAP_DIR", str(tmp_path))
    return tmp_path


def _make_snapshot(tmp_path, name):
    snap = tmp_path / f"{name}.json"
    snap.write_text(json.dumps({"FOO": "bar"}))


@pytest.fixture()
def runner():
    return CliRunner()


def test_lock_and_unlock(isolated_snapshot_dir, runner):
    _make_snapshot(isolated_snapshot_dir, "mysnap")
    r = runner.invoke(lock_cmd, ["set", "mysnap"])
    assert r.exit_code == 0
    assert "locked" in r.output

    r = runner.invoke(lock_cmd, ["status", "mysnap"])
    assert "locked" in r.output

    r = runner.invoke(lock_cmd, ["unset", "mysnap"])
    assert r.exit_code == 0
    assert "unlocked" in r.output


def test_lock_missing_snapshot(isolated_snapshot_dir, runner):
    r = runner.invoke(lock_cmd, ["set", "ghost"])
    assert r.exit_code == 1
    assert "not found" in r.output.lower() or "not found" in (r.output + r.exception.__str__() if r.exception else r.output).lower()


def test_lock_status_json(isolated_snapshot_dir, runner):
    _make_snapshot(isolated_snapshot_dir, "s1")
    runner.invoke(lock_cmd, ["set", "s1"])
    r = runner.invoke(lock_cmd, ["status", "s1", "--json"])
    data = json.loads(r.output)
    assert data == {"name": "s1", "locked": True}


def test_lock_list(isolated_snapshot_dir, runner):
    _make_snapshot(isolated_snapshot_dir, "a")
    _make_snapshot(isolated_snapshot_dir, "b")
    runner.invoke(lock_cmd, ["set", "a"])
    r = runner.invoke(lock_cmd, ["list"])
    assert "a" in r.output
    assert "b" not in r.output


def test_lock_list_json(isolated_snapshot_dir, runner):
    _make_snapshot(isolated_snapshot_dir, "x")
    runner.invoke(lock_cmd, ["set", "x"])
    r = runner.invoke(lock_cmd, ["list", "--json"])
    data = json.loads(r.output)
    assert "x" in data


def test_assert_not_locked_raises(isolated_snapshot_dir):
    from envsnap.lock import lock_snapshot, assert_not_locked, SnapshotLockedError
    _make_snapshot(isolated_snapshot_dir, "locked_snap")
    lock_snapshot("locked_snap")
    with pytest.raises(SnapshotLockedError):
        assert_not_locked("locked_snap")
