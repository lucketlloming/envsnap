"""Snapshot vitals: quick health-like metrics for a snapshot."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from envsnap.storage import load_snapshot, list_snapshots
from envsnap.history import get_history
from envsnap.pin import get_pin
from envsnap.lock import is_locked
from envsnap.expire import get_expiry


@dataclass
class VitalsResult:
    name: str
    key_count: int
    empty_count: int
    event_count: int
    is_pinned: bool
    is_locked: bool
    expiry: Optional[str]
    fill_rate: float  # percentage of non-empty values

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "key_count": self.key_count,
            "empty_count": self.empty_count,
            "event_count": self.event_count,
            "is_pinned": self.is_pinned,
            "is_locked": self.is_locked,
            "expiry": self.expiry,
            "fill_rate": round(self.fill_rate, 2),
        }


def compute_vitals(name: str) -> VitalsResult:
    """Compute vitals for a single snapshot."""
    data = load_snapshot(name)
    key_count = len(data)
    empty_count = sum(1 for v in data.values() if not v or not v.strip())
    fill_rate = ((key_count - empty_count) / key_count * 100) if key_count else 0.0

    events = get_history(name)
    event_count = len(events)

    pinned = False
    try:
        pinned = get_pin(name) is not None
    except Exception:
        pass

    locked = False
    try:
        locked = is_locked(name)
    except Exception:
        pass

    expiry = None
    try:
        exp = get_expiry(name)
        expiry = exp.get("expires_at") if exp else None
    except Exception:
        pass

    return VitalsResult(
        name=name,
        key_count=key_count,
        empty_count=empty_count,
        event_count=event_count,
        is_pinned=pinned,
        is_locked=locked,
        expiry=expiry,
        fill_rate=fill_rate,
    )


def compute_all_vitals() -> list[VitalsResult]:
    """Compute vitals for every snapshot."""
    return [compute_vitals(n) for n in list_snapshots()]


def format_vitals(result: VitalsResult) -> str:
    lines = [
        f"Snapshot : {result.name}",
        f"Keys     : {result.key_count}  (empty: {result.empty_count})",
        f"Fill rate: {result.fill_rate:.1f}%",
        f"Events   : {result.event_count}",
        f"Pinned   : {'yes' if result.is_pinned else 'no'}",
        f"Locked   : {'yes' if result.is_locked else 'no'}",
        f"Expiry   : {result.expiry or 'none'}",
    ]
    return "\n".join(lines)
