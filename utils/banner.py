import random
import time
from rich.console import Console, Group
from rich.text import Text
from rich.table import Table
from rich.panel import Panel
from rich.progress_bar import ProgressBar

console = Console()

def print_banner():
    art = r"""
  ____  _ _ _ ____  _ _ _ 
 | __ )(_) (_) __ )(_) (_)
 |  _ \| | | |  _ \| | | |
 | |_) | | | | |_) | | | |
 |____/|_|_|_|____/|_|_|_|"""
    console.print(art, style="#cba6f7")

def get_huge_visualizer(width, height, is_paused=False):
    if height < 1: height = 1
    viz = Text()
    if is_paused:
        for _ in range(height - 1): viz.append(" \n")
        viz.append(" " + "▃" * (width-2) + "\n", style="#f38ba8")
        return viz
    
    heights = [random.randint(0, height) for _ in range(width)]
    for h in range(height, 0, -1):
        line = "".join("█" if ch >= h else ("▄" if ch == h-1 else " ") for ch in heights)
        viz.append(f"{line}\n", style="#cba6f7")
    return viz

def make_player_ui(current_track, tracks, index, total, start_time, is_paused=False):
    tw, th = console.width, console.height
    
    # --- 修复标题渲染的核心逻辑 ---
    header = Text()
    header.append(f"◉ {current_track[:tw-35]} ", style="bold #cba6f7")
    if is_paused:
        header.append("⏸ PAUSED", style="#f38ba8")
    else:
        header.append("▶ PLAYING", style="#a6e3a1")
    # ----------------------------

    list_prog = ProgressBar(total=total, completed=index, width=tw//3, complete_style="#cba6f7")
    
    table = Table(show_header=False, box=None, padding=(0, 1), expand=True)
    table.add_column(width=4); table.add_column()
    list_rows = max(1, (th - 14) // 2)
    start, end = max(0, index - 1), min(total, index + list_rows)
    for i in range(start, end):
        style = "bold black on #a6e3a1" if (i + 1) == index else "#6c7086"
        table.add_row(f"{i+1:02d}", tracks[i]['title'][:tw-15], style=style)

    elapsed = int(time.time() - start_time)
    song_prog = ProgressBar(total=240, completed=elapsed % 240, width=tw-20, complete_style="#cba6f7")
    viz_h = max(2, th - len(table.rows) - 12)
    viz = get_huge_visualizer(tw-6, viz_h, is_paused)

    footer = Group(
        Text(f"Track {index}/{total} | Time: {elapsed//60:02d}:{elapsed%60:02d}", style="#6c7086"),
        song_prog,
        Text("\n"),
        viz
    )

    return Panel(
        Group(header, list_prog, Text("\n"), table, Text("\n"), footer),
        border_style="#cba6f7" if not is_paused else "#f38ba8",
        height=th
    )