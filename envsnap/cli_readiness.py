"""CLI commands for snapshot readiness assessment."""
from __future__ import annotations

import json

import click

from envsnap.snapshot_readiness import (
    assess_readiness,
    assess_all_readiness,
    format_readiness,
)
from envsnap.storage import SnapshotNotFoundError


@click.group("readiness")
def readiness_cmd() -> None:
    """Assess snapshot readiness for production use."""


@readiness_cmd.command("show")
@click.argument("snapshot")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]), show_default=True)
def readiness_show(snapshot: str, fmt: str) -> None:
    """Show readiness report for a single snapshot."""
    try:
        result = assess_readiness(snapshot)
    except SnapshotNotFoundError:
        raise click.ClickException(f"Snapshot '{snapshot}' not found.")

    if fmt == "json":
        click.echo(json.dumps(result.as_dict(), indent=2))
    else:
        click.echo(format_readiness(result))


@readiness_cmd.command("all")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]), show_default=True)
@click.option("--min-level", default=None, type=click.Choice(["ready", "nearly-ready", "not-ready"]),
              help="Filter results to at most this level.")
def readiness_all(fmt: str, min_level: str | None) -> None:
    """Show readiness report for all snapshots."""
    results = assess_all_readiness()

    _order = {"ready": 0, "nearly-ready": 1, "not-ready": 2}
    if min_level is not None:
        threshold = _order[min_level]
        results = [r for r in results if _order[r.level] >= threshold]

    if fmt == "json":
        click.echo(json.dumps([r.as_dict() for r in results], indent=2))
    else:
        if not results:
            click.echo("No snapshots match the filter.")
            return
        for r in results:
            click.echo(format_readiness(r))
            click.echo()
