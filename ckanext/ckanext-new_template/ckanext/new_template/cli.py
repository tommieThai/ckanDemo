import click


@click.group(short_help="new_template CLI.")
def new_template():
    """new_template CLI.
    """
    pass


@new_template.command()
@click.argument("name", default="new_template")
def command(name):
    """Docs.
    """
    click.echo("Hello, {name}!".format(name=name))


def get_commands():
    return [new_template]
