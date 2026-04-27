"""CLI commands for snapshot impact assessment."""
from __future__ import annotations

import json

import click

from envsnap.snapshot_impact import assess_impact, assess_all_impact, format_impact


@click.group("impact")
def impact_cmd() -> None:
    """Assess the relational impact of snapshots."""


@impact_cmd.command("show")
@click.argument("name")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]), show_default=True)
def impact_show(name: str, fmt: str) -> None:
    """Show impact assessment for a single snapshot."""
    try:
        result = assess_impact(name)
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc

    if fmt == "json":
        click.echo(json.dumps(result.as_dict(), indent=2))
    else:
        click.echo(format_impact(result))


@impact_cmd.command("all")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]), show_default=True)
@click.option("--sort", "sort_by", default="score", type=click.Choice(["score", "name"]), show_default=True)
def impact_all(fmt: str, sort_by: str) -> None:
    """Show impact assessment for all snapshots."""
    results = assess_all_impact()
    if sort_by == "score":
        results = sorted(results, key=lambda r: r.score, reverse=True)
    else:
        results = sorted(results, key=lambda r: r.name)

    if fmt == "json":
        click.echo(json.dumps([r.as_dict() for r in results], indent=2))
    else:
        for r in results:
            click.echo(format_impact(r))
            click.echo()
