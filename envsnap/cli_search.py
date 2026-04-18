"""CLI commands for searching snapshots."""
import click
from envsnap.search import search_snapshots, format_search_results


@click.group("search")
def search_cmd():
    """Search across snapshots by key or value patterns."""


@search_cmd.command("run")
@click.option("--key", "key_pattern", default=None, help="Glob pattern for key names.")
@click.option("--value", "value_pattern", default=None, help="Glob pattern for values.")
@click.option(
    "--snapshots", "snapshot_names", default=None,
    help="Comma-separated list of snapshot names to search."
)
@click.option(
    "--format", "fmt", default="text",
    type=click.Choice(["text", "json"], case_sensitive=False),
    help="Output format."
)
def search_run(key_pattern, value_pattern, snapshot_names, fmt):
    """Search snapshots matching KEY and/or VALUE patterns."""
    if not key_pattern and not value_pattern:
        raise click.UsageError("Provide at least --key or --value.")

    names = [s.strip() for s in snapshot_names.split(",")] if snapshot_names else None
    results = search_snapshots(
        key_pattern=key_pattern,
        value_pattern=value_pattern,
        snapshot_names=names,
    )
    click.echo(format_search_results(results, fmt=fmt))
