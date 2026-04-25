"""Tests for envsnap.cli_mirror."""
from __future__ import annotations

import json
import pytest
from click.testing import CliRunner
from pathlib import Path

from envsnap.cli_mirror import mirror_cmd
from envsnap import storage


@pytest.fixture()
def isolated(tmp_path, monkeypatch):
    snap_dir = tmp_path / "snapshots"
    snap_dir.mkdir()
    monkeypatch.setattr(storage, "get_snapshot_dir", lambda: snap_dir)
    monkeypatch.setattr(storage, "snapshot_path", lambda name: snap_dir / f"{name}.json")
    monkeypatch.setattr(storage, "list_snapshots", lambda: [p.stem for p in snap_dir.glob("*.json")])
    return snap_dir


@pytest.fixture()
def runner():
    return CliRunner()


def _snap(name: str, data: dict, snap_dir: Path):
    (snap_dir / f"{name}.json").write_text(json.dumps(data))


def test_push_text_output(isolated, runner, tmp_path):
    remote = tmp_path / "remote"
    _snap("dev", {"A": "1"}, isolated)
    result = runner.invoke(mirror_cmd, ["push", "dev", str(remote)])
    assert result.exit_code == 0
    assert "Pushed 'dev'" in result.output


def test_push_json_output(isolated, runner, tmp_path):
    remote = tmp_path / "remote"
    _snap("dev", {"A": "1"}, isolated)
    result = runner.invoke(mirror_cmd, ["push", "dev", str(remote), "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["pushed"] == "dev"


def test_push_missing_snapshot_error(isolated, runner, tmp_path):
    remote = tmp_path / "remote"
    result = runner.invoke(mirror_cmd, ["push", "ghost", str(remote)])
    assert result.exit_code == 1
    assert "Error" in result.output


def test_pull_text_output(isolated, runner, tmp_path):
    remote = tmp_path / "remote"
    remote.mkdir()
    (remote / "prod.json").write_text(json.dumps({"X": "y"}))
    result = runner.invoke(mirror_cmd, ["pull", "prod", str(remote)])
    assert result.exit_code == 0
    assert "Pulled 'prod'" in result.output


def test_status_text_output(isolated, runner, tmp_path):
    remote = tmp_path / "remote"
    remote.mkdir()
    _snap("alpha", {"K": "v"}, isolated)
    (remote / "alpha.json").write_text(json.dumps({"K": "v"}))
    result = runner.invoke(mirror_cmd, ["status", str(remote)])
    assert result.exit_code == 0
    assert "synced" in result.output


def test_status_json_output(isolated, runner, tmp_path):
    remote = tmp_path / "remote"
    remote.mkdir()
    _snap("beta", {"K": "v"}, isolated)
    result = runner.invoke(mirror_cmd, ["status", str(remote), "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert isinstance(data, list)
    assert data[0]["name"] == "beta"
    assert data[0]["status"] == "local-only"
