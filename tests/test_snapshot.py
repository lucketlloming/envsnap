"""Tests for envsnap.snapshot module."""

import os
import pytest
from envsnap.snapshot import capture, restore, diff


@pytest.fixture(autouse=True)
def isolated_snapshot_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVSNAP_DIR", str(tmp_path))


def test_capture_all(monkeypatch):
    monkeypatch.setenv("MY_VAR", "hello")
    variables = capture("full")
    assert "MY_VAR" in variables
    assert variables["MY_VAR"] == "hello"


def test_capture_specific_keys(monkeypatch):
    monkeypatch.setenv("KEEP", "yes")
    monkeypatch.setenv("SKIP", "no")
    variables = capture("partial", keys=["KEEP"])
    assert "KEEP" in variables
    assert "SKIP" not in variables


def test_capture_missing_key_ignored(monkeypatch):
    variables = capture("safe", keys=["DEFINITELY_NOT_SET_XYZ"])
    assert "DEFINITELY_NOT_SET_XYZ" not in variables


def test_restore_sets_env(monkeypatch):
    capture_env = {"RESTORED_VAR": "restored_value"}
    from envsnap.storage import save_snapshot
    save_snapshot("restore_test", capture_env)
    monkeypatch.delenv("RESTORED_VAR", raising=False)
    restore("restore_test")
    assert os.environ.get("RESTORED_VAR") == "restored_value"


def test_diff_detects_changes(monkeypatch):
    monkeypatch.setenv("DIFF_VAR", "old_value")
    capture("diffsnap")
    monkeypatch.setenv("DIFF_VAR", "new_value")
    monkeypatch.setenv("EXTRA_VAR", "extra")
    result = diff("diffsnap")
    assert "DIFF_VAR" in result["changed"]
    assert result["changed"]["DIFF_VAR"]["old"] == "old_value"
    assert result["changed"]["DIFF_VAR"]["new"] == "new_value"
    assert "EXTRA_VAR" in result["added"]
