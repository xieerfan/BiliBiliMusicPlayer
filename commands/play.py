import click
import json
import os
import asyncio
from colorama import Fore
from utils.banner import print_banner
from core.player import play_audio_stream

CONFIG_PATH = os.path.expanduser("~/.config/BiliBiliMusicPlayer/config.json")

@click.command()
@click.option('--shuffle', is_flag=True, help="随机播放模式")
def play(shuffle):
    """开始循环播放歌单喵！"""
    if not os.path.exists(CONFIG_PATH):
        click.echo(Fore.RED + "找不到歌单文件，请先运行 setup 添加音乐喵！")
        return
        
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    tracks = config.get("tracks", [])
    if not tracks:
        click.echo(Fore.RED + "歌单是空的，快去添加吧！")
        return

    import random
    if shuffle:
        random.shuffle(tracks)
        click.echo(Fore.YELLOW + ">> 已开启随机播放模式")

    print_banner()
    click.echo(f"{Fore.GREEN}共加载 {len(tracks)} 首歌曲，准备开始巡演！")

    # 无限循环播放列表
    while True:
        for index, track in enumerate(tracks):
            # 这里的 asyncio.run 会等待一首歌播完（或被按 q 结束）
            asyncio.run(play_audio_stream(track['bvid'], track['title']))
            
            # 可以在这里加个小小的检测，比如按了 Ctrl+C 彻底退出
            # 否则它会一直循环列表下去
        
        click.echo(Fore.YELLOW + "\n>> 歌单播完一遍啦，即将重新开始...")