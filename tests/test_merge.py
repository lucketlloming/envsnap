import pytest
from unittest.mock import patch, MagicMock
from envsnap.merge import merge_snapshots, conflicts
from envsnap.storage import SnapshotNotFoundError


SNAP_A = {"FOO": "1", "SHARED": "from_a", "ONLY_A": "aaa"}
SNAP_B = {"BAR": "2", "SHARED": "from_b", "ONLY_B": "bbb"}


def _patch(a=SNAP_A, b=SNAP_B):
    def _load(name):
        return {"snap_a": a, "snap_b": b}[name]
    return patch("envsnap.merge.load_snapshot", side_effect=_load)


def test_merge_union_a_wins():
    saved = {}
    with _patch(), patch("envsnap.merge.save_snapshot", side_effect=lambda n, d: saved.update({n: d})):
        result = merge_snapshots("snap_a", "snap_b", "out", strategy="union")
    assert result["SHARED"] == "from_a"
    assert "FOO" in result and "BAR" in result
    assert saved["out"] == result


def test_merge_ours_keeps_a_values():
    with _patch(), patch("envsnap.merge.save_snapshot"):
        result = merge_snapshots("snap_a", "snap_b", "out", strategy="ours")
    assert result["SHARED"] == "from_a"
    assert "ONLY_B" in result
    assert "BAR" in result


def test_merge_theirs_keeps_b_values():
    with _patch(), patch("envsnap.merge.save_snapshot"):
        result = merge_snapshots("snap_a", "snap_b", "out", strategy="theirs")
    assert result["SHARED"] == "from_b"
    assert "ONLY_A" in result


def test_merge_invalid_strategy():
    with _patch(), patch("envsnap.merge.save_snapshot"):
        with pytest.raises(ValueError, match="Unknown strategy"):
            merge_snapshots("snap_a", "snap_b", "out", strategy="bad")


def test_conflicts_returns_differing_keys():
    with _patch():
        result = conflicts("snap_a", "snap_b")
    assert "SHARED" in result
    assert result["SHARED"] == ("from_a", "from_b")
    assert "FOO" not in result
    assert "BAR" not in result


def test_conflicts_no_overlap():
    a = {"X": "1"}
    b = {"Y": "2"}
    with _patch(a, b):
        result = conflicts("snap_a", "snap_b")
    assert result == {}
