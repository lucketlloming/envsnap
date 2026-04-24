"""Tests for envsnap.snapshot_quota."""
from __future__ import annotations

import pytest

from envsnap.snapshot_quota import (
    QuotaExceededError,
    QuotaNotFoundError,
    check_quota,
    get_quota,
    list_quotas,
    remove_quota,
    set_quota,
)


@pytest.fixture(autouse=True)
def isolated_snapshot_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("envsnap.snapshot_quota.get_snapshot_dir", lambda: tmp_path)
    monkeypatch.setattr("envsnap.storage.get_snapshot_dir", lambda: tmp_path)
    return tmp_path


def test_set_and_get_quota():
    set_quota("projectA", 10)
    q = get_quota("projectA")
    assert q is not None
    assert q["max_snapshots"] == 10


def test_get_quota_missing_returns_none():
    assert get_quota("nonexistent") is None


def test_set_quota_invalid_raises():
    with pytest.raises(ValueError):
        set_quota("projectA", 0)


def test_remove_quota():
    set_quota("projectA", 5)
    remove_quota("projectA")
    assert get_quota("projectA") is None


def test_remove_missing_quota_raises():
    with pytest.raises(QuotaNotFoundError):
        remove_quota("ghost")


def test_list_quotas_empty():
    assert list_quotas() == {}


def test_list_quotas_returns_all():
    set_quota("a", 3)
    set_quota("b", 7)
    result = list_quotas()
    assert "a" in result
    assert "b" in result


def test_check_quota_no_config_passes(monkeypatch):
    monkeypatch.setattr("envsnap.snapshot_quota.list_snapshots", lambda: ["s1", "s2"])
    # no quota set — should not raise
    check_quota("projectX")


def test_check_quota_within_limit(monkeypatch):
    monkeypatch.setattr("envsnap.snapshot_quota.list_snapshots", lambda: ["proj_s1"])
    set_quota("proj", 3)
    check_quota("proj", prefix="proj_")


def test_check_quota_exceeded(monkeypatch):
    monkeypatch.setattr(
        "envsnap.snapshot_quota.list_snapshots",
        lambda: ["proj_s1", "proj_s2", "proj_s3"],
    )
    set_quota("proj", 3)
    with pytest.raises(QuotaExceededError):
        check_quota("proj", prefix="proj_")
