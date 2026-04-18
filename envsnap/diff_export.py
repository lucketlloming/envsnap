"""Export diff/compare results to file formats."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Literal

from envsnap.compare import compare_snapshots, format_compare_report

ExportFormat = Literal["json", "text"]


def export_diff(
    name_a: str,
    name_b: str,
    fmt: ExportFormat = "text",
    output_path: str | None = None,
) -> str:
    """Compare two snapshots and return (or write) the result.

    Args:
        name_a: First snapshot name.
        name_b: Second snapshot name.
        fmt: Output format — 'text' or 'json'.
        output_path: If provided, write result to this file path.

    Returns:
        The formatted diff string.
    """
    result = compare_snapshots(name_a, name_b)

    if fmt == "json":
        payload = {
            "snapshot_a": name_a,
            "snapshot_b": name_b,
            "only_in_a": result["only_in_a"],
            "only_in_b": result["only_in_b"],
            "changed": result["changed"],
            "common": result["common"],
        }
        content = json.dumps(payload, indent=2)
    elif fmt == "text":
        content = format_compare_report(name_a, name_b, result)
    else:
        raise ValueError(f"Unsupported format: {fmt!r}. Choose 'text' or 'json'.")

    if output_path:
        Path(output_path).write_text(content, encoding="utf-8")

    return content
