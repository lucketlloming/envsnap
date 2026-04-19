"""Tests for envsnap.patch."""
import pytest
from unittest.mock import patch as mock_patch

from envsnap.patch import patch_snapshot, set_key, unset_key, SnapshotNotFoundError


_SNAP = "mysnap"
_BASE = {"FOO": "bar", "BAZ": "qux"}


def _patch(snapshots=None, data=None):
    """Return a context-manager that stubs storage calls."""
    if snapshots is None:
        snapshots = [_SNAP]
    if data is None:
        data = dict(_BASE)

    saved = {}

    def fake_load(name):
        return dict(data)

    def fake_save(name, d):
        saved["result"] = dict(d)
        saved["name"] = name

    return mock_patch.multiple(
        "envsnap.patch",
        list_snapshots=lambda: snapshots,
        load_snapshot=fake_load,
        save_snapshot=fake_save,
    ), saved


def test_patch_updates_keys():
    ctx, saved = _patch()
    with ctx:
        result = patch_snapshot(_SNAP, {"FOO": "NEW", "EXTRA": "yes"})
    assert result["FOO"] == "NEW"
    assert result["EXTRA"] == "yes"
    assert result["BAZ"] == "qux"
    assert saved["result"] == result


def test_patch_deletes_keys():
    ctx, saved = _patch()
    with ctx:
        result = patch_snapshot(_SNAP, {}, delete_keys=["FOO"])
    assert "FOO" not in result
    assert result["BAZ"] == "qux"


def test_patch_update_and_delete():
    ctx, saved = _patch()
    with ctx:
        result = patch_snapshot(_SNAP, {"BAZ": "updated"}, delete_keys=["FOO"])
    assert "FOO" not in result
    assert result["BAZ"] == "updated"


def test_patch_missing_snapshot_raises():
    ctx, _ = _patch(snapshots=[])
    with ctx:
        with pytest.raises(SnapshotNotFoundError):
            patch_snapshot(_SNAP, {"X": "1"})


def test_set_key():
    ctx, saved = _patch()
    with ctx:
        result = set_key(_SNAP, "FOO", "changed")
    assert result["FOO"] == "changed"


def test_unset_key():
    ctx, saved = _patch()
    with ctx:
        result = unset_key(_SNAP, "BAZ")
    assert "BAZ" not in result
    assert result["FOO"] == "bar"


def test_unset_missing_key_is_noop():
    ctx, saved = _patch()
    with ctx:
        result = unset_key(_SNAP, "DOES_NOT_EXIST")
    assert result == _BASE
