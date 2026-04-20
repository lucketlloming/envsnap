"""Manage favorite (starred) snapshots."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from envsnap.storage import get_snapshot_dir, list_snapshots


def _favorites_path() -> Path:
    return get_snapshot_dir() / "favorites.json"


def _load_favorites() -> List[str]:
    p = _favorites_path()
    if not p.exists():
        return []
    return json.loads(p.read_text())


def _save_favorites(favorites: List[str]) -> None:
    _favorites_path().write_text(json.dumps(favorites, indent=2))


def add_favorite(name: str) -> None:
    """Mark a snapshot as a favorite."""
    existing = list_snapshots()
    if name not in existing:
        raise ValueError(f"Snapshot '{name}' does not exist.")
    favs = _load_favorites()
    if name not in favs:
        favs.append(name)
        _save_favorites(favs)


def remove_favorite(name: str) -> None:
    """Unmark a snapshot as a favorite."""
    favs = _load_favorites()
    if name not in favs:
        raise ValueError(f"Snapshot '{name}' is not a favorite.")
    favs.remove(name)
    _save_favorites(favs)


def list_favorites() -> List[str]:
    """Return all favorited snapshot names."""
    return _load_favorites()


def is_favorite(name: str) -> bool:
    """Return True if snapshot is favorited."""
    return name in _load_favorites()
