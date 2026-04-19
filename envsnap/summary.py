"""Snapshot summary: metadata overview for a snapshot."""
from __future__ import annotations
from typing import Any
from envsnap.storage import load_snapshot, list_snapshots
from envsnap.tags import get_tags
from envsnap.notes import get_note
from envsnap.pin import get_pin
import json


def summarize_snapshot(name: str) -> dict[str, Any]:
    """Return a metadata summary dict for a named snapshot."""
    data = load_snapshot(name)
    keys = list(data.keys())
    return {
        "name": name,
        "key_count": len(keys),
        "keys": keys,
        "tags": get_tags(name),
        "note": get_note(name),
        "pinned": get_pin(name) == name,
    }


def summarize_all() -> list[dict[str, Any]]:
    """Return summary dicts for all snapshots."""
    return [summarize_snapshot(n) for n in list_snapshots()]


def format_summary(summary: dict[str, Any]) -> str:
    lines = [
        f"Snapshot : {summary['name']}",
        f"Keys     : {summary['key_count']} ({', '.join(summary['keys']) or 'none'})",
        f"Tags     : {', '.join(summary['tags']) or 'none'}",
        f"Note     : {summary['note'] or 'none'}",
        f"Pinned   : {'yes' if summary['pinned'] else 'no'}",
    ]
    return "\n".join(lines)
