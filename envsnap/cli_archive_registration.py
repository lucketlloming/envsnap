"""Register archive commands with the root CLI."""

from envsnap.cli_archive import archive_cmd


def register(cli):
    cli.add_command(archive_cmd)
