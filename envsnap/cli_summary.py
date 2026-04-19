"""CLI commands for snapshot summary."""
import click
import json
from envsnap.summary import summarize_snapshot, summarize_all, format_summary
from envsnap.storage import SnapshotNotFoundError


@click.group("summary")
def summary_cmd():
    """Show snapshot summaries."""


@summary_cmd.command("show")
@click.argument("name")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]), show_default=True)
def summary_show(name: str, fmt: str):
    """Show summary for a single snapshot."""
    try:
        s = summarize_snapshot(name)
    except SnapshotNotFoundError:
        click.echo(f"Snapshot '{name}' not found.", err=True)
        raise SystemExit(1)
    if fmt == "json":
        click.echo(json.dumps(s, indent=2))
    else:
        click.echo(format_summary(s))


@summary_cmd.command("all")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]), show_default=True)
@click.option("--separator", default="---", show_default=True, help="Separator line between summaries in text mode.")
def summary_all(fmt: str, separator: str):
    """Show summaries for all snapshots."""
    summaries = summarize_all()
    if not summaries:
        click.echo("No snapshots found.")
        return
    if fmt == "json":
        click.echo(json.dumps(summaries, indent=2))
    else:
        for s in summaries:
            click.echo(format_summary(s))
            click.echo(separator)
