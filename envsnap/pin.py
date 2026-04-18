"""Pin a snapshot as the 'default' or a named alias for quick restore."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

from envsnap.storage import get_snapshot_dir, load_snapshot


def _pins_path() -> Path:
    return get_snapshot_dir() / "pins.json"


def _load_pins() -> Dict[str, str]:
    p = _pins_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_pins(pins: Dict[str, str]) -> None:
    _pins_path().write_text(json.dumps(pins, indent=2))


def set_pin(alias: str, snapshot_name: str) -> None:
    """Pin *snapshot_name* under *alias*. Raises KeyError if snapshot missing."""
    load_snapshot(snapshot_name)  # validate existence
    pins = _load_pins()
    pins[alias] = snapshot_name
    _save_pins(pins)


def remove_pin(alias: str) -> None:
    """Remove a pin by alias. Raises KeyError if alias not found."""
    pins = _load_pins()
    if alias not in pins:
        raise KeyError(f"Pin '{alias}' not found.")
    del pins[alias]
    _save_pins(pins)


def get_pin(alias: str) -> Optional[str]:
    """Return the snapshot name for *alias*, or None."""
    return _load_pins().get(alias)


def list_pins() -> Dict[str, str]:
    """Return all alias -> snapshot_name mappings."""
    return _load_pins()


def resolve_pin(alias: str) -> dict:
    """Resolve alias to snapshot data. Raises KeyError if missing."""
    name = get_pin(alias)
    if name is None:
        raise KeyError(f"Pin '{alias}' not found.")
    return load_snapshot(name)
