"""CLI commands for workflow management."""
from __future__ import annotations

import json

import click

from envsnap.workflow import (
    WorkflowNotFoundError,
    SnapshotNotFoundError,
    create_workflow,
    get_workflow,
    delete_workflow,
    list_workflows,
    append_step,
)


@click.group(name="workflow")
def workflow_cmd():
    """Manage ordered snapshot workflows."""


@workflow_cmd.command("create")
@click.argument("name")
@click.argument("steps", nargs=-1, required=True)
@click.option("--description", "-d", default="", help="Optional description.")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]))
def workflow_create(name, steps, description, fmt):
    """Create a workflow NAME with ordered STEPS (snapshot names)."""
    try:
        create_workflow(name, list(steps), description or None)
    except SnapshotNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
    if fmt == "json":
        click.echo(json.dumps({"workflow": name, "steps": list(steps)}))
    else:
        click.echo(f"Workflow '{name}' created with {len(steps)} step(s).")


@workflow_cmd.command("show")
@click.argument("name")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]))
def workflow_show(name, fmt):
    """Show steps in workflow NAME."""
    try:
        wf = get_workflow(name)
    except WorkflowNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
    if fmt == "json":
        click.echo(json.dumps({"name": name, **wf}))
    else:
        desc = wf["description"]
        if desc:
            click.echo(f"Workflow: {name}  ({desc})")
        else:
            click.echo(f"Workflow: {name}")
        for i, step in enumerate(wf["steps"], 1):
            click.echo(f"  {i}. {step}")


@workflow_cmd.command("list")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]))
def workflow_list(fmt):
    """List all workflows."""
    names = list_workflows()
    if fmt == "json":
        click.echo(json.dumps(names))
    else:
        if not names:
            click.echo("No workflows defined.")
        for n in names:
            click.echo(n)


@workflow_cmd.command("delete")
@click.argument("name")
def workflow_delete(name):
    """Delete workflow NAME."""
    try:
        delete_workflow(name)
    except WorkflowNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
    click.echo(f"Workflow '{name}' deleted.")


@workflow_cmd.command("append")
@click.argument("name")
@click.argument("snapshot")
def workflow_append(name, snapshot):
    """Append SNAPSHOT as the next step in workflow NAME."""
    try:
        append_step(name, snapshot)
    except (WorkflowNotFoundError, SnapshotNotFoundError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
    click.echo(f"Appended '{snapshot}' to workflow '{name}'.")
