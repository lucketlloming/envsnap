"""CLI commands for snapshot templates."""
import json
import click
from envsnap.template import save_template, get_template, list_templates, delete_template, apply_template


@click.group("template")
def template_cmd():
    """Manage snapshot templates."""


@template_cmd.command("save")
@click.argument("name")
@click.argument("keys", nargs=-1, required=True)
@click.option("--default", "defaults", multiple=True, metavar="KEY=VALUE",
              help="Default value for a key (repeatable).")
def template_save(name, keys, defaults):
    """Save a template with expected KEYS."""
    parsed = {}
    for d in defaults:
        if "=" not in d:
            raise click.BadParameter(f"Expected KEY=VALUE, got: {d}")
        k, v = d.split("=", 1)
        parsed[k] = v
    save_template(name, list(keys), parsed)
    click.echo(f"Template '{name}' saved with keys: {', '.join(keys)}")


@template_cmd.command("show")
@click.argument("name")
@click.option("--json", "as_json", is_flag=True)
def template_show(name, as_json):
    """Show a template's keys and defaults."""
    try:
        t = get_template(name)
    except KeyError as e:
        raise click.ClickException(str(e))
    if as_json:
        click.echo(json.dumps(t, indent=2))
    else:
        click.echo(f"Keys: {', '.join(t['keys'])}")
        if t["defaults"]:
            click.echo("Defaults:")
            for k, v in t["defaults"].items():
                click.echo(f"  {k}={v}")


@template_cmd.command("list")
def template_list():
    """List all saved templates."""
    names = list_templates()
    if not names:
        click.echo("No templates saved.")
    else:
        for n in names:
            click.echo(n)


@template_cmd.command("delete")
@click.argument("name")
def template_delete(name):
    """Delete a template."""
    try:
        delete_template(name)
        click.echo(f"Template '{name}' deleted.")
    except KeyError as e:
        raise click.ClickException(str(e))


@template_cmd.command("apply")
@click.argument("name")
@click.option("--set", "overrides", multiple=True, metavar="KEY=VALUE")
def template_apply(name, overrides):
    """Print env vars from template, optionally overriding defaults."""
    parsed = {}
    for o in overrides:
        if "=" not in o:
            raise click.BadParameter(f"Expected KEY=VALUE, got: {o}")
        k, v = o.split("=", 1)
        parsed[k] = v
    try:
        result = apply_template(name, parsed or None)
    except KeyError as e:
        raise click.ClickException(str(e))
    for k, v in result.items():
        click.echo(f"{k}={v}")
