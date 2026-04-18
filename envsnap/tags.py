"""Tag management for snapshots."""

import json
from pathlib import Path
from envsnap.storage import get_snapshot_dir

TAGS_FILE = "tags.json"


def _tags_path() -> Path:
    return get_snapshot_dir() / TAGS_FILE


def _load_tags() -> dict:
    path = _tags_path()
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_tags(tags: dict) -> None:
    path = _tags_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(tags, f, indent=2)


def add_tag(snapshot_name: str, tag: str) -> None:
    """Add a tag to a snapshot."""
    tags = _load_tags()
    tags.setdefault(snapshot_name, []).append(tag)
    tags[snapshot_name] = list(dict.fromkeys(tags[snapshot_name]))  # dedupe
    _save_tags(tags)


def remove_tag(snapshot_name: str, tag: str) -> None:
    """Remove a tag from a snapshot."""
    tags = _load_tags()
    if snapshot_name in tags:
        tags[snapshot_name] = [t for t in tags[snapshot_name] if t != tag]
        if not tags[snapshot_name]:
            del tags[snapshot_name]
        _save_tags(tags)


def get_tags(snapshot_name: str) -> list:
    """Return tags for a snapshot."""
    return _load_tags().get(snapshot_name, [])


def find_by_tag(tag: str) -> list:
    """Return snapshot names that have the given tag."""
    tags = _load_tags()
    return [name for name, t_list in tags.items() if tag in t_list]


def list_all_tags() -> dict:
    """Return all snapshot -> tags mappings."""
    return _load_tags()
