"""CLI commands for snapshot freshness analysis."""
from __future__ import annotations

import json

import click

from envsnap.snapshot_freshness import (
    compute_freshness,
    compute_all_freshness,
    format_freshness,
)


@click.group("freshness")
def freshness_cmd():
    """Analyse how recently snapshots were used or modified."""


@freshness_cmd.command("show")
@click.argument("name")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
def freshness_show(name: str, as_json: bool):
    """Show freshness for a single snapshot."""
    try:
        result = compute_freshness(name)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc))

    if as_json:
        click.echo(json.dumps(result.as_dict(), indent=2))
    else:
        click.echo(format_freshness(result))


@freshness_cmd.command("all")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
@click.option(
    "--level",
    type=click.Choice(["fresh", "stale", "aged", "unknown"]),
    default=None,
    help="Filter by freshness level.",
)
def freshness_all(as_json: bool, level: str | None):
    """Show freshness for all snapshots."""
    results = compute_all_freshness()
    if level:
        results = [r for r in results if r.level == level]

    if as_json:
        click.echo(json.dumps([r.as_dict() for r in results], indent=2))
    else:
        if not results:
            click.echo("No snapshots found.")
            return
        for r in results:
            click.echo(format_freshness(r))
            click.echo("---")
