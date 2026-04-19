from envsnap.cli_remind import remind_cmd


def register(cli):
    cli.add_command(remind_cmd)
