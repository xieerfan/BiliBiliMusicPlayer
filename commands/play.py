import click
import json
import os
import asyncio
from core.player import play_audio_stream

CONFIG_PATH = os.path.expanduser("~/.config/BiliBiliMusicPlayer/config.json")

@click.command()
def play():
    if not os.path.exists(CONFIG_PATH): return
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    tracks = config.get("tracks", [])
    if not tracks: return
    
    total = len(tracks)
    while True:
        for index, track in enumerate(tracks):
            # 确保传入: 当前歌曲字典, 完整列表, 当前序号(1起), 总数
            asyncio.run(play_audio_stream(track, tracks, index + 1, total))