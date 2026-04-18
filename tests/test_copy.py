import pytest
from unittest.mock import patch, MagicMock

from envsnap.copy import copy_keys, SnapshotNotFoundError


SNAPSHOTS = {
    "base": {"FOO": "1", "BAR": "2", "BAZ": "3"},
    "target": {"FOO": "old", "EXTRA": "yes"},
}


def _patch(monkeypatch, snapshots=None):
    data = {k: dict(v) for k, v in (snapshots or SNAPSHOTS).items()}
    saved = {}

    def _list():
        return list(data.keys())

    def _load(name):
        return dict(data[name])

    def _save(name, d):
        data[name] = dict(d)
        saved[name] = dict(d)

    monkeypatch.setattr("envsnap.copy.list_snapshots", _list)
    monkeypatch.setattr("envsnap.copy.load_snapshot", _load)
    monkeypatch.setattr("envsnap.copy.save_snapshot", _save)
    return data, saved


def test_copy_keys_into_existing_no_overwrite(monkeypatch):
    data, saved = _patch(monkeypatch)
    result = copy_keys("base", "target", ["BAR", "BAZ"], overwrite=False)
    # FOO already existed in target → kept
    assert result["FOO"] == "old"
    assert result["BAR"] == "2"
    assert result["BAZ"] == "3"
    assert result["EXTRA"] == "yes"


def test_copy_keys_with_overwrite(monkeypatch):
    data, saved = _patch(monkeypatch)
    result = copy_keys("base", "target", ["FOO"], overwrite=True)
    assert result["FOO"] == "1"


def test_copy_keys_creates_new_snapshot(monkeypatch):
    data, saved = _patch(monkeypatch, snapshots={"base": {"X": "10"}})
    result = copy_keys("base", "fresh", ["X"])
    assert result == {"X": "10"}
    assert saved["fresh"] == {"X": "10"}


def test_copy_missing_source_raises(monkeypatch):
    data, saved = _patch(monkeypatch)
    with pytest.raises(SnapshotNotFoundError):
        copy_keys("ghost", "target", ["FOO"])


def test_copy_missing_keys_raises(monkeypatch):
    data, saved = _patch(monkeypatch)
    with pytest.raises(KeyError):
        copy_keys("base", "target", ["NOPE"])
