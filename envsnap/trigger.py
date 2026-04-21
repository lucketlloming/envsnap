"""Trigger module for envsnap.

Allows users to define named triggers that automatically snap the environment
when a specified file path changes (mtime) or a shell command exits with code 0.
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any

from envsnap.storage import get_snapshot_dir, list_snapshots

# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------


class TriggerNotFoundError(KeyError):
    """Raised when a requested trigger name does not exist."""


class SnapshotNotFoundError(KeyError):
    """Raised when the target snapshot does not exist."""


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _triggers_path() -> Path:
    """Return the path to the triggers JSON file."""
    return get_snapshot_dir() / "triggers.json"


def _load_triggers() -> dict[str, Any]:
    """Load triggers from disk, returning an empty dict if none exist."""
    path = _triggers_path()
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _save_triggers(data: dict[str, Any]) -> None:
    """Persist triggers to disk."""
    path = _triggers_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def set_trigger(
    name: str,
    snapshot: str,
    *,
    watch_file: str | None = None,
    command: str | None = None,
) -> None:
    """Create or update a trigger.

    Parameters
    ----------
    name:
        Unique identifier for this trigger.
    snapshot:
        The snapshot name to associate with this trigger.
    watch_file:
        Absolute or relative path to a file whose mtime is monitored.
    command:
        Shell command whose exit-code 0 fires the trigger.

    At least one of *watch_file* or *command* must be provided.
    """
    if not watch_file and not command:
        raise ValueError("A trigger requires at least a watch_file or a command.")

    if snapshot not in list_snapshots():
        raise SnapshotNotFoundError(f"Snapshot '{snapshot}' does not exist.")

    triggers = _load_triggers()
    triggers[name] = {
        "snapshot": snapshot,
        "watch_file": watch_file,
        "command": command,
        "last_mtime": None,
    }
    _save_triggers(triggers)


def remove_trigger(name: str) -> None:
    """Delete a trigger by name."""
    triggers = _load_triggers()
    if name not in triggers:
        raise TriggerNotFoundError(f"Trigger '{name}' not found.")
    del triggers[name]
    _save_triggers(triggers)


def get_trigger(name: str) -> dict[str, Any]:
    """Return the definition of a single trigger."""
    triggers = _load_triggers()
    if name not in triggers:
        raise TriggerNotFoundError(f"Trigger '{name}' not found.")
    return dict(triggers[name])


def list_triggers() -> list[str]:
    """Return a sorted list of all trigger names."""
    return sorted(_load_triggers().keys())


def evaluate_trigger(name: str) -> bool:
    """Check whether a trigger's condition is currently satisfied.

    For *watch_file* triggers the condition is satisfied when the file's
    modification time has changed since the last evaluation.  For *command*
    triggers it is satisfied when the command exits with code 0.

    Returns ``True`` if the trigger fired (condition met), ``False`` otherwise.
    The internal ``last_mtime`` is updated when a file-based trigger fires.
    """
    triggers = _load_triggers()
    if name not in triggers:
        raise TriggerNotFoundError(f"Trigger '{name}' not found.")

    entry = triggers[name]
    fired = False

    if entry.get("watch_file"):
        path = Path(entry["watch_file"])
        if path.exists():
            current_mtime = path.stat().st_mtime
            last_mtime = entry.get("last_mtime")
            if last_mtime is None or current_mtime != last_mtime:
                entry["last_mtime"] = current_mtime
                fired = True

    if not fired and entry.get("command"):
        result = subprocess.run(
            entry["command"],
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        fired = result.returncode == 0

    if fired:
        triggers[name] = entry
        _save_triggers(triggers)

    return fired
