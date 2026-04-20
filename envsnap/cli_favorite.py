"""CLI commands for managing favorite snapshots."""

from __future__ import annotations

import json

import click

from envsnap.favorite import add_favorite, remove_favorite, list_favorites, is_favorite


@click.group("favorite")
def favorite_cmd():
    """Star/unstar snapshots as favorites."""


@favorite_cmd.command("add")
@click.argument("name")
def favorite_add(name: str):
    """Mark NAME as a favorite."""
    try:
        add_favorite(name)
        click.echo(f"Snapshot '{name}' added to favorites.")
    except ValueError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@favorite_cmd.command("remove")
@click.argument("name")
def favorite_remove(name: str):
    """Unmark NAME as a favorite."""
    try:
        remove_favorite(name)
        click.echo(f"Snapshot '{name}' removed from favorites.")
    except ValueError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@favorite_cmd.command("list")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]))
def favorite_list(fmt: str):
    """List all favorited snapshots."""
    favs = list_favorites()
    if fmt == "json":
        click.echo(json.dumps(favs))
    else:
        if not favs:
            click.echo("No favorites set.")
        else:
            for name in favs:
                click.echo(f"  * {name}")


@favorite_cmd.command("check")
@click.argument("name")
def favorite_check(name: str):
    """Check if NAME is a favorite."""
    if is_favorite(name):
        click.echo(f"'{name}' is a favorite.")
    else:
        click.echo(f"'{name}' is not a favorite.")
