"""CLI commands for snapshot recommendations."""
from __future__ import annotations

import click

from envsnap.snapshot_recommendation import recommend, recommend_all, format_recommendations
from envsnap.storage import load_snapshot


@click.group("recommend")
def recommend_cmd() -> None:
    """Snapshot recommendation commands."""


@recommend_cmd.command("show")
@click.argument("name")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]),
              show_default=True, help="Output format.")
def recommend_show(name: str, fmt: str) -> None:
    """Show recommendations for a single snapshot."""
    try:
        load_snapshot(name)  # validate existence
    except FileNotFoundError:
        raise click.ClickException(f"Snapshot '{name}' not found.")

    recs = recommend(name)
    click.echo(format_recommendations(recs, fmt=fmt))


@recommend_cmd.command("all")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]),
              show_default=True, help="Output format.")
@click.option("--level", default=None,
              type=click.Choice(["info", "warning", "action"]),
              help="Filter by recommendation level.")
def recommend_all_cmd(fmt: str, level: str | None) -> None:
    """Show recommendations for all snapshots."""
    recs = recommend_all()
    if level:
        recs = [r for r in recs if r.level == level]
    click.echo(format_recommendations(recs, fmt=fmt))
