"""Tests for envsnap.search."""
import pytest
from unittest.mock import patch
from envsnap.search import search_snapshots, format_search_results

SNAPSHOTS = {
    "dev": {"DB_HOST": "localhost", "DB_PORT": "5432", "DEBUG": "true"},
    "prod": {"DB_HOST": "prod-db.example.com", "DB_PORT": "5432", "DEBUG": "false"},
    "staging": {"APP_ENV": "staging", "DEBUG": "true"},
}


def _mock_load(name):
    if name not in SNAPSHOTS:
        raise FileNotFoundError(name)
    return SNAPSHOTS[name]


@pytest.fixture(autouse=True)
def _patch(monkeypatch):
    monkeypatch.setattr("envsnap.search.list_snapshots", lambda: list(SNAPSHOTS))
    monkeypatch.setattr("envsnap.search.load_snapshot", _mock_load)


def test_search_by_key_exact():
    res = search_snapshots(key_pattern="DEBUG")
    assert set(res.keys()) == {"dev", "prod", "staging"}


def test_search_by_key_glob():
    res = search_snapshots(key_pattern="DB_*")
    assert set(res.keys()) == {"dev", "prod"}
    assert "DB_HOST" in res["dev"]
    assert "DB_PORT" in res["dev"]


def test_search_by_value_glob():
    res = search_snapshots(value_pattern="*example.com")
    assert list(res.keys()) == ["prod"]
    assert res["prod"]["DB_HOST"] == "prod-db.example.com"


def test_search_by_key_and_value():
    res = search_snapshots(key_pattern="DEBUG", value_pattern="true")
    assert set(res.keys()) == {"dev", "staging"}


def test_search_no_match():
    res = search_snapshots(key_pattern="NONEXISTENT")
    assert res == {}


def test_search_specific_snapshots():
    res = search_snapshots(key_pattern="DB_*", snapshot_names=["dev"])
    assert list(res.keys()) == ["dev"]


def test_format_text():
    res = search_snapshots(key_pattern="APP_ENV")
    out = format_search_results(res, fmt="text")
    assert "[staging]" in out
    assert "APP_ENV=staging" in out


def test_format_json():
    import json
    res = search_snapshots(key_pattern="APP_ENV")
    out = format_search_results(res, fmt="json")
    parsed = json.loads(out)
    assert parsed["staging"]["APP_ENV"] == "staging"


def test_format_empty():
    out = format_search_results({}, fmt="text")
    assert out == "No matches found."
