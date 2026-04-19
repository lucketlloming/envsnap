import pytest
from click.testing import CliRunner
from envsnap.cli_clone import clone_cmd
from envsnap.storage import save_snapshot, get_snapshot_dir
import os


@pytest.fixture
def isolated_snapshot_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVSNAP_DIR", str(tmp_path))
    return tmp_path


@pytest.fixture
def runner():
    return CliRunner()


def _save(name, data, isolated_snapshot_dir):
    save_snapshot(name, data)


def test_clone_run_basic(runner, isolated_snapshot_dir):
    _save("src", {"FOO": "bar", "BAZ": "qux"}, isolated_snapshot_dir)
    result = runner.invoke(clone_cmd, ["run", "src", "dst"])
    assert result.exit_code == 0
    assert "Cloned 'src' → 'dst'" in result.output


def test_clone_run_with_overrides(runner, isolated_snapshot_dir):
    _save("src", {"FOO": "bar"}, isolated_snapshot_dir)
    result = runner.invoke(clone_cmd, ["run", "src", "dst2", "--set", "FOO=override"])
    assert result.exit_code == 0
    assert "override: FOO=override" in result.output


def test_clone_run_missing_source(runner, isolated_snapshot_dir):
    result = runner.invoke(clone_cmd, ["run", "nonexistent", "dst"])
    assert result.exit_code == 1
    assert "Error" in result.output


def test_clone_run_destination_exists_no_force(runner, isolated_snapshot_dir):
    _save("src", {"A": "1"}, isolated_snapshot_dir)
    _save("dst", {"B": "2"}, isolated_snapshot_dir)
    result = runner.invoke(clone_cmd, ["run", "src", "dst"])
    assert result.exit_code == 1
    assert "--force" in result.output


def test_clone_run_destination_exists_with_force(runner, isolated_snapshot_dir):
    _save("src", {"A": "1"}, isolated_snapshot_dir)
    _save("dst", {"B": "2"}, isolated_snapshot_dir)
    result = runner.invoke(clone_cmd, ["run", "src", "dst", "--force"])
    assert result.exit_code == 0
    assert "Cloned 'src' → 'dst'" in result.output


def test_clone_run_invalid_override_format(runner, isolated_snapshot_dir):
    _save("src", {"A": "1"}, isolated_snapshot_dir)
    result = runner.invoke(clone_cmd, ["run", "src", "dst", "--set", "NOEQUALS"])
    assert result.exit_code == 1
    assert "KEY=VALUE" in result.output
