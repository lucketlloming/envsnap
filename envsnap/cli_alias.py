"""CLI commands for snapshot aliases."""

from __future__ import annotations

import click

from envsnap.alias import set_alias, remove_alias, list_aliases, resolve_alias


@click.group("alias")
def alias_cmd():
    """Manage snapshot aliases."""


@alias_cmd.command("set")
@click.argument("alias")
@click.argument("snapshot")
def alias_set(alias: str, snapshot: str):
    """Create or update ALIAS pointing to SNAPSHOT."""
    try:
        set_alias(alias, snapshot)
        click.echo(f"Alias '{alias}' -> '{snapshot}' saved.")
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc))


@alias_cmd.command("remove")
@click.argument("alias")
def alias_remove(alias: str):
    """Remove ALIAS."""
    try:
        remove_alias(alias)
        click.echo(f"Alias '{alias}' removed.")
    except KeyError as exc:
        raise click.ClickException(str(exc))


@alias_cmd.command("show")
@click.argument("alias")
def alias_show(alias: str):
    """Show the snapshot name for ALIAS."""
    target = resolve_alias(alias)
    if target is None:
        raise click.ClickException(f"Alias '{alias}' not found.")
    click.echo(target)


@alias_cmd.command("list")
def alias_list():
    """List all aliases."""
    data = list_aliases()
    if not data:
        click.echo("No aliases defined.")
        return
    for alias, snapshot in sorted(data.items()):
        click.echo(f"{alias} -> {snapshot}")
