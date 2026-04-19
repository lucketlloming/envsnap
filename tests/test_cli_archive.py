"""Tests for CLI archive commands."""

import json
import pytest
from click.testing import CliRunner
from pathlib import Path

from envsnap.cli_archive import archive_cmd
from envsnap.storage import save_snapshot


@pytest.fixture(autouse=True)
def isolated_snapshot_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("envsnap.storage.get_snapshot_dir", lambda: tmp_path)
    return tmp_path


@pytest.fixture()
def runner():
    return CliRunner()


def _snap(name, data):
    save_snapshot(name, data)


def test_archive_export_text(runner, tmp_path):
    _snap("dev", {"ENV": "dev"})
    dest = str(tmp_path / "out.zip")
    result = runner.invoke(archive_cmd, ["export", dest, "--name", "dev"])
    assert result.exit_code == 0
    assert "1 snapshot" in result.output
    assert "+ dev" in result.output


def test_archive_export_json(runner, tmp_path):
    _snap("prod", {"ENV": "prod"})
    dest = str(tmp_path / "out.zip")
    result = runner.invoke(archive_cmd, ["export", dest, "--name", "prod", "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "prod" in data["included"]


def test_archive_export_missing_snapshot(runner, tmp_path):
    dest = str(tmp_path / "out.zip")
    result = runner.invoke(archive_cmd, ["export", dest, "--name", "ghost"])
    assert result.exit_code != 0
    assert "Error" in result.output or "Error" in (result.output + (result.exception and str(result.exception) or ""))


def test_archive_import_text(runner, tmp_path):
    _snap("staging", {"X": "1"})
    dest = tmp_path / "bundle.zip"
    runner.invoke(archive_cmd, ["export", str(dest), "--name", "staging"])
    # remove original
    save_snapshot("staging", {})
    result = runner.invoke(archive_cmd, ["import", str(dest), "--overwrite"])
    assert result.exit_code == 0
    assert "+ staging" in result.output


def test_archive_import_no_overwrite_fails(runner, tmp_path):
    _snap("snap", {"K": "v"})
    dest = tmp_path / "b.zip"
    runner.invoke(archive_cmd, ["export", str(dest), "--name", "snap"])
    result = runner.invoke(archive_cmd, ["import", str(dest)])
    assert result.exit_code != 0
