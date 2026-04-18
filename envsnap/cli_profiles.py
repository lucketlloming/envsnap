"""CLI commands for profile management."""

from __future__ import annotations

import click

from envsnap import profiles
from envsnap.storage import list_snapshots


@click.group("profile")
def profile_cmd():
    """Manage snapshot profiles."""


@profile_cmd.command("add")
@click.argument("profile")
@click.argument("snapshot")
def profile_add(profile: str, snapshot: str):
    """Add SNAPSHOT to PROFILE."""
    if snapshot not in list_snapshots():
        raise click.ClickException(f"Snapshot '{snapshot}' not found.")
    profiles.add_to_profile(profile, snapshot)
    click.echo(f"Added '{snapshot}' to profile '{profile}'.")


@profile_cmd.command("remove")
@click.argument("profile")
@click.argument("snapshot")
def profile_remove(profile: str, snapshot: str):
    """Remove SNAPSHOT from PROFILE."""
    profiles.remove_from_profile(profile, snapshot)
    click.echo(f"Removed '{snapshot}' from profile '{profile}'.")


@profile_cmd.command("list")
@click.argument("profile", required=False)
def profile_list(profile: str | None):
    """List profiles or snapshots within a PROFILE."""
    if profile:
        snaps = profiles.get_profile(profile)
        if not snaps:
            click.echo(f"Profile '{profile}' is empty or does not exist.")
        for s in snaps:
            click.echo(s)
    else:
        all_profiles = profiles.list_profiles()
        if not all_profiles:
            click.echo("No profiles defined.")
        for p in all_profiles:
            click.echo(p)


@profile_cmd.command("delete")
@click.argument("profile")
def profile_delete(profile: str):
    """Delete an entire PROFILE."""
    profiles.delete_profile(profile)
    click.echo(f"Deleted profile '{profile}'.")
