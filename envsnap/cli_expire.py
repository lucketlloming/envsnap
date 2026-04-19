"""CLI commands for snapshot expiry management."""
from __future__ import annotations

import json

import click

from envsnap.expire import (
    ExpiryNotFoundError,
    SnapshotNotFoundError,
    get_expired,
    get_expiry,
    list_expiry,
    remove_expiry,
    set_expiry,
)


@click.group("expire")
def expire_cmd():
    """Manage snapshot expiry dates."""


@expire_cmd.command("set")
@click.argument("name")
@click.argument("date")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]))
def expire_set(name: str, date: str, fmt: str):
    """Set expiry DATE (YYYY-MM-DD) for snapshot NAME."""
    try:
        set_expiry(name, date)
    except SnapshotNotFoundError:
        click.echo(f"Error: snapshot '{name}' not found.", err=True)
        raise SystemExit(1)
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
    if fmt == "json":
        click.echo(json.dumps({"snapshot": name, "expiry": date}))
    else:
        click.echo(f"Expiry for '{name}' set to {date}.")


@expire_cmd.command("remove")
@click.argument("name")
def expire_remove(name: str):
    """Remove the expiry date for snapshot NAME."""
    try:
        remove_expiry(name)
    except ExpiryNotFoundError:
        click.echo(f"Error: no expiry set for '{name}'.", err=True)
        raise SystemExit(1)
    click.echo(f"Expiry for '{name}' removed.")


@expire_cmd.command("list")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]))
def expire_list(fmt: str):
    """List all snapshots with expiry dates."""
    data = list_expiry()
    if fmt == "json":
        click.echo(json.dumps(data))
    else:
        if not data:
            click.echo("No expiry dates set.")
        else:
            for name, date in sorted(data.items()):
                click.echo(f"  {name}: {date}")


@expire_cmd.command("check")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]))
def expire_check(fmt: str):
    """List snapshots whose expiry date has passed."""
    expired = get_expired()
    if fmt == "json":
        click.echo(json.dumps({"expired": expired}))
    else:
        if not expired:
            click.echo("No expired snapshots.")
        else:
            click.echo("Expired snapshots:")
            for name in expired:
                click.echo(f"  {name}")
