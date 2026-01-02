import click
import json
import os
import asyncio
# 确保导入 json 喵！
from core.player import play_audio_stream

def load_config():
    cfg_path = os.path.expanduser("~/.config/BiliBiliMusicPlayer/config.json")
    if os.path.exists(cfg_path):
        with open(cfg_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"tracks": [], "lang": "zh"}

@click.command()
def play():
    """开始播放 (支持多语言环境)"""
    config = load_config()
    tracks = config.get("tracks", [])
    lang = config.get("lang", "zh") # 获取你在 -la 里设置的语言
    
    if not tracks:
        # 这里可以加个小提示
        from utils.i18n import get_text
        from utils.banner import console
        console.print(f" [#f38ba8]{get_text('empty', lang)}[/]")
        return
    
    idx = 0
    while idx < len(tracks):
        # 核心改动：把 lang 传给播放流，这样 UI 渲染时就能用 get_text 了
        # 注意：这里需要确保你的 core/player.py 里的 play_audio_stream 接收 lang 参数
        result = asyncio.run(play_audio_stream(tracks[idx], tracks, idx + 1, len(tracks), lang))
        
        idx += 1
        if idx >= len(tracks):
            idx = 0 # 列表循环