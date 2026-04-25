"""CLI commands for snapshot history."""

import json
import click

from envsnap.history import get_history, clear_history, format_history_report


@click.command("history")
@click.argument("snapshot_name", required=False, default=None)
@click.option("--format", "fmt", type=click.Choice(["text", "json"]), default="text",
              help="Output format.")
def history_cmd(snapshot_name, fmt):
    """Show history of actions for snapshots."""
    entries = get_history(snapshot_name)
    if not entries:
        name_hint = f" for '{snapshot_name}'" if snapshot_name else ""
        click.echo(f"No history entries found{name_hint}.")
        return
    if fmt == "json":
        click.echo(json.dumps(entries, indent=2))
    else:
        click.echo(format_history_report(entries))


@click.command("clear-history")
@click.argument("snapshot_name", required=False, default=None)
@click.option("--yes", is_flag=True, help="Skip confirmation prompt.")
def clear_history_cmd(snapshot_name, yes):
    """Clear history entries for a snapshot or all snapshots."""
    target = f"snapshot '{snapshot_name}'" if snapshot_name else "ALL snapshots"
    if not yes:
        click.confirm(f"Clear history for {target}?", abort=True)
    removed = clear_history(snapshot_name)
    click.echo(f"Removed {removed} history entry/entries.")
