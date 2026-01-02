import subprocess
import asyncio
from bilibili_api import video, Credential
from colorama import Fore, Style

async def play_audio_stream(bvid, title):
    """
    获取音频流并调用 mpv 播放。
    支持按键：空格(暂停), q(下一首), 9/0(音量)
    """
    v = video.Video(bvid=bvid)
    
    try:
        # 获取视频的分 P 信息以拿到 cid
        # 即使单视频也需要这个步骤来防止 ArgsException
        download_url_data = await v.get_download_url(page_index=0)
        
        # 优先提取音频流 (DASH)
        if 'dash' in download_url_data:
            audio_url = download_url_data['dash']['audio'][0]['base_url']
        else:
            audio_url = download_url_data['durl'][0]['url']
        
        # 构造 mpv 命令
        # 去掉 stdout/stderr 的重定向，让 mpv 控制台可见
        cmd = [
            "mpv",
            audio_url,
            "--no-video",
            f"--referrer=https://www.bilibili.com/video/{bvid}",
            "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            f"--title=BiliPlayer - {title}",
            "--terminal=yes",
            "--force-window=no" # 确保不弹出黑窗口
        ]
        
        print(f"\n{Fore.MAGENTA}♪ 正在播放: {Fore.WHITE}{title}")
        print(f"{Fore.CYAN}操作: [空格]暂停 | [q]跳过/下一首 | [9/0]音量调整{Style.RESET_ALL}\n")
        
        # 运行 mpv。这里不使用 Popen，使用 run 会阻塞直到这首歌结束或被按 q
        subprocess.run(cmd)

    except Exception as e:
        print(f"\n{Fore.RED}播放 {title} 时出错: {e}")