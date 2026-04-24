"""Snapshot index: build and query a searchable index of all snapshot metadata."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from envsnap.storage import get_snapshot_dir, list_snapshots, load_snapshot
from envsnap.tags import get_tags
from envsnap.pin import get_pin
from envsnap.notes import get_note


def _index_path() -> Path:
    return get_snapshot_dir() / "_index.json"


def build_index() -> dict[str, dict[str, Any]]:
    """Build a fresh index from all snapshots on disk."""
    index: dict[str, dict[str, Any]] = {}
    for name in list_snapshots():
        try:
            data = load_snapshot(name)
        except Exception:
            continue
        index[name] = {
            "keys": sorted(data.keys()),
            "key_count": len(data),
            "tags": get_tags(name),
            "pinned": get_pin(name) is not None,
            "note": get_note(name),
        }
    return index


def save_index(index: dict[str, dict[str, Any]]) -> None:
    """Persist the index to disk."""
    path = _index_path()
    path.write_text(json.dumps(index, indent=2))


def load_index() -> dict[str, dict[str, Any]]:
    """Load the index from disk, or build it if missing."""
    path = _index_path()
    if not path.exists():
        index = build_index()
        save_index(index)
        return index
    return json.loads(path.read_text())


def refresh_index() -> dict[str, dict[str, Any]]:
    """Rebuild and save the index, then return it."""
    index = build_index()
    save_index(index)
    return index


def query_index(
    index: dict[str, dict[str, Any]],
    *,
    tag: str | None = None,
    pinned: bool | None = None,
    min_keys: int | None = None,
    max_keys: int | None = None,
    has_note: bool | None = None,
) -> list[str]:
    """Return snapshot names matching all supplied criteria."""
    results = []
    for name, meta in index.items():
        if tag is not None and tag not in meta.get("tags", []):
            continue
        if pinned is not None and meta.get("pinned") != pinned:
            continue
        kc = meta.get("key_count", 0)
        if min_keys is not None and kc < min_keys:
            continue
        if max_keys is not None and kc > max_keys:
            continue
        if has_note is not None:
            note_present = bool(meta.get("note"))
            if has_note != note_present:
                continue
        results.append(name)
    return sorted(results)
