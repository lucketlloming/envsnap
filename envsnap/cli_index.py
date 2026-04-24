"""CLI commands for the snapshot index."""
from __future__ import annotations

import json

import click

from envsnap.snapshot_index import load_index, refresh_index, query_index


@click.group("index")
def index_cmd() -> None:
    """Manage and query the snapshot index."""


@index_cmd.command("refresh")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]))
def index_refresh(fmt: str) -> None:
    """Rebuild the snapshot index from disk."""
    index = refresh_index()
    if fmt == "json":
        click.echo(json.dumps({"refreshed": list(index.keys())}, indent=2))
    else:
        click.echo(f"Index refreshed: {len(index)} snapshot(s) indexed.")


@index_cmd.command("query")
@click.option("--tag", default=None, help="Filter by tag.")
@click.option("--pinned", is_flag=True, default=False, help="Only pinned snapshots.")
@click.option("--min-keys", type=int, default=None, help="Minimum key count.")
@click.option("--max-keys", type=int, default=None, help="Maximum key count.")
@click.option("--has-note", is_flag=True, default=False, help="Only snapshots with a note.")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]))
def index_query(
    tag: str | None,
    pinned: bool,
    min_keys: int | None,
    max_keys: int | None,
    has_note: bool,
    fmt: str,
) -> None:
    """Query the snapshot index with optional filters."""
    index = load_index()
    results = query_index(
        index,
        tag=tag,
        pinned=pinned if pinned else None,
        min_keys=min_keys,
        max_keys=max_keys,
        has_note=has_note if has_note else None,
    )
    if fmt == "json":
        click.echo(json.dumps(results, indent=2))
    else:
        if not results:
            click.echo("No snapshots matched.")
        else:
            for name in results:
                meta = index[name]
                tags_str = ", ".join(meta.get("tags", [])) or "—"
                pin_str = "pinned" if meta.get("pinned") else "unpinned"
                click.echo(f"  {name}  [{meta['key_count']} keys] [{pin_str}] tags: {tags_str}")


@index_cmd.command("show")
@click.argument("name")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]))
def index_show(name: str, fmt: str) -> None:
    """Show index metadata for a single snapshot."""
    index = load_index()
    if name not in index:
        click.echo(f"Snapshot '{name}' not found in index.", err=True)
        raise SystemExit(1)
    meta = index[name]
    if fmt == "json":
        click.echo(json.dumps({name: meta}, indent=2))
    else:
        click.echo(f"Snapshot : {name}")
        click.echo(f"Keys     : {meta['key_count']}")
        click.echo(f"Pinned   : {meta.get('pinned', False)}")
        click.echo(f"Tags     : {', '.join(meta.get('tags', [])) or '—'}")
        click.echo(f"Note     : {meta.get('note') or '—'}")
