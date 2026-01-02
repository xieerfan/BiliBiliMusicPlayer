import subprocess
import os
import asyncio
import time
from bilibili_api import video
from rich.live import Live
from utils.banner import console, make_player_layout

async def play_audio_stream(track, all_tracks, index, total):
    v = video.Video(bvid=track['bvid'])
    proc = None
    try:
        # 1. 真正的获取音频逻辑
        download_url_data = await v.get_download_url(page_index=0)
        audio_url = download_url_data['dash']['audio'][0]['base_url'] if 'dash' in download_url_data else download_url_data['durl'][0]['url']
        
        # 2. 静默启动 mpv
        cmd = [
            "mpv", audio_url, "--no-video",
            f"--referrer=https://www.bilibili.com/video/{track['bvid']}",
            "--msg-level=all=no", "--input-terminal=yes"
        ]
        
        # 使用 Popen 方便我们随时杀掉它
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # 3. 实时渲染界面
        os.system('clear')
        with Live(console=console, refresh_per_second=12, transient=True) as live:
            while proc.poll() is None:
                live.update(make_player_layout(track['title'], all_tracks, index, total))
                await asyncio.sleep(0.08)

    except Exception as e:
        console.print(f"\n[#f38ba8]Error:[/] {e}")
        await asyncio.sleep(2)
    finally:
        # 4. 关键：确保函数退出时杀死当前 mpv 进程，防止叠加播放
        if proc:
            proc.terminate()
            proc.wait()