"""CLI commands for managing auto-snapshot schedules."""

import json
import click
from envsnap.schedule import set_schedule, remove_schedule, list_schedules, get_schedule


@click.group("schedule")
def schedule_cmd():
    """Manage auto-snapshot schedules."""


@schedule_cmd.command("set")
@click.argument("name")
@click.option("--interval", required=True, type=click.Choice(["hourly", "daily", "weekly"]), help="Snapshot frequency")
@click.option("--keys", default=None, help="Comma-separated env keys to capture (default: all)")
def schedule_set(name, interval, keys):
    """Register a scheduled snapshot for NAME."""
    key_list = [k.strip() for k in keys.split(",")] if keys else []
    set_schedule(name, interval, keys=key_list)
    click.echo(f"Schedule set: '{name}' every {interval}.")


@schedule_cmd.command("remove")
@click.argument("name")
def schedule_remove(name):
    """Remove a scheduled snapshot for NAME."""
    try:
        remove_schedule(name)
        click.echo(f"Schedule removed: '{name}'.")
    except KeyError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@schedule_cmd.command("list")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def schedule_list(as_json):
    """List all scheduled snapshots."""
    schedules = list_schedules()
    if as_json:
        click.echo(json.dumps(schedules, indent=2))
        return
    if not schedules:
        click.echo("No schedules configured.")
        return
    for name, info in schedules.items():
        keys_str = ", ".join(info["keys"]) if info["keys"] else "all"
        last = info["last_run"] or "never"
        click.echo(f"{name}: {info['interval']} | keys={keys_str} | last_run={last}")


@schedule_cmd.command("show")
@click.argument("name")
def schedule_show(name):
    """Show details for a specific schedule."""
    try:
        info = get_schedule(name)
        click.echo(json.dumps(info, indent=2))
    except KeyError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)
