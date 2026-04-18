import json
import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envsnap.cli_audit import audit_cmd
import envsnap.audit as audit_mod


@pytest.fixture(autouse=True)
def isolated_snapshot_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("envsnap.audit.get_snapshot_dir", lambda: tmp_path)
    return tmp_path


@pytest.fixture
def runner():
    return CliRunner()


def _add(action, snap, user="tester"):
    audit_mod.record_audit(action, snap, user=user)


def test_audit_log_empty(runner):
    result = runner.invoke(audit_cmd, ["log"])
    assert result.exit_code == 0
    assert "No audit entries" in result.output


def test_audit_log_text(runner):
    _add("snap", "mysnap")
    result = runner.invoke(audit_cmd, ["log"])
    assert result.exit_code == 0
    assert "snap" in result.output
    assert "mysnap" in result.output


def test_audit_log_json(runner):
    _add("restore", "s1")
    result = runner.invoke(audit_cmd, ["log", "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data[0]["action"] == "restore"


def test_audit_log_filtered(runner):
    _add("snap", "alpha")
    _add("snap", "beta")
    result = runner.invoke(audit_cmd, ["log", "alpha"])
    assert "alpha" in result.output
    assert "beta" not in result.output


def test_audit_clear_with_yes(runner):
    _add("snap", "s1")
    result = runner.invoke(audit_cmd, ["clear", "--yes"])
    assert result.exit_code == 0
    assert "Removed 1" in result.output
    assert audit_mod.get_audit() == []


def test_audit_clear_specific(runner):
    _add("snap", "keep")
    _add("snap", "gone")
    result = runner.invoke(audit_cmd, ["clear", "gone", "--yes"])
    assert "Removed 1" in result.output
    remaining = audit_mod.get_audit()
    assert len(remaining) == 1
    assert remaining[0]["snapshot"] == "keep"
