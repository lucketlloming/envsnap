"""CLI commands for snapshot comparison."""

import click
from envsnap.compare import compare_snapshots, format_compare_report
from envsnap.storage import load_snapshot


@click.command(name="compare")
@click.argument("snapshot_a")
@click.argument("snapshot_b")
@click.option("--json", "as_json", is_flag=True, default=False, help="Output as JSON")
@click.option("--exit-code", is_flag=True, default=False, help="Exit with code 1 if differences found")
def compare_cmd(snapshot_a: str, snapshot_b: str, as_json: bool, exit_code: bool) -> None:
    """Compare two snapshots and show differences."""
    try:
        result = compare_snapshots(snapshot_a, snapshot_b)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc))

    if as_json:
        import json
        click.echo(json.dumps(result, indent=2))
    else:
        report = format_compare_report(snapshot_a, snapshot_b, result)
        click.echo(report)

    if exit_code and any(result.get(key) for key in ("added", "removed", "changed")):
        raise SystemExit(1)
