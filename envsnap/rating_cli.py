import click
import json
from envsnap.rating import (
    set_rating,
    get_rating,
    remove_rating,
    list_ratings,
    InvalidRatingError,
    SnapshotNotFoundError,
)


@click.group(name="rating")
def rating_cmd():
    """Manage snapshot ratings (1-5 stars)."""


@rating_cmd.command(name="set")
@click.argument("name")
@click.argument("score", type=int)
@click.option("--note", default=None, help="Optional note for this rating.")
def rating_set(name, score, note):
    """Set a rating (1-5) for a snapshot."""
    try:
        set_rating(name, score, note=note)
        click.echo(f"Rated '{name}': {score}/5" + (f" — {note}" if note else ""))
    except SnapshotNotFoundError:
        click.echo(f"Error: snapshot '{name}' not found.", err=True)
        raise SystemExit(1)
    except InvalidRatingError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@rating_cmd.command(name="show")
@click.argument("name")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]))
def rating_show(name, fmt):
    """Show the rating for a snapshot."""
    entry = get_rating(name)
    if entry is None:
        click.echo(f"No rating set for '{name}'.")
        return
    if fmt == "json":
        click.echo(json.dumps({"snapshot": name, **entry}, indent=2))
    else:
        note_part = f" — {entry['note']}" if entry.get("note") else ""
        click.echo(f"{name}: {entry['score']}/5{note_part} (set {entry['timestamp']})")


@rating_cmd.command(name="remove")
@click.argument("name")
def rating_remove(name):
    """Remove the rating for a snapshot."""
    try:
        remove_rating(name)
        click.echo(f"Rating removed for '{name}'.")
    except KeyError:
        click.echo(f"No rating found for '{name}'.", err=True)
        raise SystemExit(1)


@rating_cmd.command(name="list")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]))
def rating_list(fmt):
    """List all rated snapshots."""
    ratings = list_ratings()
    if fmt == "json":
        click.echo(json.dumps(ratings, indent=2))
    else:
        if not ratings:
            click.echo("No ratings recorded.")
            return
        for snap_name, entry in sorted(ratings.items()):
            note_part = f" — {entry['note']}" if entry.get("note") else ""
            click.echo(f"{snap_name}: {entry['score']}/5{note_part}")
