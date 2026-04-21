"""Tests for envsnap.retention module."""

from __future__ import annotations

import json
import pytest

from envsnap.retention import (
    RetentionError,
    set_retention,
    get_retention,
    remove_retention,
    list_retention,
)


@pytest.fixture(autouse=True)
def isolated_snapshot_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("envsnap.retention.get_snapshot_dir", lambda: tmp_path)
    return tmp_path


def test_set_and_get_retention():
    set_retention("mysnap", max_count=5, action="warn")
    policy = get_retention("mysnap")
    assert policy is not None
    assert policy["max_count"] == 5
    assert policy["max_age_days"] is None
    assert policy["action"] == "warn"


def test_set_retention_with_age():
    set_retention("oldsnap", max_age_days=30, action="delete")
    policy = get_retention("oldsnap")
    assert policy["max_age_days"] == 30
    assert policy["max_count"] is None
    assert policy["action"] == "delete"


def test_set_retention_both_constraints():
    set_retention("combo", max_count=10, max_age_days=14, action="warn")
    policy = get_retention("combo")
    assert policy["max_count"] == 10
    assert policy["max_age_days"] == 14


def test_set_retention_invalid_action_raises():
    with pytest.raises(RetentionError, match="Invalid action"):
        set_retention("snap", max_count=3, action="archive")


def test_set_retention_no_constraints_raises():
    with pytest.raises(RetentionError, match="At least one"):
        set_retention("snap", action="warn")


def test_set_retention_invalid_max_count_raises():
    with pytest.raises(RetentionError, match="max_count must be at least 1"):
        set_retention("snap", max_count=0)


def test_set_retention_invalid_max_age_raises():
    with pytest.raises(RetentionError, match="max_age_days must be at least 1"):
        set_retention("snap", max_age_days=-5)


def test_get_retention_missing_returns_none():
    assert get_retention("nonexistent") is None


def test_remove_retention():
    set_retention("snap", max_count=3)
    remove_retention("snap")
    assert get_retention("snap") is None


def test_remove_retention_missing_raises():
    with pytest.raises(RetentionError, match="No retention policy found"):
        remove_retention("ghost")


def test_list_retention_returns_all():
    set_retention("a", max_count=1)
    set_retention("b", max_age_days=7)
    policies = list_retention()
    assert "a" in policies
    assert "b" in policies


def test_list_retention_empty():
    assert list_retention() == {}
