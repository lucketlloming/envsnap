"""CLI commands for linting snapshots."""
import json
import click
from envsnap.lint import lint_snapshot, format_lint_report
from envsnap.storage import StorageError


@click.group("lint")
def lint_cmd():
    """Lint snapshots for potential issues."""


@lint_cmd.command("run")
@click.argument("name")
@click.option("--format", "fmt", type=click.Choice(["text", "json"]), default="text")
def lint_run(name: str, fmt: str):
    """Run lint checks on a snapshot."""
    try:
        issues = lint_snapshot(name)
    except StorageError as e:
        raise click.ClickException(str(e))

    if fmt == "json":
        click.echo(json.dumps({"snapshot": name, "issues": issues}, indent=2))
    else:
        click.echo(format_lint_report(name, issues))
    if any(i["severity"] == "warning" for i in issues):
        raise SystemExit(1)
