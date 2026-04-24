"""Tests for envsnap.cli_chain."""
import json
import pytest
from click.testing import CliRunner

from envsnap.cli_chain import chain_cmd


@pytest.fixture()
def runner():
    return CliRunner()


def _patch(monkeypatch, **kwargs):
    base = "envsnap.cli_chain"
    for name, val in kwargs.items():
        monkeypatch.setattr(f"{base}.{name}", val)


def test_chain_create_text(runner, monkeypatch):
    created = {}
    _patch(monkeypatch, create_chain=lambda n, s: created.update({n: s}))
    result = runner.invoke(chain_cmd, ["create", "mychain", "snap_a", "snap_b"])
    assert result.exit_code == 0
    assert "mychain" in result.output


def test_chain_create_json(runner, monkeypatch):
    _patch(monkeypatch, create_chain=lambda n, s: None)
    result = runner.invoke(chain_cmd, ["create", "--format", "json", "c1", "s1"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["chain"] == "c1"


def test_chain_create_missing_snapshot(runner, monkeypatch):
    from envsnap.snapshot_chain import SnapshotNotFoundError
    _patch(monkeypatch, create_chain=lambda n, s: (_ for _ in ()).throw(SnapshotNotFoundError("x")))
    result = runner.invoke(chain_cmd, ["create", "c", "bad"])
    assert result.exit_code == 1


def test_chain_show_text(runner, monkeypatch):
    _patch(monkeypatch, get_chain=lambda n: ["snap_a", "snap_b"])
    result = runner.invoke(chain_cmd, ["show", "mychain"])
    assert "snap_a" in result.output
    assert "snap_b" in result.output


def test_chain_show_json(runner, monkeypatch):
    _patch(monkeypatch, get_chain=lambda n: ["snap_a"])
    result = runner.invoke(chain_cmd, ["show", "--format", "json", "c"])
    data = json.loads(result.output)
    assert data["snapshots"] == ["snap_a"]


def test_chain_list_empty(runner, monkeypatch):
    _patch(monkeypatch, list_chains=lambda: [])
    result = runner.invoke(chain_cmd, ["list"])
    assert "No chains" in result.output


def test_chain_list_json(runner, monkeypatch):
    _patch(monkeypatch, list_chains=lambda: ["a", "b"])
    result = runner.invoke(chain_cmd, ["list", "--format", "json"])
    data = json.loads(result.output)
    assert data["chains"] == ["a", "b"]


def test_chain_append(runner, monkeypatch):
    appended = {}
    _patch(monkeypatch, append_to_chain=lambda c, s: appended.update({c: s}))
    result = runner.invoke(chain_cmd, ["append", "mychain", "snap_x"])
    assert result.exit_code == 0
    assert "snap_x" in result.output


def test_chain_delete(runner, monkeypatch):
    _patch(monkeypatch, delete_chain=lambda n: None)
    result = runner.invoke(chain_cmd, ["delete", "mychain"])
    assert result.exit_code == 0
    assert "deleted" in result.output
