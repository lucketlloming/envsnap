"""Namespace support: group snapshots under named namespaces."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from envsnap.storage import get_snapshot_dir, list_snapshots


class NamespaceError(Exception):
    """Raised for invalid namespace operations."""


class SnapshotNotFoundError(Exception):
    """Raised when a snapshot does not exist."""


def _namespaces_path() -> Path:
    return get_snapshot_dir() / "namespaces.json"


def _load_namespaces() -> Dict[str, List[str]]:
    p = _namespaces_path()
    if not p.exists():
        return {}
    with p.open() as f:
        return json.load(f)


def _save_namespaces(data: Dict[str, List[str]]) -> None:
    _namespaces_path().write_text(json.dumps(data, indent=2))


def add_to_namespace(namespace: str, snapshot_name: str) -> None:
    """Add *snapshot_name* to *namespace*, creating it if necessary."""
    existing = list_snapshots()
    if snapshot_name not in existing:
        raise SnapshotNotFoundError(f"Snapshot '{snapshot_name}' does not exist.")
    if not namespace.strip():
        raise NamespaceError("Namespace name must not be empty.")
    data = _load_namespaces()
    members = data.setdefault(namespace, [])
    if snapshot_name not in members:
        members.append(snapshot_name)
    _save_namespaces(data)


def remove_from_namespace(namespace: str, snapshot_name: str) -> None:
    """Remove *snapshot_name* from *namespace*."""
    data = _load_namespaces()
    if namespace not in data or snapshot_name not in data[namespace]:
        raise NamespaceError(
            f"Snapshot '{snapshot_name}' is not in namespace '{namespace}'."
        )
    data[namespace].remove(snapshot_name)
    if not data[namespace]:
        del data[namespace]
    _save_namespaces(data)


def get_namespace(namespace: str) -> List[str]:
    """Return the list of snapshot names in *namespace*."""
    return _load_namespaces().get(namespace, [])


def list_namespaces() -> List[str]:
    """Return all defined namespace names."""
    return list(_load_namespaces().keys())


def delete_namespace(namespace: str) -> None:
    """Remove an entire namespace entry."""
    data = _load_namespaces()
    if namespace not in data:
        raise NamespaceError(f"Namespace '{namespace}' does not exist.")
    del data[namespace]
    _save_namespaces(data)
