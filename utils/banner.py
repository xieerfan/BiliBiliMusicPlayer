import random
import time
from rich.console import Console, Group
from rich.text import Text
from rich.table import Table
from rich.panel import Panel
from rich.progress_bar import ProgressBar
from rich.columns import Columns
from utils.i18n import get_text

console = Console()

def print_banner(lang="zh"):
    """
    支持响应式布局的 Banner
    大窗口时 BiliBili 和 MusicPlayer 并排，小窗口自动换行
    """
    # BiliBili 艺术字
    bili_art = r"""
  ____  _ _ _ 
 | __ )(_) (_)
 |  _ \| | | |
 | |_) | | | |
 |____/|_|_|_|"""

    # MusicPlayer 艺术字 (保持风格一致)
    music_art = r"""
  __  __ _      ____  _                      
 |  \/  | |    |  _ \| | __ _ _   _  ___ _ __ 
 | |\/| | |    | |_) | |/ _` | | | |/ _ \ '__|
 | |  | | |___ |  __/| | (_| | |_| |  __/ |   
 |_|  |_|_____||_|   |_|\__,_|\__, |\___|_|   
                              |___/           """

    # 创建两个渲染对象
    render_bili = Text(bili_art, style="#cba6f7")
    render_music = Text(music_art, style="#cba6f7")

    # 使用 Columns 实现响应式：在大终端它们会并排，小终端会自动折行
    # padding=(0, 2) 增加两个字间距
    console.print(Columns([render_bili, render_music], padding=(0, 2)))

    # 副标题
    status_str = "BILIBILI TERMINAL PLAYER" if lang == "en" else "哔哩哔哩终端播放器"
    console.print(f"\n{' ' * 4}[bold #6c7086]v1.0.0[/] | [italic #94e2d5]{status_str}[/]\n")

def get_huge_visualizer(width, height, is_paused=False):
    if height < 1: height = 1
    viz = Text()
    if is_paused:
        for _ in range(height - 1): viz.append(" \n")
        viz.append(" " * (width//2 - 5) + "P A U S E D" + "\n", style="#f38ba8")
        return viz
    heights = [random.randint(0, height) for _ in range(width)]
    for h in range(height, 0, -1):
        line = "".join("█" if ch >= h else ("▄" if ch == h-1 else " ") for ch in heights)
        viz.append(f"{line}\n", style="#cba6f7")
    return viz

def make_player_ui(current_track, tracks, index, total, start_time, is_paused=False, lang="zh"):
    tw, th = console.width, console.height
    
    # 状态头部
    header = Text()
    header.append(f"◉ {current_track[:tw-40]} ", style="bold #cba6f7")
    status_txt = get_text('paused' if is_paused else 'playing', lang).upper()
    header.append(f" {status_txt}", style="#f38ba8" if is_paused else "#a6e3a1")

    # 列表展示
    table = Table(show_header=False, box=None, padding=(0, 1), expand=True)
    table.add_column(width=4); table.add_column()
    list_rows = max(1, (th - 16) // 2) # 留出空间给大的 Banner
    start, end = max(0, index - 2), min(total, index + list_rows)
    for i in range(start, end):
        style = "bold black on #a6e3a1" if (i + 1) == index else "#6c7086"
        table.add_row(f"{i+1:02d}", tracks[i]['title'][:tw-15], style=style)

    # 底部进度条与频谱
    elapsed = int(time.time() - start_time)
    footer = Group(
        ProgressBar(total=240, completed=elapsed % 240, width=tw-20, complete_style="#cba6f7"),
        Text(f"{get_text('track_label', lang)} {index}/{total} | {get_text('time_label', lang)}: {elapsed//60:02d}:{elapsed%60:02d}", style="#6c7086"),
        get_huge_visualizer(tw-6, max(2, th - len(table.rows) - 14), is_paused)
    )

    return Panel(
        Group(header, Text("\n"), table, Text("\n"), footer), 
        border_style="#cba6f7", 
        height=th
    )