"""CLI commands for snapshot groups."""
import click
import json
from envsnap.group import add_to_group, remove_from_group, get_group, list_groups, delete_group


@click.group("group")
def group_cmd():
    """Manage snapshot groups."""


@group_cmd.command("add")
@click.argument("group")
@click.argument("snapshot")
def group_add(group, snapshot):
    """Add SNAPSHOT to GROUP."""
    try:
        add_to_group(group, snapshot)
        click.echo(f"Added '{snapshot}' to group '{group}'.")
    except KeyError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@group_cmd.command("remove")
@click.argument("group")
@click.argument("snapshot")
def group_remove(group, snapshot):
    """Remove SNAPSHOT from GROUP."""
    try:
        remove_from_group(group, snapshot)
        click.echo(f"Removed '{snapshot}' from group '{group}'.")
    except KeyError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@group_cmd.command("show")
@click.argument("group")
@click.option("--json", "as_json", is_flag=True)
def group_show(group, as_json):
    """Show members of GROUP."""
    try:
        members = get_group(group)
    except KeyError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)
    if as_json:
        click.echo(json.dumps({group: members}, indent=2))
    else:
        if not members:
            click.echo(f"Group '{group}' is empty.")
        for m in members:
            click.echo(f"  {m}")


@group_cmd.command("list")
@click.option("--json", "as_json", is_flag=True)
def group_list(as_json):
    """List all groups."""
    groups = list_groups()
    if as_json:
        click.echo(json.dumps(groups, indent=2))
    else:
        if not groups:
            click.echo("No groups defined.")
        for g in groups:
            click.echo(g)


@group_cmd.command("delete")
@click.argument("group")
def group_delete(group):
    """Delete GROUP entirely."""
    try:
        delete_group(group)
        click.echo(f"Deleted group '{group}'.")
    except KeyError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)
