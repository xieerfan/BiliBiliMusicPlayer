import click
import json
import os
import asyncio
import random
from colorama import Fore
from core.player import play_audio_stream

CONFIG_PATH = os.path.expanduser("~/.config/BiliBiliMusicPlayer/config.json")

@click.command()
@click.option('--shuffle', is_flag=True, help="随机播放")
def play(shuffle):
    if not os.path.exists(CONFIG_PATH): return
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    tracks = config.get("tracks", [])
    if not tracks: return

    if shuffle: random.shuffle(tracks)
    
    total = len(tracks)
    while True:
        for index, track in enumerate(tracks):
            # 传入 3 个参数：track 字典, 当前序号 (index+1), 总数
            asyncio.run(play_audio_stream(track, index + 1, total))
        click.echo(Fore.YELLOW + "歌单循环结束，即将重新开始...")