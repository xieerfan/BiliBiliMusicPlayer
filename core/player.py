import subprocess
import os
import asyncio
import time
import sys
import select
import tty
import termios
import json
import socket
from bilibili_api import video
from rich.live import Live
from utils.banner import console, make_player_ui
from utils.i18n import get_text  # 导入翻译函数

# 定义 Socket 路径
SOCKET_PATH = "/tmp/BiliMLPalyer-socket"

def send_mpv_command(command_list):
    """通过 Unix Socket 发送 JSON 指令控制 mpv"""
    try:
        if not os.path.exists(SOCKET_PATH): return
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.settimeout(0.2)
        client.connect(SOCKET_PATH)
        msg = {"command": command_list}
        client.send(json.dumps(msg).encode() + b"\n")
        client.close()
    except:
        pass

def check_stdin():
    """非阻塞读取标准输入"""
    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        return sys.stdin.read(1)
    return None

async def play_audio_stream(track, all_tracks, index, total, lang="zh"):
    """
    播放核心逻辑
    返回状态: "next" (自然结束), "skip" (Q跳过), "exit" (ESC退出)
    """
    v = video.Video(bvid=track['bvid'])
    start_time = time.time()
    pause_time_sum = 0
    last_pause_start = 0
    status = "next" 
    is_paused = False
    
    # 清理旧的 Socket 
    if os.path.exists(SOCKET_PATH): os.remove(SOCKET_PATH)
    
    try:
        # 获取 B 站音频流地址
        data = await v.get_download_url(page_index=0)
        url = data['dash']['audio'][0]['base_url'] if 'dash' in data else data['durl'][0]['url']
        
        # 启动 mpv 
        proc = subprocess.Popen(
            ["mpv", url, "--no-video", "--msg-level=all=no", f"--input-ipc-server={SOCKET_PATH}"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

        # 终端进入原始模式以捕获按键
        old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())

        try:
            with Live(console=console, refresh_per_second=10, screen=True) as live:
                while proc.poll() is None:
                    # 计算进度条时间（考虑暂停补偿）
                    if is_paused:
                        v_start = time.time() - (last_pause_start - start_time - pause_time_sum)
                    else:
                        v_start = start_time + pause_time_sum

                    # 渲染 UI
                    live.update(make_player_ui(track['title'], all_tracks, index, total, v_start, is_paused, lang))
                    
                    key = check_stdin()
                    if key:
                        # 1. ESC 退出 (\x1b)
                        if key == '\x1b':
                            status = "exit"
                            break
                        
                        k = key.lower()
                        # 2. Q 跳过
                        if k == 'q':
                            status = "skip"
                            break
                        # 3. 空格 暂停
                        elif k in (' ', '\x20'):
                            is_paused = not is_paused
                            send_mpv_command(["set_property", "pause", is_paused])
                            
                            if is_paused:
                                last_pause_start = time.time()
                            else:
                                pause_time_sum += (time.time() - last_pause_start)
                    
                    await asyncio.sleep(0.05)
        finally:
            # 恢复终端设置
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            if proc:
                proc.terminate()
                proc.wait()
            if os.path.exists(SOCKET_PATH): os.remove(SOCKET_PATH)

    except Exception as e:
        console.print(f"[#f38ba8]Error:[/] {e}")
        await asyncio.sleep(1)
        
    return status