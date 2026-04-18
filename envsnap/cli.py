"""Main CLI entry point for envsnap."""

import click

from envsnap.snapshot import capture, restore, diff
from envsnap.storage import save_snapshot, load_snapshot, list_snapshots, delete_snapshot
from envsnap.cli_export import export_cmd, import_cmd


@click.group()
def cli() -> None:
    """envsnap — snapshot and restore environment variables."""


@cli.command()
@click.argument("name")
@click.option("--keys", "-k", multiple=True, help="Specific keys to capture.")
def snap(name: str, keys) -> None:
    """Capture current environment as snapshot NAME."""
    data = capture(list(keys) if keys else None)
    save_snapshot(name, data)
    click.echo(f"Saved snapshot '{name}' with {len(data)} variable(s).")


@cli.command()
@click.argument("name")
def show(name: str) -> None:
    """Show variables stored in snapshot NAME."""
    try:
        data = load_snapshot(name)
    except FileNotFoundError:
        raise click.ClickException(f"Snapshot '{name}' not found.")
    for k, v in sorted(data.items()):
        click.echo(f"{k}={v}")


@cli.command(name="list")
def list_cmd() -> None:
    """List all saved snapshots."""
    names = list_snapshots()
    if not names:
        click.echo("No snapshots found.")
    for name in names:
        click.echo(name)


@cli.command()
@click.argument("name")
def delete(name: str) -> None:
    """Delete snapshot NAME."""
    try:
        delete_snapshot(name)
        click.echo(f"Deleted snapshot '{name}'.")
    except FileNotFoundError:
        raise click.ClickException(f"Snapshot '{name}' not found.")


@cli.command()
@click.argument("name")
def apply(name: str) -> None:
    """Print shell export commands to restore snapshot NAME."""
    try:
        data = load_snapshot(name)
    except FileNotFoundError:
        raise click.ClickException(f"Snapshot '{name}' not found.")
    for k, v in sorted(data.items()):
        click.echo(f"export {k}={v!r}")


@cli.command()
@click.argument("name")
def diffcmd(name: str) -> None:
    """Show diff between current env and snapshot NAME."""
    try:
        data = load_snapshot(name)
    except FileNotFoundError:
        raise click.ClickException(f"Snapshot '{name}' not found.")
    changes = diff(data)
    if not changes:
        click.echo("No differences.")
        return
    for change in changes:
        click.echo(change)


cli.add_command(export_cmd)
cli.add_command(import_cmd)


if __name__ == "__main__":
    cli()
