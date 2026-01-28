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
from utils.i18n import get_text
from core.mpris_controller import MPRISController

# 定义 Socket 路径
SOCKET_PATH = "/tmp/BiliMLPalyer-socket"


class PlayerCallbackHandler:
    """
    播放器回调处理器
    用于响应 MPRIS 控制命令
    """
    
    def __init__(self):
        self.current_command = None
        self.is_paused = False
        self.should_exit = False
        self.should_skip = False
        self.should_previous = False
    
    def play_pause(self):
        """播放/暂停切换"""
        self.current_command = 'toggle_pause'
        self.is_paused = not self.is_paused
        return "Paused" if self.is_paused else "Playing"
    
    def play(self):
        """播放"""
        if self.is_paused:
            self.current_command = 'toggle_pause'
            self.is_paused = False
    
    def pause(self):
        """暂停"""
        if not self.is_paused:
            self.current_command = 'toggle_pause'
            self.is_paused = True
    
    def stop(self):
        """停止"""
        self.should_exit = True
    
    def next(self):
        """下一曲"""
        self.should_skip = True
    
    def previous(self):
        """上一曲"""
        self.should_previous = True
    
    def quit(self):
        """退出播放器"""
        self.should_exit = True


def send_mpv_command(command_list):
    """通过 Unix Socket 发送 JSON 指令控制 mpv"""
    try:
        if not os.path.exists(SOCKET_PATH):
            return None
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.settimeout(0.5)
        client.connect(SOCKET_PATH)
        msg = {"command": command_list}
        client.send(json.dumps(msg).encode() + b"\n")
        
        # 接收响应
        response = b""
        while True:
            chunk = client.recv(1024)
            if not chunk:
                break
            response += chunk
            if b'\n' in response:
                break
        
        client.close()
        
        if response:
            return json.loads(response.decode().strip())
        return None
    except:
        return None


def check_stdin():
    """非阻塞读取标准输入"""
    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        return sys.stdin.read(1)
    return None


async def get_video_duration(bvid):
    """获取视频实际时长（秒）"""
    try:
        v = video.Video(bvid=bvid)
        info = await v.get_info()
        # B站返回的 duration 是秒
        duration = info.get('duration', 240)
        return duration
    except Exception as e:
        console.print(f"[yellow]⚠ 获取时长失败: {e}, 使用默认值[/yellow]")
        return 240


async def play_audio_stream(track, all_tracks, index, total, lang="zh", mpris_controller=None, callback_handler=None):
    """
    播放核心逻辑（集成 MPRIS 支持）
    
    返回状态: 
        "next" (自然结束)
        "skip" (Q跳过/MPRIS下一曲)
        "previous" (上一曲)
        "exit" (ESC退出/MPRIS停止)
    """
    v = video.Video(bvid=track['bvid'])
    status = "next"
    is_paused = False
    
    # 清理旧的 Socket
    if os.path.exists(SOCKET_PATH):
        os.remove(SOCKET_PATH)
    
    proc = None
    
    try:
        # 获取 B 站音频流地址
        data = await v.get_download_url(page_index=0)
        url = data['dash']['audio'][0]['base_url'] if 'dash' in data else data['durl'][0]['url']
        
        # 获取视频实际时长
        video_duration = await get_video_duration(track['bvid'])
        
        # 更新 MPRIS 元数据
        if mpris_controller:
            track_info = {
                'id': track['bvid'],
                'title': track['title'],
                'artist': 'BiliBili',
                'album': 'BiliBili Music',
                'length': video_duration,  # 使用实际时长
                'url': f"https://www.bilibili.com/video/{track['bvid']}"
            }
            mpris_controller.update_track(track_info)
            mpris_controller.update_status("Playing")
        
        # 启动 mpv
        proc = subprocess.Popen(
            ["mpv", url, "--no-video", "--msg-level=all=no", f"--input-ipc-server={SOCKET_PATH}"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # 等待 Socket 文件创建
        socket_ready = False
        for _ in range(20):  # 最多等待 2 秒
            if os.path.exists(SOCKET_PATH):
                socket_ready = True
                break
            await asyncio.sleep(0.1)
        
        if not socket_ready:
            console.print("[red]✗ MPV Socket 初始化失败[/red]")
            return "skip"
        
        # 记录播放开始时间（用于 UI 显示）
        ui_start_time = time.time()
        pause_time_sum = 0
        last_pause_start = 0
        
        # 终端进入原始模式以捕获按键
        old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())
        
        try:
            with Live(console=console, refresh_per_second=10, screen=True) as live:
                while True:
                    # 检查 mpv 进程是否还在运行
                    if proc.poll() is not None:
                        # mpv 进程已结束，自然播放完成
                        status = "next"
                        break
                    
                    # 检查 MPRIS 命令
                    if callback_handler:
                        # 处理播放/暂停
                        if callback_handler.current_command == 'toggle_pause':
                            is_paused = not is_paused
                            send_mpv_command(["set_property", "pause", is_paused])
                            
                            if is_paused:
                                last_pause_start = time.time()
                                if mpris_controller:
                                    mpris_controller.update_status("Paused")
                            else:
                                pause_time_sum += (time.time() - last_pause_start)
                                if mpris_controller:
                                    mpris_controller.update_status("Playing")
                            
                            callback_handler.current_command = None
                        
                        # 处理下一曲
                        if callback_handler.should_skip:
                            status = "skip"
                            break
                        
                        # 处理上一曲
                        if callback_handler.should_previous:
                            status = "previous"
                            break
                        
                        # 处理退出
                        if callback_handler.should_exit:
                            status = "exit"
                            break
                    
                    # 获取 mpv 实际播放位置
                    response = send_mpv_command(["get_property", "time-pos"])
                    current_time = 0
                    
                    if response and response.get("error") == "success":
                        current_time = response.get("data", 0)
                    else:
                        # 降级：使用计算的时间
                        if is_paused:
                            current_time = last_pause_start - ui_start_time - pause_time_sum
                        else:
                            current_time = time.time() - ui_start_time - pause_time_sum
                    
                    # 限制显示时间不超过总时长
                    current_time = max(0, min(current_time, video_duration))
                    
                    # 计算用于 UI 显示的虚拟开始时间
                    v_start = time.time() - current_time
                    
                    # 更新 MPRIS 播放位置
                    if mpris_controller and not is_paused:
                        mpris_controller.update_position(current_time)
                    
                    # 渲染 UI
                    live.update(make_player_ui(
                        track['title'], 
                        all_tracks, 
                        index, 
                        total, 
                        v_start, 
                        is_paused, 
                        lang
                    ))
                    
                    # 检查键盘输入
                    key = check_stdin()
                    if key:
                        # ESC 退出
                        if key == '\x1b':
                            status = "exit"
                            break
                        
                        k = key.lower()
                        
                        # Q 跳过
                        if k == 'q':
                            status = "skip"
                            break
                        
                        # P 上一曲
                        elif k == 'p':
                            status = "previous"
                            break
                        
                        # 空格 暂停
                        elif k in (' ', '\x20'):
                            is_paused = not is_paused
                            send_mpv_command(["set_property", "pause", is_paused])
                            
                            if is_paused:
                                last_pause_start = time.time()
                                if mpris_controller:
                                    mpris_controller.update_status("Paused")
                            else:
                                pause_time_sum += (time.time() - last_pause_start)
                                if mpris_controller:
                                    mpris_controller.update_status("Playing")
                    
                    await asyncio.sleep(0.05)
        
        finally:
            # 恢复终端设置
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    
    except Exception as e:
        console.print(f"[#f38ba8]Error:[/] {e}")
        await asyncio.sleep(1)
        status = "skip"
    
    finally:
        # 清理进程和 Socket
        if proc and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                proc.kill()
        
        if os.path.exists(SOCKET_PATH):
            try:
                os.remove(SOCKET_PATH)
            except:
                pass
    
    return status