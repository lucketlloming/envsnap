"""CLI entry point for envsnap."""

import click
from envsnap.snapshot import capture, restore, diff
from envsnap.storage import list_snapshots, delete_snapshot


@click.group()
def cli():
    """envsnap — snapshot and restore local environment variables."""


@cli.command()
@click.argument("name")
@click.option("--keys", "-k", multiple=True, help="Specific env var keys to capture.")
def snap(name, keys):
    """Capture current environment variables into a snapshot."""
    variables = capture(name, list(keys) if keys else None)
    click.echo(f"Snapshot '{name}' saved with {len(variables)} variable(s).")


@cli.command()
@click.argument("name")
def show(name):
    """Display variables stored in a snapshot."""
    from envsnap.storage import load_snapshot
    data = load_snapshot(name)
    click.echo(f"Snapshot: {data['name']}  (created {data['created_at']})")
    for k, v in sorted(data["variables"].items()):
        click.echo(f"  {k}={v}")


@cli.command(name="list")
def list_cmd():
    """List all saved snapshots."""
    names = list_snapshots()
    if not names:
        click.echo("No snapshots found.")
    for name in sorted(names):
        click.echo(name)


@cli.command()
@click.argument("name")
def delete(name):
    """Delete a snapshot by name."""
    delete_snapshot(name)
    click.echo(f"Snapshot '{name}' deleted.")


@cli.command()
@click.argument("name")
def compare(name):
    """Compare a snapshot to the current environment."""
    result = diff(name)
    if result["added"]:
        click.echo("Added (in current, not in snapshot):")
        for k, v in result["added"].items():
            click.echo(f"  + {k}={v}")
    if result["removed"]:
        click.echo("Removed (in snapshot, not in current):")
        for k, v in result["removed"].items():
            click.echo(f"  - {k}={v}")
    if result["changed"]:
        click.echo("Changed:")
        for k, vals in result["changed"].items():
            click.echo(f"  ~ {k}: {vals['old']} -> {vals['new']}")
    if not any(result.values()):
        click.echo("No differences found.")


if __name__ == "__main__":
    cli()
