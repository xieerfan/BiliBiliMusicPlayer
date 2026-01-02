import random
from rich.console import Console
from rich.text import Text
from rich.table import Table
from rich.layout import Layout

console = Console()

# Catppuccin Mocha Palette
MAUVE = "#cba6f7"
LAVENDER = "#b4befe"
GREEN = "#a6e3a1"
SURFACE0 = "#313244"
OVERLAY0 = "#6c7086"
TEXT = "#cdd6f4"
BASE = "#1e1e2e"

BILI_ART = r"""
  ____  _ _ _ ____  _ _ _ 
 | __ )(_) (_) __ )(_) (_)
 |  _ \| | | |  _ \| | | |
 | |_) | | | | |_) | | | |
 |____/|_|_|_|____/|_|_|_|"""

def print_banner():
    """供 setup 和 main 使用，绝对不会再报 ImportError 了喵！"""
    console.print(BILI_ART, style=MAUVE)
    console.print(f" {'━' * 48}", style=SURFACE0)
    console.print(f"  [#b4befe]BiliBili MusicPlayer[/] | [#bac2de]MTF Edition 2026[/]\n")

def get_visualizer(width=46):
    """生成 ASCII 频谱"""
    chars = [" ", " ", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
    return Text("".join(random.choice(chars) for _ in range(width)), style=MAUVE)

def make_player_layout(current_track, tracks, index, total):
    """构建播放界面"""
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body", size=10),
        Layout(name="footer", size=5)
    )

    layout["header"].update(Text(f"\n ◉ NOW PLAYING: {current_track}", style=f"bold {MAUVE}"))

    table = Table(show_header=False, box=None, padding=(0, 1), show_edge=False)
    table.add_column("ID", width=4)
    table.add_column("Title")
    
    start = max(0, index - 3)
    end = min(total, index + 4)
    for i in range(start, end):
        t_idx = i + 1
        title = tracks[i]['title'][:40]
        style = f"bold {BASE} on {GREEN}" if t_idx == index else OVERLAY0
        table.add_row(f"{t_idx:02d}", title, style=style)
    
    layout["body"].update(table)

    viz = get_visualizer()
    info = Text(f"\n [ {index}/{total} ]  Space:Pause | Q:Skip\n {'━' * 48}\n", style=SURFACE0)
    layout["footer"].update(Text.assemble(info, viz))

    return layout