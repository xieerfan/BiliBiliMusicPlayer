import click
import json
import os
from utils.banner import print_banner
from commands.setup import setup
from commands.play import play

CONFIG_DIR = os.path.expanduser("~/.config/BiliBiliMusicPlayer")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")

def set_language(lang_code):
    """保存语言设置到配置文件"""
    if not os.path.exists(CONFIG_DIR): os.makedirs(CONFIG_DIR)
    data = {"tracks": [], "lang": "zh"}
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    
    data["lang"] = "en" if lang_code.lower() == "en" else "zh"
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Language set to: {data['lang']}")

@click.group(invoke_without_command=True)
@click.option('--la', '-la', type=str, help="Set language: zh / en")
@click.pass_context
def cli(ctx, la):
    if la:
        set_language(la)
        return # 设置完语言后直接退出
    
    if ctx.invoked_subcommand is None:
        print_banner()
        click.echo(ctx.get_help())

# 这里把 setup 命令重命名为 setmain
cli.add_command(setup, name="setmain")
cli.add_command(play)

if __name__ == '__main__':
    cli()