"""Tests for envsnap.profiles."""

import pytest
from pathlib import Path

from envsnap import profiles
from envsnap.storage import get_snapshot_dir


@pytest.fixture(autouse=True)
def isolated_snapshot_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("envsnap.storage._SNAPSHOT_DIR", tmp_path)
    monkeypatch.setattr("envsnap.profiles.get_snapshot_dir", lambda: tmp_path)
    yield tmp_path


def test_add_and_get_profile():
    profiles.add_to_profile("work", "snap1")
    profiles.add_to_profile("work", "snap2")
    assert profiles.get_profile("work") == ["snap1", "snap2"]


def test_add_deduplicates():
    profiles.add_to_profile("dev", "snap1")
    profiles.add_to_profile("dev", "snap1")
    assert profiles.get_profile("dev") == ["snap1"]


def test_remove_from_profile():
    profiles.add_to_profile("work", "snap1")
    profiles.add_to_profile("work", "snap2")
    profiles.remove_from_profile("work", "snap1")
    assert profiles.get_profile("work") == ["snap2"]


def test_remove_cleans_empty_profile():
    profiles.add_to_profile("tmp", "snap1")
    profiles.remove_from_profile("tmp", "snap1")
    assert "tmp" not in profiles.list_profiles()


def test_list_profiles():
    profiles.add_to_profile("a", "s1")
    profiles.add_to_profile("b", "s2")
    assert set(profiles.list_profiles()) == {"a", "b"}


def test_delete_profile():
    profiles.add_to_profile("gone", "snap1")
    profiles.delete_profile("gone")
    assert profiles.get_profile("gone") == []
    assert "gone" not in profiles.list_profiles()


def test_get_missing_profile_returns_empty():
    assert profiles.get_profile("nonexistent") == []
