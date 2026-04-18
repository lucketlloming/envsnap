"""Compare two snapshots and report differences."""

from typing import Dict, List, Tuple
from envsnap.storage import load_snapshot


def compare_snapshots(name_a: str, name_b: str) -> Dict[str, dict]:
    """Compare two snapshots and return a structured diff report."""
    snap_a = load_snapshot(name_a)
    snap_b = load_snapshot(name_b)

    keys_a = set(snap_a.keys())
    keys_b = set(snap_b.keys())

    only_in_a = {k: snap_a[k] for k in keys_a - keys_b}
    only_in_b = {k: snap_b[k] for k in keys_b - keys_a}
    changed = {
        k: {"from": snap_a[k], "to": snap_b[k]}
        for k in keys_a & keys_b
        if snap_a[k] != snap_b[k]
    }
    common = {
        k: snap_a[k]
        for k in keys_a & keys_b
        if snap_a[k] == snap_b[k]
    }

    return {
        "only_in_a": only_in_a,
        "only_in_b": only_in_b,
        "changed": changed,
        "common": common,
    }


def format_compare_report(name_a: str, name_b: str, result: Dict[str, dict]) -> str:
    """Format a comparison result as a human-readable string."""
    lines: List[str] = []
    lines.append(f"Comparing '{name_a}' vs '{name_b}'")
    lines.append("=" * 40)

    if result["only_in_a"]:
        lines.append(f"\nOnly in '{name_a}':")
        for k, v in sorted(result["only_in_a"].items()):
            lines.append(f"  - {k}={v}")

    if result["only_in_b"]:
        lines.append(f"\nOnly in '{name_b}':")
        for k, v in sorted(result["only_in_b"].items()):
            lines.append(f"  + {k}={v}")

    if result["changed"]:
        lines.append("\nChanged:")
        for k, diff in sorted(result["changed"].items()):
            lines.append(f"  ~ {k}: {diff['from']} -> {diff['to']}")

    if not result["only_in_a"] and not result["only_in_b"] and not result["changed"]:
        lines.append("\nSnapshots are identical.")
    else:
        lines.append(f"\nUnchanged: {len(result['common'])} variable(s)")

    return "\n".join(lines)
