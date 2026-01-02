import random
import time
from rich.console import Console, Group
from rich.text import Text
from rich.table import Table
from rich.panel import Panel
from rich.progress_bar import ProgressBar
from utils.i18n import get_text

console = Console()

def print_banner(lang="zh"):
    art = r"""
  ____  _ _ _ ____  _ _ _ 
 | __ )(_) (_) __ )(_) (_)
 |  _ \| | | |  _ \| | | |
 | |_) | | | | |_) | | | |
 |____/|_|_|_|____/|_|_|_|"""
    console.print(art, style="#cba6f7")
    status_str = "BILIBILI TERMINAL PLAYER" if lang == "en" else "哔哩哔哩终端播放器"
    console.print(f"{' ' * 4}[bold #6c7086]v1.0.0[/] | [italic #94e2d5]{status_str}[/]\n")

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
    header = Text()
    header.append(f"◉ {current_track[:tw-35]} ", style="bold #cba6f7")
    
    # 修复乱码的关键：使用 style 参数而不是在字符串里写 []
    status_txt = get_text('paused' if is_paused else 'playing', lang).upper()
    header.append(f" {status_txt}", style="#f38ba8" if is_paused else "#a6e3a1")

    table = Table(show_header=False, box=None, padding=(0, 1), expand=True)
    table.add_column(width=4); table.add_column()
    list_rows = max(1, (th - 14) // 2)
    start, end = max(0, index - 2), min(total, index + list_rows)
    for i in range(start, end):
        style = "bold black on #a6e3a1" if (i + 1) == index else "#6c7086"
        table.add_row(f"{i+1:02d}", tracks[i]['title'][:tw-15], style=style)

    elapsed = int(time.time() - start_time)
    footer = Group(
        ProgressBar(total=240, completed=elapsed % 240, width=tw-20, complete_style="#cba6f7"),
        Text(f"{get_text('track_label', lang)} {index}/{total} | {get_text('time_label', lang)}: {elapsed//60:02d}:{elapsed%60:02d}", style="#6c7086"),
        get_huge_visualizer(tw-6, max(2, th - len(table.rows) - 12), is_paused)
    )

    return Panel(Group(header, Text("\n"), table, Text("\n"), footer), border_style="#cba6f7", height=th)