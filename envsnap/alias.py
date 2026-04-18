"""Alias support: map friendly names to snapshot names."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

from envsnap.storage import get_snapshot_dir, snapshot_path


def _aliases_path() -> Path:
    return get_snapshot_dir() / "aliases.json"


def _load_aliases() -> Dict[str, str]:
    p = _aliases_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_aliases(data: Dict[str, str]) -> None:
    _aliases_path().write_text(json.dumps(data, indent=2))


def set_alias(alias: str, snapshot_name: str) -> None:
    """Create or update an alias pointing to snapshot_name."""
    if not snapshot_path(snapshot_name).exists():
        raise FileNotFoundError(f"Snapshot '{snapshot_name}' does not exist.")
    data = _load_aliases()
    data[alias] = snapshot_name
    _save_aliases(data)


def remove_alias(alias: str) -> None:
    """Remove an alias. Raises KeyError if not found."""
    data = _load_aliases()
    if alias not in data:
        raise KeyError(f"Alias '{alias}' not found.")
    del data[alias]
    _save_aliases(data)


def resolve_alias(alias: str) -> Optional[str]:
    """Return the snapshot name for alias, or None."""
    return _load_aliases().get(alias)


def list_aliases() -> Dict[str, str]:
    """Return all alias -> snapshot_name mappings."""
    return _load_aliases()
