"""Export and import snapshots to/from portable file formats."""

import json
import os
from pathlib import Path
from typing import Dict, Optional

from envsnap.storage import load_snapshot, save_snapshot


def export_snapshot(name: str, output_path: str, fmt: str = "env") -> None:
    """Export a named snapshot to a file.

    Args:
        name: Snapshot name to export.
        output_path: Destination file path.
        fmt: Format — 'env' for dotenv style, 'json' for JSON.
    """
    data = load_snapshot(name)
    path = Path(output_path)

    if fmt == "json":
        path.write_text(json.dumps(data, indent=2))
    elif fmt == "env":
        lines = [f"{k}={v}" for k, v in sorted(data.items())]
        path.write_text("\n".join(lines) + "\n")
    else:
        raise ValueError(f"Unsupported format: {fmt!r}. Use 'env' or 'json'.")


def import_snapshot(name: str, input_path: str, fmt: Optional[str] = None) -> None:
    """Import a snapshot from a file.

    Args:
        name: Snapshot name to save as.
        input_path: Source file path.
        fmt: Format — 'env' or 'json'. Auto-detected from extension if None.
    """
    path = Path(input_path)
    if not path.exists():
        raise FileNotFoundError(f"Import file not found: {input_path}")

    if fmt is None:
        fmt = "json" if path.suffix == ".json" else "env"

    if fmt == "json":
        data: Dict[str, str] = json.loads(path.read_text())
    elif fmt == "env":
        data = {}
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            key, _, value = line.partition("=")
            data[key.strip()] = value.strip()
    else:
        raise ValueError(f"Unsupported format: {fmt!r}. Use 'env' or 'json'.")

    save_snapshot(name, data)
