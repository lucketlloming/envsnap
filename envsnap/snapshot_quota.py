"""Snapshot quota management: enforce limits on snapshot count per project/namespace."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from envsnap.storage import get_snapshot_dir, list_snapshots


class QuotaExceededError(Exception):
    """Raised when creating a snapshot would exceed the configured quota."""


class QuotaNotFoundError(Exception):
    """Raised when no quota is configured for a given scope."""


def _quota_path() -> Path:
    return get_snapshot_dir() / "_quotas.json"


def _load_quotas() -> dict:
    p = _quota_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_quotas(data: dict) -> None:
    _quota_path().write_text(json.dumps(data, indent=2))


def set_quota(scope: str, max_snapshots: int) -> None:
    """Set the maximum number of snapshots allowed for *scope*."""
    if max_snapshots < 1:
        raise ValueError("max_snapshots must be >= 1")
    data = _load_quotas()
    data[scope] = {"max_snapshots": max_snapshots}
    _save_quotas(data)


def get_quota(scope: str) -> Optional[dict]:
    """Return quota config for *scope*, or None if not set."""
    return _load_quotas().get(scope)


def remove_quota(scope: str) -> None:
    """Remove quota for *scope*."""
    data = _load_quotas()
    if scope not in data:
        raise QuotaNotFoundError(f"No quota configured for scope '{scope}'")
    del data[scope]
    _save_quotas(data)


def list_quotas() -> dict:
    """Return all configured quotas."""
    return _load_quotas()


def check_quota(scope: str, prefix: str = "") -> None:
    """Raise QuotaExceededError if adding a snapshot would exceed the quota.

    *prefix* is used to filter snapshot names belonging to *scope*.
    If no quota is set for *scope* the check is a no-op.
    """
    quota = get_quota(scope)
    if quota is None:
        return
    all_names = list_snapshots()
    scoped = [n for n in all_names if n.startswith(prefix or scope)]
    if len(scoped) >= quota["max_snapshots"]:
        raise QuotaExceededError(
            f"Quota exceeded for scope '{scope}': "
            f"{len(scoped)}/{quota['max_snapshots']} snapshots used."
        )
