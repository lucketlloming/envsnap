"""Integration tests for export/import CLI commands."""

import json
import pytest
from click.testing import CliRunner
from pathlib import Path

from envsnap import storage
from envsnap.cli_export import export_cmd, import_cmd


@pytest.fixture(autouse=True)
def isolated_snapshot_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "get_snapshot_dir", lambda: tmp_path)
    return tmp_path


SAMPLE = {"KEY": "value"}


def test_export_cmd_json(tmp_path):
    storage.save_snapshot("s1", SAMPLE)
    out = tmp_path / "s1.json"
    runner = CliRunner()
    result = runner.invoke(export_cmd, ["s1", str(out)])
    assert result.exit_code == 0
    assert "Exported" in result.output
    assert json.loads(out.read_text()) == SAMPLE


def test_export_cmd_env(tmp_path):
    storage.save_snapshot("s2", SAMPLE)
    out = tmp_path / "s2.env"
    runner = CliRunner()
    result = runner.invoke(export_cmd, ["s2", str(out), "--format", "env"])
    assert result.exit_code == 0
    assert "KEY=value" in out.read_text()


def test_export_cmd_missing_snapshot(tmp_path):
    runner = CliRunner()
    result = runner.invoke(export_cmd, ["ghost", str(tmp_path / "g.json")])
    assert result.exit_code != 0


def test_import_cmd_json(tmp_path):
    src = tmp_path / "data.json"
    src.write_text(json.dumps(SAMPLE))
    runner = CliRunner()
    result = runner.invoke(import_cmd, ["new", str(src)])
    assert result.exit_code == 0
    assert storage.load_snapshot("new") == SAMPLE


def test_import_cmd_missing_file(tmp_path):
    runner = CliRunner()
    result = runner.invoke(import_cmd, ["x", str(tmp_path / "nope.env")])
    assert result.exit_code != 0
    assert "Error" in result.output
