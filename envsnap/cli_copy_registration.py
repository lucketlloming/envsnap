from envsnap.cli_copy import copy_cmd


def register(cli):
    cli.add_command(copy_cmd)
