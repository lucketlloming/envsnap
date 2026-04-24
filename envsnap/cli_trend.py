"""CLI commands for snapshot trend analysis."""
from __future__ import annotations

import json

import click

from envsnap.snapshot_trend import build_trend, build_all_trends, format_trend


@click.group("trend")
def trend_cmd():
    """Analyse snapshot usage trends over time."""


@trend_cmd.command("show")
@click.argument("name")
@click.option("--event", default="snap", show_default=True, help="Event type to analyse.")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]), show_default=True)
def trend_show(name: str, event: str, fmt: str):
    """Show trend for a single snapshot."""
    result = build_trend(name, event_type=event)
    if fmt == "json":
        click.echo(json.dumps(result.as_dict(), indent=2))
    else:
        click.echo(format_trend(result))


@trend_cmd.command("all")
@click.option("--event", default="snap", show_default=True, help="Event type to analyse.")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]), show_default=True)
@click.option("--min-total", default=1, show_default=True, help="Only show snapshots with at least this many events.")
def trend_all(event: str, fmt: str, min_total: int):
    """Show trends for all snapshots."""
    results = [r for r in build_all_trends(event_type=event) if r.total >= min_total]
    if not results:
        click.echo("No trend data available.")
        return
    if fmt == "json":
        click.echo(json.dumps([r.as_dict() for r in results], indent=2))
    else:
        for r in results:
            click.echo(format_trend(r))
            click.echo()
