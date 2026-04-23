"""Workflow: ordered sequence of snapshots to apply in succession."""
from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

from envsnap.storage import get_snapshot_dir, list_snapshots


class WorkflowNotFoundError(Exception):
    pass


class SnapshotNotFoundError(Exception):
    pass


def _workflows_path() -> Path:
    return get_snapshot_dir() / "workflows.json"


def _load_workflows() -> dict:
    p = _workflows_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_workflows(data: dict) -> None:
    _workflows_path().write_text(json.dumps(data, indent=2))


def create_workflow(name: str, steps: List[str], description: Optional[str] = None) -> None:
    """Create or overwrite a named workflow with an ordered list of snapshot names."""
    existing = list_snapshots()
    for step in steps:
        if step not in existing:
            raise SnapshotNotFoundError(f"Snapshot not found: {step!r}")
    data = _load_workflows()
    data[name] = {"steps": steps, "description": description or ""}
    _save_workflows(data)


def get_workflow(name: str) -> dict:
    """Return workflow dict with keys 'steps' and 'description'."""
    data = _load_workflows()
    if name not in data:
        raise WorkflowNotFoundError(f"Workflow not found: {name!r}")
    return data[name]


def delete_workflow(name: str) -> None:
    data = _load_workflows()
    if name not in data:
        raise WorkflowNotFoundError(f"Workflow not found: {name!r}")
    del data[name]
    _save_workflows(data)


def list_workflows() -> List[str]:
    return sorted(_load_workflows().keys())


def append_step(name: str, snapshot: str) -> None:
    """Append a snapshot step to an existing workflow."""
    existing = list_snapshots()
    if snapshot not in existing:
        raise SnapshotNotFoundError(f"Snapshot not found: {snapshot!r}")
    data = _load_workflows()
    if name not in data:
        raise WorkflowNotFoundError(f"Workflow not found: {name!r}")
    data[name]["steps"].append(snapshot)
    _save_workflows(data)
