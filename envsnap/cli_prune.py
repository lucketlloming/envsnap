"""CLI commands for pruning snapshots."""
import click
from envsnap.prune import prune_by_age, prune_by_count, PruneError


@click.group("prune")
def prune_cmd():
    """Prune old or excess snapshots."""


@prune_cmd.command("age")
@click.argument("max_age_days", type=float)
@click.option("--dry-run", is_flag=True, help="Show what would be pruned without deleting.")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
def prune_age(max_age_days: float, dry_run: bool, as_json: bool):
    """Delete snapshots older than MAX_AGE_DAYS days."""
    pruned = prune_by_age(max_age_days=max_age_days, dry_run=dry_run)
    _output(pruned, dry_run, as_json)


@prune_cmd.command("count")
@click.argument("keep", type=int)
@click.option("--dry-run", is_flag=True, help="Show what would be pruned without deleting.")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
def prune_count(keep: int, dry_run: bool, as_json: bool):
    """Keep only the KEEP most recent snapshots, pruning the rest."""
    try:
        pruned = prune_by_count(keep=keep, dry_run=dry_run)
    except PruneError as exc:
        raise click.ClickException(str(exc))
    _output(pruned, dry_run, as_json)


def _output(pruned: list[str], dry_run: bool, as_json: bool):
    import json as _json
    label = "Would prune" if dry_run else "Pruned"
    if as_json:
        click.echo(_json.dumps({"pruned": pruned, "dry_run": dry_run}))
    else:
        if not pruned:
            click.echo("Nothing to prune.")
        else:
            for name in pruned:
                click.echo(f"{label}: {name}")
