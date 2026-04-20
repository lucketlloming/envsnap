"""Register dependency commands with the main CLI."""

from envsnap.cli_dependency import dependency_cmd


def register(cli):
    cli.add_command(dependency_cmd)
