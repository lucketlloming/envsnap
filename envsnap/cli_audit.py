"""CLI commands for the audit log feature."""
import json
import click
from envsnap.audit import get_audit, clear_audit


@click.group("audit")
def audit_cmd():
    """View and manage the audit log."""


@audit_cmd.command("log")
@click.argument("snapshot", required=False)
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]), show_default=True)
def audit_log(snapshot, fmt):
    """Show audit entries, optionally for a specific SNAPSHOT."""
    entries = get_audit(snapshot=snapshot)
    if not entries:
        click.echo("No audit entries found.")
        return
    if fmt == "json":
        click.echo(json.dumps(entries, indent=2))
    else:
        for e in entries:
            detail = f" ({e['detail']})" if e.get("detail") else ""
            click.echo(f"{e['timestamp']}  {e['action']:10s}  {e['snapshot']}  [{e['user']}]{detail}")


@audit_cmd.command("clear")
@click.argument("snapshot", required=False)
@click.option("--yes", is_flag=True, help="Skip confirmation.")
def audit_clear(snapshot, yes):
    """Clear audit entries. Optionally limit to a specific SNAPSHOT."""
    target = snapshot or "ALL snapshots"
    if not yes:
        click.confirm(f"Clear audit log for {target}?", abort=True)
    removed = clear_audit(snapshot=snapshot)
    click.echo(f"Removed {removed} audit entry/entries.")
