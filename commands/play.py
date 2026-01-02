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
    config = load_config()
    tracks = config.get("tracks", [])
    lang = config.get("lang", "zh")
    
    if not tracks: return
    
    idx = 0
    while idx < len(tracks):
        # 获取播放状态返回值
        result = asyncio.run(play_audio_stream(tracks[idx], tracks, idx + 1, len(tracks), lang))
        
        if result == "exit":
            # 如果是 ESC 退出，直接跳出 while 循环返回终端
            break
        
        # 否则（自然播完或 Q 跳过）继续下一首
        idx += 1
        if idx >= len(tracks):
            idx = 0 # 列表循环