"""Tests for envsnap.snapshot_entropy."""
import pytest
from unittest.mock import patch

from envsnap.snapshot_entropy import (
    _shannon_entropy,
    _level,
    compute_entropy,
    compute_all_entropy,
    format_entropy,
    EntropyResult,
)


def _patch(snapshots=None, load_map=None):
    """Helper to patch storage calls."""
    snapshots = snapshots or []
    load_map = load_map or {}

    def _load(name):
        if name not in load_map:
            raise FileNotFoundError(name)
        return load_map[name]

    return (
        patch("envsnap.snapshot_entropy.list_snapshots", return_value=snapshots),
        patch("envsnap.snapshot_entropy.load_snapshot", side_effect=_load),
    )


def test_shannon_entropy_uniform():
    values = ["a", "b", "c", "d"]
    e = _shannon_entropy(values)
    assert abs(e - 2.0) < 1e-9


def test_shannon_entropy_single_value():
    values = ["x", "x", "x"]
    assert _shannon_entropy(values) == 0.0


def test_shannon_entropy_empty():
    assert _shannon_entropy([]) == 0.0


def test_level_high():
    assert _level(3.5) == "high"


def test_level_medium():
    assert _level(1.5) == "medium"


def test_level_low():
    assert _level(0.5) == "low"


def test_compute_entropy_basic():
    data = {"A": "foo", "B": "bar", "C": "baz", "D": "qux"}
    p1, p2 = _patch(snapshots=["snap1"], load_map={"snap1": data})
    with p1, p2:
        result = compute_entropy("snap1")
    assert result.name == "snap1"
    assert result.key_count == 4
    assert result.unique_values == 4
    assert result.value_entropy > 0
    assert result.level in ("high", "medium", "low")


def test_compute_entropy_empty_snapshot():
    p1, p2 = _patch(snapshots=["empty"], load_map={"empty": {}})
    with p1, p2:
        result = compute_entropy("empty")
    assert result.key_count == 0
    assert result.value_entropy == 0.0
    assert result.avg_value_length == 0.0
    assert result.level == "low"


def test_compute_all_entropy_returns_list():
    load_map = {"s1": {"X": "1", "Y": "2"}, "s2": {"A": "hello"}}
    p1, p2 = _patch(snapshots=["s1", "s2"], load_map=load_map)
    with p1, p2:
        results = compute_all_entropy()
    assert len(results) == 2
    names = {r.name for r in results}
    assert names == {"s1", "s2"}


def test_format_entropy_contains_fields():
    result = EntropyResult(
        name="mysnap",
        key_count=5,
        unique_values=4,
        value_entropy=2.321,
        avg_value_length=6.4,
        level="high",
    )
    text = format_entropy(result)
    assert "mysnap" in text
    assert "2.3210" in text
    assert "high" in text
    assert "6.40" in text
