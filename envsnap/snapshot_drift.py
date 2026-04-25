"""Detect drift between a snapshot and the current live environment."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envsnap.storage import load_snapshot


@dataclass
class DriftResult:
    snapshot_name: str
    added: Dict[str, str] = field(default_factory=dict)       # in live env, not in snapshot
    removed: Dict[str, str] = field(default_factory=dict)     # in snapshot, not in live env
    changed: Dict[str, tuple] = field(default_factory=dict)   # (snapshot_val, live_val)
    unchanged: List[str] = field(default_factory=list)

    @property
    def has_drift(self) -> bool:
        return bool(self.added or self.removed or self.changed)

    def as_dict(self) -> dict:
        return {
            "snapshot": self.snapshot_name,
            "has_drift": self.has_drift,
            "added": self.added,
            "removed": self.removed,
            "changed": {
                k: {"snapshot": v[0], "live": v[1]}
                for k, v in self.changed.items()
            },
            "unchanged_count": len(self.unchanged),
        }


def detect_drift(
    snapshot_name: str,
    live_env: Optional[Dict[str, str]] = None,
    keys: Optional[List[str]] = None,
) -> DriftResult:
    """Compare a saved snapshot against the live environment.

    Args:
        snapshot_name: Name of the snapshot to compare against.
        live_env: The live environment dict. Defaults to ``os.environ``.
        keys: Optional list of specific keys to restrict comparison to.

    Returns:
        A :class:`DriftResult` describing the drift.
    """
    import os

    snap_data: Dict[str, str] = load_snapshot(snapshot_name)
    env_data: Dict[str, str] = dict(live_env if live_env is not None else os.environ)

    if keys:
        snap_data = {k: v for k, v in snap_data.items() if k in keys}
        env_data = {k: v for k, v in env_data.items() if k in keys}

    result = DriftResult(snapshot_name=snapshot_name)

    all_keys = set(snap_data) | set(env_data)
    for k in all_keys:
        in_snap = k in snap_data
        in_env = k in env_data
        if in_snap and in_env:
            if snap_data[k] != env_data[k]:
                result.changed[k] = (snap_data[k], env_data[k])
            else:
                result.unchanged.append(k)
        elif in_env:
            result.added[k] = env_data[k]
        else:
            result.removed[k] = snap_data[k]

    return result


def format_drift(result: DriftResult, fmt: str = "text") -> str:
    if fmt == "json":
        import json
        return json.dumps(result.as_dict(), indent=2)

    lines = [f"Drift report for snapshot '{result.snapshot_name}'"]
    if not result.has_drift:
        lines.append("  No drift detected.")
        return "\n".join(lines)

    if result.added:
        lines.append("  Added in live env:")
        for k, v in sorted(result.added.items()):
            lines.append(f"    + {k}={v}")
    if result.removed:
        lines.append("  Removed from live env:")
        for k, v in sorted(result.removed.items()):
            lines.append(f"    - {k}={v}")
    if result.changed:
        lines.append("  Changed:")
        for k, (sv, lv) in sorted(result.changed.items()):
            lines.append(f"    ~ {k}: '{sv}' -> '{lv}'")
    return "\n".join(lines)
