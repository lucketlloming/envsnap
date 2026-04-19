import json
import pytest
from click.testing import CliRunner
from envsnap.cli_remind import remindnfrom envsnap.storage import save_snapshot
import envsnap.storage as _st
import envsnap.remind as _rm


@pytest.fixture(autouse=True)	mp_path, monkeypatch):
    monkeypatch.setattr(_st, "_SNAPSHOT_DIR", tmp_path)
    monkeypatch.setattr(_rm, "get_snapshot_dir", lambda: tmp_path)
    return tmp_path


@pytest.fixture
def runner():
    return CliRunner()


def _snap(name):
    save_snapshot(name, {"K": "V"})


def test_remind_set(runner, isolated_snapshot_dir):
    _snap("dev")
    result = runner.invoke(remind_cmd, ["set", "dev", "Check logs", "--due", "2099-01-01"])
    assert result.exit_code == 0
    assert "Reminder set" in result.output


def test_remind_set_missing_snapshot(runner, isolated_snapshot_dir):
    result = runner.invoke(remind_cmd, ["set", "ghost", "msg"])
    assert result.exit_code == 1


def test_remind_show_text(runner, isolated_snapshot_dir):
    _snap("dev")
    runner.invoke(remind_cmd, ["set", "dev", "Deploy soon", "--due", "2099-06-01"])
    result = runner.invoke(remind_cmd, ["show", "dev"])
    assert "Deploy soon" in result.output
    assert "2099-06-01" in result.output


def test_remind_show_json(runner, isolated_snapshot_dir):
    _snap("dev")
    runner.invoke(remind_cmd, ["set", "dev", "JSON test", "--due", "2099-03-15"])
    result = runner.invoke(remind_cmd, ["show", "--format", "json", "dev"])
    data = json.loads(result.output)
    assert data["dev"]["message"] == "JSON test"


def test_remind_show_missing(runner, isolated_snapshot_dir):
    result = runner.invoke(remind_cmd, ["show", "ghost"])
    assert result.exit_code == 1


def test_remind_remove(runner, isolated_snapshot_dir):
    _snap("dev")
    runner.invoke(remind_cmd, ["set", "dev", "msg"])
    result = runner.invoke(remind_cmd, ["remove", "dev"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remind_list(runner, isolated_snapshot_dir):
    _snap("a")
    _snap("b")
    runner.invoke(remind_cmd, ["set", "a", "First"])
    runner.invoke(remind_cmd, ["set", "b", "Second"])
    result = runner.invoke(remind_cmd, ["list"])
    assert "First" in result.output
    assert "Second" in result.output


def test_remind_due(runner, isolated_snapshot_dir):
    _snap("old")
    runner.invoke(remind_cmd, ["set", "old", "overdue", "--due", "2000-01-01"])
    result = runner.invoke(remind_cmd, ["due", "--as-of", "2024-01-01"])
    assert "overdue" in result.output
