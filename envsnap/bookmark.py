"""Bookmark support: mark snapshots as favourites for quick access."""
from __future__ import annotations

import json
from pathlib import Path
from typing import List

from envsnap.storage import get_snapshot_dir, list_snapshots


def _bookmarks_path() -> Path:
    return get_snapshot_dir() / "bookmarks.json"


def _load_bookmarks() -> List[str]:
    p = _bookmarks_path()
    if not p.exists():
        return []
    return json.loads(p.read_text())


def _save_bookmarks(bookmarks: List[str]) -> None:
    _bookmarks_path().write_text(json.dumps(bookmarks, indent=2))


def add_bookmark(name: str) -> None:
    """Bookmark a snapshot by name."""
    if name not in list_snapshots():
        raise KeyError(f"Snapshot '{name}' does not exist.")
    bookmarks = _load_bookmarks()
    if name not in bookmarks:
        bookmarks.append(name)
        _save_bookmarks(bookmarks)


def remove_bookmark(name: str) -> None:
    """Remove a bookmark."""
    bookmarks = _load_bookmarks()
    if name not in bookmarks:
        raise KeyError(f"Bookmark '{name}' not found.")
    bookmarks.remove(name)
    _save_bookmarks(bookmarks)


def list_bookmarks() -> List[str]:
    """Return all bookmarked snapshot names."""
    existing = set(list_snapshots())
    return [b for b in _load_bookmarks() if b in existing]


def is_bookmarked(name: str) -> bool:
    return name in _load_bookmarks()
