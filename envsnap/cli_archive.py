"""CLI commands for snapshot archive export/import."""

from __future__ import annotations

import json
from pathlib import Path

import click

from envsnap.archive import export_archive, import_archive, ArchiveError


@click.group("archive")
def archive_cmd():
    """Bundle snapshots into a zip archive or restore from one."""


@archive_cmd.command("export")
@click.argument("dest")
@click.option("--name", "-n", multiple=True, help="Snapshot name(s) to include (default: all).")
@click.option("--format", "fmt", type=click.Choice(["text", "json"]), default="text")
def archive_export(dest: str, name: tuple[str, ...], fmt: str):
    """Export snapshots to a zip archive."""
    path = Path(dest)
    try:
        included = export_archive(list(name), path)
    except ArchiveError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    if fmt == "json":
        click.echo(json.dumps({"archive": str(path), "included": included}))
    else:
        click.echo(f"Archived {len(included)} snapshot(s) to {path}")
        for n in included:
            click.echo(f"  + {n}")


@archive_cmd.command("import")
@click.argument("src")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing snapshots.")
@click.option("--format", "fmt", type=click.Choice(["text", "json"]), default="text")
def archive_import(src: str, overwrite: bool, fmt: str):
    """Import snapshots from a zip archive."""
    path = Path(src)
    try:
        imported = import_archive(path, overwrite=overwrite)
    except ArchiveError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    if fmt == "json":
        click.echo(json.dumps({"imported": imported}))
    else:
        click.echo(f"Imported {len(imported)} snapshot(s) from {path}")
        for n in imported:
            click.echo(f"  + {n}")
