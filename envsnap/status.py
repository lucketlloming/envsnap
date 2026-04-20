"""Snapshot status module: compute and format a rich status report for a snapshot."""
from __future__ import annotations

from typing import Any

from envsnap import storage
from envsnap.pin import get_pin
from envsnap.lock import is_locked
from envsnap.favorite import is_favorite
from envsnap.expire import get_expiry
from envsnap.rating import get_rating
from envsnap.notes import get_note
from envsnap.tags import get_tags


def snapshot_status(name: str) -> dict[str, Any]:
    """Return a dict with rich status information about a snapshot."""
    data = storage.load_snapshot(name)  # raises FileNotFoundError if missing

    pinned = False
    try:
        pinned = get_pin(name) is not None
    except Exception:
        pass

    locked = False
    try:
        locked = is_locked(name)
    except Exception:
        pass

    fav = False
    try:
        fav = is_favorite(name)
    except Exception:
        pass

    expiry = None
    try:
        expiry = get_expiry(name)
    except Exception:
        pass

    rating = None
    try:
        rating = get_rating(name)
    except Exception:
        pass

    note = None
    try:
        note = get_note(name)
    except Exception:
        pass

    tags: list[str] = []
    try:
        tags = get_tags(name)
    except Exception:
        pass

    return {
        "name": name,
        "key_count": len(data),
        "pinned": pinned,
        "locked": locked,
        "favorite": fav,
        "expiry": expiry,
        "rating": rating,
        "note": note,
        "tags": tags,
    }


def format_status(status: dict[str, Any], fmt: str = "text") -> str:
    """Format a status dict as text or json."""
    if fmt == "json":
        import json
        return json.dumps(status, indent=2, default=str)

    lines = [
        f"Snapshot : {status['name']}",
        f"Keys     : {status['key_count']}",
        f"Pinned   : {'yes' if status['pinned'] else 'no'}",
        f"Locked   : {'yes' if status['locked'] else 'no'}",
        f"Favorite : {'yes' if status['favorite'] else 'no'}",
        f"Expiry   : {status['expiry'] or 'none'}",
        f"Rating   : {status['rating'] if status['rating'] is not None else 'unrated'}",
        f"Tags     : {', '.join(status['tags']) if status['tags'] else 'none'}",
        f"Note     : {status['note'] or 'none'}",
    ]
    return "\n".join(lines)
