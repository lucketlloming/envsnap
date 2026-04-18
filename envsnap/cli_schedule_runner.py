"""Runner that checks schedules and fires auto-snapshots when due."""

import os
from datetime import datetime, timedelta
from typing import Callable, Optional

from envsnap.schedule import list_schedules, update_last_run
from envsnap.snapshot import capture
from envsnap.storage import save_snapshot

_INTERVALS = {
    "hourly": timedelta(hours=1),
    "daily": timedelta(days=1),
    "weekly": timedelta(weeks=1),
}


def _is_due(last_run: Optional[str], interval: str) -> bool:
    if last_run is None:
        return True
    delta = _INTERVALS.get(interval)
    if delta is None:
        return False
    last_dt = datetime.fromisoformat(last_run)
    return datetime.utcnow() - last_dt >= delta


def run_due_schedules(
    env: Optional[dict] = None,
    on_snap: Optional[Callable[[str], None]] = None,
) -> list:
    """Check all schedules and execute any that are due.

    Args:
        env: Environment dict to snapshot (defaults to os.environ).
        on_snap: Optional callback invoked with snapshot name after each snap.

    Returns:
        List of snapshot names that were created.
    """
    if env is None:
        env = dict(os.environ)

    schedules = list_schedules()
    triggered = []

    for name, info in schedules.items():
        if not _is_due(info.get("last_run"), info["interval"]):
            continue

        keys = info.get("keys") or None
        snap_name = f"{name}-{datetime.utcnow().strftime('%Y%m%dT%H%M%S')}"
        data = capture(keys=keys, env=env)
        save_snapshot(snap_name, data)
        update_last_run(name)
        triggered.append(snap_name)

        if on_snap:
            on_snap(snap_name)

    return triggered
