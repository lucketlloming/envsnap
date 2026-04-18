"""Core logic for capturing and restoring environment variable snapshots."""

import os
from envsnap.storage import save_snapshot, load_snapshot, delete_snapshot, list_snapshots


def capture(name: str, keys: list[str] | None = None) -> dict:
    """
    Capture current environment variables into a snapshot.

    Args:
        name: Snapshot name.
        keys: Optional list of specific keys to capture. Captures all if None.

    Returns:
        The saved variables dict.
    """
    if keys:
        variables = {k: os.environ[k] for k in keys if k in os.environ}
    else:
        variables = dict(os.environ)

    save_snapshot(name, variables)
    return variables


def restore(name: str, overwrite: bool = True) -> dict:
    """
    Load a snapshot and return its variables.
    Optionally applies them to the current process environment.

    Args:
        name: Snapshot name.
        overwrite: If True, set variables in os.environ.

    Returns:
        The restored variables dict.
    """
    data = load_snapshot(name)
    variables = data["variables"]
    if overwrite:
        for key, value in variables.items():
            os.environ[key] = value
    return variables


def diff(name: str) -> dict:
    """
    Compare a snapshot against the current environment.

    Returns:
        Dict with keys 'added', 'removed', 'changed'.
    """
    data = load_snapshot(name)
    saved = data["variables"]
    current = dict(os.environ)

    added = {k: current[k] for k in current if k not in saved}
    removed = {k: saved[k] for k in saved if k not in current}
    changed = {
        k: {"old": saved[k], "new": current[k]}
        for k in saved
        if k in current and saved[k] != current[k]
    }
    return {"added": added, "removed": removed, "changed": changed}
