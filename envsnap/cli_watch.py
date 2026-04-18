"""CLI commands for watching environment variable changes."""
from __future__ import annotations

import json
import os
import click

from envsnap.compare import format_compare_report
from envsnap.watch import watch


@click.group("watch")
def watch_cmd():
    """Watch environment variables for live changes."""


@watch_cmd.command("start")
@click.option("--interval", default=5.0, show_default=True, help="Poll interval in seconds.")
@click.option("--key", "keys", multiple=True, help="Specific keys to watch (repeatable).")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]), show_default=True)
def watch_start(interval: float, keys: tuple, fmt: str):
    """Start watching environment variables for changes."""
    key_list = list(keys) if keys else None
    click.echo(f"Watching {'keys: ' + ', '.join(key_list) if key_list else 'all env vars'} every {interval}s...")

    def on_change(result: dict):
        if fmt == "json":
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo("[envsnap] Environment change detected:")
            click.echo(format_compare_report(result))

    try:
        watch(interval=interval, keys=key_list, on_change=on_change)
    except KeyboardInterrupt:
        click.echo("\nWatch stopped.")
