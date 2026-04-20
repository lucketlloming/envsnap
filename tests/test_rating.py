"""Tests for envsnap.rating."""

from __future__ import annotations

import pytest

from envsnap.rating import (
    InvalidRatingError,
    SnapshotNotFoundError,
    get_rating,
    list_ratings,
    remove_rating,
    set_rating,
    top_rated,
)


@pytest.fixture(autouse=True)
def isolated_snapshot_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVSNAP_DIR", str(tmp_path))
    # Pre-create a couple of fake snapshots so existence checks pass
    for name in ("snap-a", "snap-b", "snap-c"):
        (tmp_path / f"{name}.json").write_text('{"FOO": "bar"}')
    return tmp_path


def test_set_and_get_rating():
    set_rating("snap-a", 4)
    assert get_rating("snap-a") == 4


def test_get_rating_unrated_returns_none():
    assert get_rating("snap-a") is None


def test_set_rating_invalid_low():
    with pytest.raises(InvalidRatingError):
        set_rating("snap-a", 0)


def test_set_rating_invalid_high():
    with pytest.raises(InvalidRatingError):
        set_rating("snap-a", 6)


def test_set_rating_missing_snapshot_raises():
    with pytest.raises(SnapshotNotFoundError):
        set_rating("no-such-snap", 3)


def test_remove_rating():
    set_rating("snap-a", 5)
    remove_rating("snap-a")
    assert get_rating("snap-a") is None


def test_remove_rating_noop_if_not_rated():
    # Should not raise
    remove_rating("snap-a")


def test_list_ratings():
    set_rating("snap-a", 3)
    set_rating("snap-b", 5)
    ratings = list_ratings()
    assert ratings == {"snap-a": 3, "snap-b": 5}


def test_top_rated_ordering():
    set_rating("snap-a", 2)
    set_rating("snap-b", 5)
    set_rating("snap-c", 4)
    result = top_rated()
    names = [name for name, _ in result]
    assert names[0] == "snap-b"
    assert names[1] == "snap-c"
    assert names[2] == "snap-a"


def test_top_rated_respects_n():
    set_rating("snap-a", 2)
    set_rating("snap-b", 5)
    set_rating("snap-c", 4)
    result = top_rated(n=2)
    assert len(result) == 2
