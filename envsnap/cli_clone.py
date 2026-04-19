import click
from envsnap.clone import clone_snapshot, SnapshotNotFoundError, SnapshotAlreadyExistsError


@click.group("clone")
def clone_cmd():
    """Clone snapshots."""


@clone_cmd.command("run")
@click.argument("source")
@click.argument("destination")
@click.option("--set", "overrides", multiple=True, metavar="KEY=VALUE",
              help="Override specific keys in the clone.")
@click.option("--force", is_flag=True, default=False,
              help="Overwrite destination if it already exists.")
def clone_run(source, destination, overrides, force):
    """Clone SOURCE snapshot into DESTINATION.

    Optionally override specific keys with --set KEY=VALUE.
    """
    parsed_overrides = {}
    for item in overrides:
        if "=" not in item:
            click.echo(f"Invalid override '{item}': expected KEY=VALUE format.", err=True)
            raise SystemExit(1)
        k, v = item.split("=", 1)
        parsed_overrides[k] = v

    try:
        clone_snapshot(
            source,
            destination,
            overrides=parsed_overrides if parsed_overrides else None,
            overwrite=force,
        )
        click.echo(f"Cloned '{source}' → '{destination}'.")
        if parsed_overrides:
            for k, v in parsed_overrides.items():
                click.echo(f"  override: {k}={v}")
    except SnapshotNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
    except SnapshotAlreadyExistsError as exc:
        click.echo(f"Error: {exc}  Use --force to overwrite.", err=True)
        raise SystemExit(1)
