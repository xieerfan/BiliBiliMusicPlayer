from rich.console import Console
from rich.text import Text
from rich.table import Table

console = Console()

# 找回字符艺术并使用低饱和度的 Mauve 配色
BILI_ART = r"""
  ____  _ _ _ ____  _ _ _ 
 | __ )(_) (_) __ )(_) (_)
 |  _ \| | | |  _ \| | | |
 | |_) | | | | |_) | | | |
 |____/|_|_|_|____/|_|_|_|"""

def print_banner():
    """设置界面使用的 Banner"""
    console.print(BILI_ART, style="#cba6f7") # Mauve
    console.print("-" * 50, style="#6c7086") # Overlay0
    console.print("  [#b4befe]BiliBili MusicPlayer[/] | [#bac2de]MTF Edition 2026[/]\n")

def print_player_ui(current_track, tracks, index, total):
    """
    播放界面：参考 Catppuccin 配色
    """
    # 顶部信息：Lavender 背景，深色字
    header = Text()
    header.append(" NOW PLAYING ", style="bold #1e1e2e on #b4befe") # Base on Lavender
    header.append(f" {current_track}", style="#cdd6f4") # Text
    console.print("\n", header)
    
    # 播放列表：低饱和度配色
    table = Table(show_header=False, box=None, padding=(0, 1), show_edge=False)
    table.add_column("Status", width=3)
    table.add_column("ID", width=4)
    table.add_column("Title")

    start = max(0, index - 3)
    end = min(total, index + 5)
    
    for i in range(start, end):
        t_idx = i + 1
        title = tracks[i]['title']
        
        if t_idx == index:
            # 当前播放：Green 高亮，深色字
            table.add_row(" > ", f"{t_idx:02d}", title, style="bold #1e1e2e on #a6e3a1")
        else:
            # 未播放：Overlay0 灰色
            table.add_row("   ", f"{t_idx:02d}", title, style="#6c7086")

    console.print("\n", table)
    
    # 底部统计：Subtext0 风格
    footer = Text(f" [ {index} / {total} ]  Space: Pause | Q: Next | 9,0: Vol", style="#a6adc8")
    console.print("\n", footer)
    console.print("-" * 50, style="#6c7086")