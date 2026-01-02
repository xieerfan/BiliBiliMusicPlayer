import subprocess
import os
from bilibili_api import video
from utils.banner import print_player_ui

async def play_audio_stream(track, all_tracks, index, total):
    v = video.Video(bvid=track['bvid'])
    try:
        os.system('clear')
        print_player_ui(track['title'], all_tracks, index, total)

        download_url_data = await v.get_download_url(page_index=0)
        # 获取音频流
        audio_url = download_url_data['dash']['audio'][0]['base_url'] if 'dash' in download_url_data else download_url_data['durl'][0]['url']
        
        cmd = [
            "mpv",
            audio_url,
            "--no-video",
            f"--referrer=https://www.bilibili.com/video/{track['bvid']}",
            "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "--force-window=no",
            "--msg-level=all=no", 
            "--input-terminal=yes"
        ]
        
        subprocess.run(cmd)

    except Exception as e:
        # 使用灰色的错误提示
        console.print(f"\n[#f38ba8]Error:[/] {e}")