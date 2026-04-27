"""Tests for envsnap.snapshot_impact."""
from __future__ import annotations

from unittest.mock import patch

import pytest

from envsnap.snapshot_impact import ImpactResult, _level, assess_impact, assess_all_impact, format_impact


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _patch(snaps, deps_map, groups_map):
    """Return a context-manager stack that patches storage, dependency, group."""
    import contextlib

    @contextlib.contextmanager
    def _ctx():
        with (
            patch("envsnap.snapshot_impact.storage.list_snapshots", return_value=snaps),
            patch(
                "envsnap.snapshot_impact.dependency.get_dependencies",
                side_effect=lambda n: deps_map.get(n, []),
            ),
            patch(
                "envsnap.snapshot_impact.group_mod.list_groups",
                return_value=groups_map,
            ),
        ):
            yield

    return _ctx()


# ---------------------------------------------------------------------------
# _level
# ---------------------------------------------------------------------------

def test_level_high():
    assert _level(0.8) == "high"


def test_level_medium():
    assert _level(0.5) == "medium"


def test_level_low():
    assert _level(0.1) == "low"


# ---------------------------------------------------------------------------
# assess_impact
# ---------------------------------------------------------------------------

def test_assess_impact_missing_snapshot_raises():
    with _patch([], {}, {}):
        with pytest.raises(KeyError, match="not found"):
            assess_impact("ghost")


def test_assess_impact_no_relationships():
    with _patch(["snap-a"], {}, {}):
        result = assess_impact("snap-a")
    assert result.name == "snap-a"
    assert result.dependency_count == 0
    assert result.dependent_count == 0
    assert result.group_count == 0
    assert result.score == 0.0
    assert result.level == "low"


def test_assess_impact_with_dependents():
    snaps = ["snap-a", "snap-b", "snap-c"]
    # snap-b and snap-c depend on snap-a
    deps_map = {"snap-a": [], "snap-b": ["snap-a"], "snap-c": ["snap-a"]}
    with _patch(snaps, deps_map, {}):
        result = assess_impact("snap-a")
    assert result.dependent_count == 2
    assert set(result.dependents) == {"snap-b", "snap-c"}
    assert result.score > 0


def test_assess_impact_with_groups():
    snaps = ["snap-a"]
    groups = {"g1": ["snap-a"], "g2": ["snap-a"], "g3": ["snap-b"]}
    with _patch(snaps, {}, groups):
        result = assess_impact("snap-a")
    assert result.group_count == 2
    assert set(result.groups) == {"g1", "g2"}


def test_assess_impact_score_capped_at_one():
    snaps = ["snap-a"] + [f"dep-{i}" for i in range(20)]
    deps_map = {f"dep-{i}": ["snap-a"] for i in range(20)}
    groups = {f"g{i}": ["snap-a"] for i in range(10)}
    with _patch(snaps, deps_map, groups):
        result = assess_impact("snap-a")
    assert result.score <= 1.0


def test_assess_all_impact_returns_list():
    snaps = ["a", "b"]
    with _patch(snaps, {}, {}):
        results = assess_all_impact()
    assert len(results) == 2
    assert all(isinstance(r, ImpactResult) for r in results)


def test_format_impact_contains_name():
    r = ImpactResult(
        name="my-snap", dependency_count=1, dependent_count=2,
        group_count=1, score=0.5, level="medium",
        groups=["g1"], dependencies=["dep"], dependents=["x", "y"],
    )
    text = format_impact(r)
    assert "my-snap" in text
    assert "medium" in text
    assert "g1" in text
