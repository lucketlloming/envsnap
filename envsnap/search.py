"""Search snapshots by key/value patterns."""
from __future__ import annotations
import fnmatch
from typing import Optional
from envsnap.storage import list_snapshots, load_snapshot


def search_snapshots(
    key_pattern: Optional[str] = None,
    value_pattern: Optional[str] = None,
    snapshot_names: Optional[list[str]] = None,
) -> dict[str, dict[str, str]]:
    """Return {snapshot_name: {key: value}} for matches.

    Filters snapshots by key_pattern and/or value_pattern (both support globs).
    If snapshot_names is given, only those snapshots are searched.
    """
    names = snapshot_names if snapshot_names is not None else list_snapshots()
    results: dict[str, dict[str, str]] = {}

    for name in names:
        try:
            data = load_snapshot(name)
        except FileNotFoundError:
            continue

        matched: dict[str, str] = {}
        for k, v in data.items():
            if key_pattern and not fnmatch.fnmatch(k, key_pattern):
                continue
            if value_pattern and not fnmatch.fnmatch(v, value_pattern):
                continue
            matched[k] = v

        if matched:
            results[name] = matched

    return results


def format_search_results(results: dict[str, dict[str, str]], fmt: str = "text") -> str:
    """Format search results as text or json."""
    if fmt == "json":
        import json
        return json.dumps(results, indent=2)

    if not results:
        return "No matches found."

    lines: list[str] = []
    for snap_name, pairs in results.items():
        lines.append(f"[{snap_name}]")
        for k, v in pairs.items():
            lines.append(f"  {k}={v}")
    return "\n".join(lines)
