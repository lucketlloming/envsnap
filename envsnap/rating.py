"""Snapshot rating module — allows users to rate snapshots (1–5 stars)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from envsnap.storage import get_snapshot_dir, list_snapshots


class InvalidRatingError(Exception):
    """Raised when a rating value is out of the 1–5 range."""


class SnapshotNotFoundError(Exception):
    """Raised when the target snapshot does not exist."""


def _ratings_path() -> Path:
    return get_snapshot_dir() / "ratings.json"


def _load_ratings() -> dict[str, int]:
    p = _ratings_path()
    if not p.exists():
        return {}
    with p.open() as f:
        return json.load(f)


def _save_ratings(data: dict[str, int]) -> None:
    p = _ratings_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w") as f:
        json.dump(data, f, indent=2)


def set_rating(name: str, stars: int) -> None:
    """Set a star rating (1–5) for *name*."""
    if name not in list_snapshots():
        raise SnapshotNotFoundError(f"Snapshot '{name}' does not exist.")
    if stars < 1 or stars > 5:
        raise InvalidRatingError(f"Rating must be between 1 and 5, got {stars}.")
    ratings = _load_ratings()
    ratings[name] = stars
    _save_ratings(ratings)


def get_rating(name: str) -> Optional[int]:
    """Return the rating for *name*, or None if not rated."""
    return _load_ratings().get(name)


def remove_rating(name: str) -> None:
    """Remove the rating for *name*. No-op if not rated."""
    ratings = _load_ratings()
    ratings.pop(name, None)
    _save_ratings(ratings)


def list_ratings() -> dict[str, int]:
    """Return all snapshot ratings as {name: stars}."""
    return dict(_load_ratings())


def top_rated(n: int = 5) -> list[tuple[str, int]]:
    """Return up to *n* snapshots sorted by rating descending."""
    ratings = _load_ratings()
    return sorted(ratings.items(), key=lambda kv: kv[1], reverse=True)[:n]
