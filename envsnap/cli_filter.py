"""CLI commands for filtering snapshots."""
from __future__ import annotations

import json

import click

from envsnap.snapshot_filter import filter_snapshots


@click.group(name="filter")
def filter_cmd() -> None:
    """Filter snapshots by various criteria."""


@filter_cmd.command(name="run")
@click.option("--key-prefix", default=None, help="Only snapshots containing keys with this prefix.")
@click.option("--min-keys", default=0, type=int, show_default=True, help="Minimum number of keys.")
@click.option("--max-keys", default=None, type=int, help="Maximum number of keys.")
@click.option("--value-pattern", default=None, help="Substring that must appear in at least one value.")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]), show_default=True)
def filter_run(
    key_prefix: str | None,
    min_keys: int,
    max_keys: int | None,
    value_pattern: str | None,
    fmt: str,
) -> None:
    """Run a filter query against all snapshots."""
    results = filter_snapshots(
        key_prefix=key_prefix,
        min_keys=min_keys,
        max_keys=max_keys,
        value_pattern=value_pattern,
    )

    if fmt == "json":
        click.echo(json.dumps(results, indent=2))
    else:
        if not results:
            click.echo("No snapshots matched the filter criteria.")
        else:
            for name in results:
                click.echo(name)
