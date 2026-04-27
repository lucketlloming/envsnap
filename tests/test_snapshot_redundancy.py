"""Tests for envsnap.snapshot_redundancy."""
import pytest
from unittest.mock import patch

from envsnap.snapshot_redundancy import (
    RedundancyResult,
    _jaccard,
    find_redundant,
    format_redundancy,
)


# ---------------------------------------------------------------------------
# Unit helpers
# ---------------------------------------------------------------------------

def _patch(names, snapshots):
    """Return a context manager that patches list_snapshots and load_snapshot."""
    return (
        patch("envsnap.snapshot_redundancy.list_snapshots", return_value=names),
        patch(
            "envsnap.snapshot_redundancy.load_snapshot",
            side_effect=lambda n: snapshots[n],
        ),
    )


# ---------------------------------------------------------------------------
# _jaccard
# ---------------------------------------------------------------------------

def test_jaccard_identical():
    d = {"A": "1", "B": "2"}
    assert _jaccard(d, d) == 1.0


def test_jaccard_disjoint():
    assert _jaccard({"A": "1"}, {"B": "2"}) == 0.0


def test_jaccard_partial():
    a = {"A": "1", "B": "2"}
    b = {"A": "1", "C": "3"}
    # intersection = {A=1}, union = {A=1, B=2, C=3}
    assert _jaccard(a, b) == pytest.approx(1 / 3)


def test_jaccard_both_empty():
    assert _jaccard({}, {}) == 1.0


# ---------------------------------------------------------------------------
# find_redundant
# ---------------------------------------------------------------------------

def test_find_redundant_exact_duplicate():
    snaps = {
        "snap_a": {"K": "V"},
        "snap_b": {"K": "V"},
    }
    p1, p2 = _patch(["snap_a", "snap_b"], snaps)
    with p1, p2:
        results = find_redundant(threshold=0.95)
    assert len(results) == 2
    names = {r.snapshot for r in results}
    assert names == {"snap_a", "snap_b"}
    for r in results:
        assert r.is_exact
        assert r.similarity == 1.0


def test_find_redundant_below_threshold():
    snaps = {
        "snap_a": {"A": "1", "B": "2"},
        "snap_b": {"A": "1", "C": "3"},
    }
    p1, p2 = _patch(["snap_a", "snap_b"], snaps)
    with p1, p2:
        results = find_redundant(threshold=0.95)
    assert results == []


def test_find_redundant_filtered_by_name():
    snaps = {
        "snap_a": {"K": "V"},
        "snap_b": {"K": "V"},
        "snap_c": {"X": "Y"},
    }
    p1, p2 = _patch(["snap_a", "snap_b", "snap_c"], snaps)
    with p1, p2:
        results = find_redundant(threshold=0.95, snapshot_name="snap_b")
    assert len(results) == 1
    assert results[0].snapshot == "snap_b"


def test_find_redundant_empty_list():
    p1, p2 = _patch([], {})
    with p1, p2:
        results = find_redundant()
    assert results == []


# ---------------------------------------------------------------------------
# format_redundancy
# ---------------------------------------------------------------------------

def test_format_redundancy_empty():
    assert format_redundancy([]) == "No redundant snapshots found."


def test_format_redundancy_shows_entries():
    r = RedundancyResult(snapshot="snap_b", duplicate_of="snap_a", similarity=1.0, is_exact=True)
    out = format_redundancy([r])
    assert "snap_b" in out
    assert "snap_a" in out
    assert "EXACT" in out
