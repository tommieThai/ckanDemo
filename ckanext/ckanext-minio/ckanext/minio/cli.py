import click


@click.group(short_help="minio CLI.")
def minio():
    """minio CLI.
    """
    pass


@minio.command()
@click.argument("name", default="minio")
def command(name):
    """Docs.
    """
    click.echo("Hello, {name}!".format(name=name))


def get_commands():
    return [minio]
