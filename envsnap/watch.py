"""Watch environment variables for changes and record diffs."""
from __future__ import annotations

import os
import time
from typing import Callable, Dict, Optional

from envsnap.snapshot import capture
from envsnap.compare import compare_snapshots, format_compare_report


def _current_env(keys: Optional[list] = None) -> Dict[str, str]:
    if keys:
        return {k: os.environ[k] for k in keys if k in os.environ}
    return dict(os.environ)


def watch(
    interval: float = 5.0,
    keys: Optional[list] = None,
    on_change: Optional[Callable[[dict], None]] = None,
    max_iterations: Optional[int] = None,
) -> None:
    """Poll environment variables and invoke callback on change.

    Args:
        interval: Seconds between polls.
        keys: Specific keys to watch; None means all.
        on_change: Called with compare result dict when a change is detected.
        max_iterations: Stop after N iterations (useful for testing).
    """
    previous = _current_env(keys)
    iterations = 0

    while True:
        time.sleep(interval)
        current = _current_env(keys)
        result = compare_snapshots(previous, current)
        changed = any(result[k] for k in ("only_in_a", "only_in_b", "changed"))
        if changed:
            if on_change:
                on_change(result)
        previous = current
        iterations += 1
        if max_iterations is not None and iterations >= max_iterations:
            break
