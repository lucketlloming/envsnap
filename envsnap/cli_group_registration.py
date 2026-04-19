"""Register group commands with the main CLI."""
from envsnap.cli_group import group_cmd


def register(cli):
    cli.add_command(group_cmd)
