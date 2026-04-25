"""CLI commands for patching (set/unset) keys in an existing snapshot."""

import click
from .patch import patch_snapshot, set_key, unset_key, SnapshotNotFoundError


@click.group("patch", help="Set or unset individual keys in a snapshot.")
def patch_cmd():
    pass


def _parse_key_value_pairs(pairs: tuple) -> dict:
    """Parse an iterable of 'KEY=VALUE' strings into a dictionary.

    Raises click.BadParameter if any pair is not in KEY=VALUE format.
    """
    updates = {}
    for pair in pairs:
        if "=" not in pair:
            raise click.BadParameter(
                f"Expected KEY=VALUE format, got: {pair!r}",
                param_hint="pairs",
            )
        k, v = pair.split("=", 1)
        updates[k] = v
    return updates


@patch_cmd.command("set", help="Set one or more KEY=VALUE pairs in a snapshot.")
@click.argument("name")
@click.argument("pairs", nargs=-1, required=True, metavar="KEY=VALUE...")
def patch_set(name: str, pairs: tuple):
    """Set KEY=VALUE pairs in snapshot NAME."""
    updates = _parse_key_value_pairs(pairs)

    try:
        changed = patch_snapshot(name, set_keys=updates)
    except SnapshotNotFoundError as exc:
        raise click.ClickException(str(exc))

    if changed:
        click.echo(f"Updated {len(changed)} key(s) in '{name}': {', '.join(changed)}")
    else:
        click.echo(f"No keys were changed in '{name}'.")


@patch_cmd.command("unset", help="Remove one or more keys from a snapshot.")
@click.argument("name")
@click.argument("keys", nargs=-1, required=True, metavar="KEY...")
def patch_unset(name: str, keys: tuple):
    """Remove KEYS from snapshot NAME."""
    try:
        removed = patch_snapshot(name, unset_keys=list(keys))
    except SnapshotNotFoundError as exc:
        raise click.ClickException(str(exc))

    if removed:
        click.echo(f"Removed {len(removed)} key(s) from '{name}': {', '.join(removed)}")
    else:
        click.echo(f"None of the specified keys were found in '{name}'.")
