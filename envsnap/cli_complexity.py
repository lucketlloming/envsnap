"""CLI commands for snapshot complexity analysis."""
from __future__ import annotations

import json

import click

from envsnap.snapshot_complexity import (
    compute_complexity,
    compute_all_complexity,
    format_complexity,
)
from envsnap.storage import list_snapshots


@click.group("complexity")
def complexity_cmd() -> None:
    """Analyse structural complexity of snapshots."""


@complexity_cmd.command("show")
@click.argument("name")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]), show_default=True)
def complexity_show(name: str, fmt: str) -> None:
    """Show complexity analysis for a single snapshot."""
    try:
        result = compute_complexity(name)
    except FileNotFoundError:
        raise click.ClickException(f"Snapshot '{name}' not found.")

    if fmt == "json":
        click.echo(json.dumps(result.as_dict(), indent=2))
    else:
        click.echo(format_complexity(result))


@complexity_cmd.command("all")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]), show_default=True)
@click.option("--sort", "sort_by", default="score", type=click.Choice(["score", "name", "key_count"]), show_default=True)
@click.option("--desc", is_flag=True, default=False, help="Sort descending.")
def complexity_all(fmt: str, sort_by: str, desc: bool) -> None:
    """Show complexity analysis for all snapshots."""
    names = list_snapshots()
    if not names:
        click.echo("No snapshots found.")
        return

    results = compute_all_complexity()
    results.sort(key=lambda r: getattr(r, sort_by), reverse=desc)

    if fmt == "json":
        click.echo(json.dumps([r.as_dict() for r in results], indent=2))
    else:
        for r in results:
            click.echo(f"{r.name:<30} score={r.score:6.2f}  level={r.level:<6}  keys={r.key_count}")
