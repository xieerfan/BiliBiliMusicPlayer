# core/player.py 修复版

import subprocess
import os
from bilibili_api import video
from utils.banner import print_player_ui

async def play_audio_stream(track, index, total):
    bvid = track['bvid']
    title = track['title']
    v = video.Video(bvid=bvid)
    
    try:
        os.system('clear')
        print_player_ui(title, total, index)

        download_url_data = await v.get_download_url(page_index=0)
        
        if 'dash' in download_url_data:
            audio_url = download_url_data['dash']['audio'][0]['base_url']
        else:
            audio_url = download_url_data['durl'][0]['url']
        
        # 优化后的命令
        cmd = [
            "mpv",
            audio_url,
            "--no-video",
            f"--referrer=https://www.bilibili.com/video/{bvid}",
            "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "--force-window=no",
            # 关键修改：不再使用 --no-terminal，而是屏蔽所有输出等级
            "--msg-level=all=no", 
            # 强制启用控制台快捷键
            "--input-terminal=yes",
            # 设置标题（部分终端顶栏可见）
            f"--title=BiliPlayer - {title}"
        ]
        
        # 使用 subprocess.run，不重定向 stdin/stdout
        # 这样键盘信号才能直接穿透 Python 传递给 mpv
        subprocess.run(cmd)

    except Exception as e:
        print(f"\n播放出错: {e}")