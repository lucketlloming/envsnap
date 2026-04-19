"""Archive and restore snapshots as compressed zip bundles."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

from envsnap.storage import list_snapshots, load_snapshot, save_snapshot


class ArchiveError(Exception):
    pass


def export_archive(names: list[str], dest: Path) -> list[str]:
    """Write named snapshots into a zip archive. Returns list of included names."""
    if not names:
        names = list_snapshots()
    if not names:
        raise ArchiveError("No snapshots available to archive.")

    included = []
    with zipfile.ZipFile(dest, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name in names:
            try:
                data = load_snapshot(name)
            except FileNotFoundError:
                raise ArchiveError(f"Snapshot not found: {name}")
            zf.writestr(f"{name}.json", json.dumps(data))
            included.append(name)
    return included


def import_archive(src: Path, overwrite: bool = False) -> list[str]:
    """Load snapshots from a zip archive. Returns list of imported names."""
    if not src.exists():
        raise ArchiveError(f"Archive not found: {src}")

    imported = []
    existing = set(list_snapshots())
    with zipfile.ZipFile(src, "r") as zf:
        for entry in zf.namelist():
            if not entry.endswith(".json"):
                continue
            name = entry[:-5]
            if name in existing and not overwrite:
                raise ArchiveError(
                    f"Snapshot '{name}' already exists. Use overwrite=True to replace."
                )
            data = json.loads(zf.read(entry))
            save_snapshot(name, data)
            imported.append(name)
    return imported
