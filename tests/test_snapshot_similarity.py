"""Tests for envsnap.snapshot_similarity."""
from unittest.mock import patch

import pytest

from envsnap.snapshot_similarity import (
    SimilarityResult,
    compute_similarity,
    find_similar,
    format_similarity,
    _jaccard,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _patch(snapshots: dict, names=None):
    """Return a context manager that mocks load_snapshot and list_snapshots."""
    import contextlib

    @contextlib.contextmanager
    def _ctx():
        def _load(name):
            if name not in snapshots:
                raise FileNotFoundError(name)
            return snapshots[name]

        with patch("envsnap.snapshot_similarity.load_snapshot", side_effect=_load), \
             patch("envsnap.snapshot_similarity.list_snapshots", return_value=names or list(snapshots)):
            yield

    return _ctx()


# ---------------------------------------------------------------------------
# _jaccard
# ---------------------------------------------------------------------------

def test_jaccard_identical():
    assert _jaccard({"a", "b"}, {"a", "b"}) == 1.0


def test_jaccard_disjoint():
    assert _jaccard({"a"}, {"b"}) == 0.0


def test_jaccard_partial():
    score = _jaccard({"a", "b"}, {"b", "c"})
    assert abs(score - 1 / 3) < 1e-9


def test_jaccard_both_empty():
    assert _jaccard(set(), set()) == 1.0


# ---------------------------------------------------------------------------
# compute_similarity
# ---------------------------------------------------------------------------

def test_compute_similarity_identical_snapshots():
    snaps = {
        "s1": {"A": "1", "B": "2"},
        "s2": {"A": "1", "B": "2"},
    }
    with _patch(snaps):
        result = compute_similarity("s1", "s2")

    assert result.overall_score == 1.0
    assert result.key_similarity == 1.0
    assert result.value_similarity == 1.0
    assert result.shared_keys == ["A", "B"]


def test_compute_similarity_no_overlap():
    snaps = {
        "s1": {"X": "1"},
        "s2": {"Y": "2"},
    }
    with _patch(snaps):
        result = compute_similarity("s1", "s2")

    assert result.overall_score == 0.0
    assert result.shared_keys == []
    assert result.shared_key_value_pairs == []


def test_compute_similarity_partial_overlap():
    snaps = {
        "s1": {"A": "1", "B": "2"},
        "s2": {"A": "1", "C": "3"},
    }
    with _patch(snaps):
        result = compute_similarity("s1", "s2")

    assert result.shared_keys == ["A"]
    assert "A=1" in result.shared_key_value_pairs
    assert 0 < result.overall_score < 1


def test_compute_similarity_same_keys_different_values():
    snaps = {
        "s1": {"A": "1"},
        "s2": {"A": "99"},
    }
    with _patch(snaps):
        result = compute_similarity("s1", "s2")

    assert result.key_similarity == 1.0
    assert result.value_similarity == 0.0
    assert result.shared_key_value_pairs == []


# ---------------------------------------------------------------------------
# find_similar
# ---------------------------------------------------------------------------

def test_find_similar_returns_above_threshold():
    snaps = {
        "base": {"A": "1", "B": "2"},
        "close": {"A": "1", "B": "2", "C": "3"},
        "far": {"X": "9"},
    }
    with _patch(snaps):
        results = find_similar("base", threshold=0.4)

    names = [r.snapshot_b for r in results]
    assert "close" in names
    assert "far" not in names


def test_find_similar_top_n():
    snaps = {f"s{i}": {"K": str(i)} for i in range(5)}
    snaps["base"] = {"K": "0"}
    with _patch(snaps):
        results = find_similar("base", threshold=0.0, top_n=2)

    assert len(results) <= 2


def test_find_similar_excludes_self():
    snaps = {"base": {"A": "1"}, "other": {"A": "1"}}
    with _patch(snaps):
        results = find_similar("base", threshold=0.0)

    assert all(r.snapshot_b != "base" for r in results)


# ---------------------------------------------------------------------------
# format_similarity
# ---------------------------------------------------------------------------

def test_format_similarity_contains_score():
    result = SimilarityResult(
        snapshot_a="a",
        snapshot_b="b",
        shared_keys=["X"],
        shared_key_value_pairs=["X=1"],
        key_similarity=0.5,
        value_similarity=0.5,
        overall_score=0.5,
    )
    text = format_similarity(result)
    assert "50.00%" in text
    assert "a <-> b" in text
    assert "X" in text
