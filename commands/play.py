import click
import json
import os
import asyncio
from core.player import play_audio_stream

@click.command()
def play():
    cfg_path = os.path.expanduser("~/.config/BiliBiliMusicPlayer/config.json")
    if not os.path.exists(cfg_path): return
    with open(cfg_path, "r", encoding="utf-8") as f:
        tracks = json.load(f).get("tracks", [])
    
    if not tracks: return
    
    idx = 0
    while idx < len(tracks):
        # 每次只运行一个协程，确保顺序执行
        asyncio.run(play_audio_stream(tracks[idx], tracks, idx + 1, len(tracks)))
        idx += 1
        if idx >= len(tracks): idx = 0 # 列表循环