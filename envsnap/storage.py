"""Handles reading and writing environment snapshots to disk."""

import json
import os
from pathlib import Path
from datetime import datetime

DEFAULT_SNAPSHOT_DIR = Path.home() / ".envsnap" / "snapshots"


def get_snapshot_dir() -> Path:
    """Return the snapshot directory, creating it if needed."""
    snapshot_dir = Path(os.environ.get("ENVSNAP_DIR", DEFAULT_SNAPSHOT_DIR))
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    return snapshot_dir


def snapshot_path(name: str) -> Path:
    """Return the file path for a named snapshot."""
    return get_snapshot_dir() / f"{name}.json"


def save_snapshot(name: str, variables: dict) -> Path:
    """Save environment variables to a named snapshot file."""
    path = snapshot_path(name)
    payload = {
        "name": name,
        "created_at": datetime.utcnow().isoformat(),
        "variables": variables,
    }
    with open(path, "w") as f:
        json.dump(payload, f, indent=2)
    return path


def load_snapshot(name: str) -> dict:
    """Load a named snapshot. Raises FileNotFoundError if missing."""
    path = snapshot_path(name)
    if not path.exists():
        raise FileNotFoundError(f"Snapshot '{name}' not found at {path}")
    with open(path) as f:
        return json.load(f)


def list_snapshots() -> list[str]:
    """Return a list of all saved snapshot names."""
    return [p.stem for p in get_snapshot_dir().glob("*.json")]


def delete_snapshot(name: str) -> None:
    """Delete a named snapshot. Raises FileNotFoundError if missing."""
    path = snapshot_path(name)
    if not path.exists():
        raise FileNotFoundError(f"Snapshot '{name}' not found")
    path.unlink()
