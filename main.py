import click
from utils.banner import print_banner
from commands.setup import setup
from commands.play import play

@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        print_banner()
        click.echo(ctx.get_help())

cli.add_command(setup)
cli.add_command(play)

if __name__ == '__main__':
    cli()