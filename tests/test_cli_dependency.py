"""Tests for envsnap.cli_dependency."""

from __future__ import annotations

import json
import pytest
from click.testing import CliRunner

from envsnap.cli_dependency import dependency_cmd


_existing = set()
_deps_store = {}


@pytest.fixture(autouse=True)
def _patch(monkeypatch, tmp_path):
    _existing.clear()
    _deps_store.clear()
    monkeypatch.setattr("envsnap.cli_dependency.add_dependency", _fake_add)
    monkeypatch.setattr("envsnap.cli_dependency.remove_dependency", _fake_remove)
    monkeypatch.setattr("envsnap.cli_dependency.get_dependencies", lambda s: _deps_store.get(s, []))
    monkeypatch.setattr("envsnap.cli_dependency.get_dependents", lambda s: [k for k, v in _deps_store.items() if s in v])
    monkeypatch.setattr("envsnap.cli_dependency.all_dependencies", lambda: dict(_deps_store))


from envsnap.dependency import DependencyError, SnapshotNotFoundError, CircularDependencyError


def _fake_add(snap, dep):
    if snap == "missing" or dep == "missing":
        raise SnapshotNotFoundError("not found")
    _deps_store.setdefault(snap, [])
    if dep not in _deps_store[snap]:
        _deps_store[snap].append(dep)


def _fake_remove(snap, dep):
    if dep not in _deps_store.get(snap, []):
        raise DependencyError("not a dependency")
    _deps_store[snap].remove(dep)


@pytest.fixture
def runner():
    return CliRunner()


def test_dep_add(runner):
    result = runner.invoke(dependency_cmd, ["add", "a", "b"])
    assert result.exit_code == 0
    assert "Added dependency" in result.output
    assert _deps_store == {"a": ["b"]}


def test_dep_add_missing_snapshot(runner):
    result = runner.invoke(dependency_cmd, ["add", "missing", "b"])
    assert result.exit_code == 1
    assert "Error" in result.output


def test_dep_remove(runner):
    _deps_store["a"] = ["b"]
    result = runner.invoke(dependency_cmd, ["remove", "a", "b"])
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_dep_remove_missing(runner):
    result = runner.invoke(dependency_cmd, ["remove", "a", "ghost"])
    assert result.exit_code == 1


def test_dep_show_text(runner):
    _deps_store["a"] = ["b"]
    result = runner.invoke(dependency_cmd, ["show", "a"])
    assert result.exit_code == 0
    assert "b" in result.output


def test_dep_show_json(runner):
    _deps_store["a"] = ["b"]
    result = runner.invoke(dependency_cmd, ["show", "a", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["dependencies"] == ["b"]


def test_dep_list_empty(runner):
    result = runner.invoke(dependency_cmd, ["list"])
    assert result.exit_code == 0
    assert "No dependencies" in result.output


def test_dep_list_json(runner):
    _deps_store["x"] = ["y"]
    result = runner.invoke(dependency_cmd, ["list", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data == {"x": ["y"]}
