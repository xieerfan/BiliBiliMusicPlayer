import click
from utils.banner import print_banner
from commands.setup import setup

@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """BiliBili-MusicPlayer 入口"""
    if ctx.invoked_subcommand is None:
        print_banner()
        click.echo(ctx.get_help())

# 注册子命令
cli.add_command(setup)

if __name__ == '__main__':
    cli()