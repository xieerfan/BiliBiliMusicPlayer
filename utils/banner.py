from colorama import Fore, Style
from rich.panel import Panel
from rich.console import Console
from rich.text import Text

console = Console()

BILI_ART = r"""
  ____  _ _ _ ____  _ _ _ 
 | __ )(_) (_) __ )(_) (_)
 |  _ \| | | |  _ \| | | |
 | |_) | | | | |_) | | | |
 |____/|_|_|_|____/|_|_|_|"""

def print_banner():
    print("\n" + Fore.LIGHTMAGENTA_EX + Style.BRIGHT + BILI_ART)
    print(Fore.WHITE + Style.BRIGHT + "  " + "-" * 56)
    print(f"{Fore.CYAN}  >> BiliBili-MusicPlayer CLI | MTF Edition | 2026-01-03{Style.RESET_ALL}\n")

def print_player_ui(current_track, total, index, status="正在播放"):
    ui_text = Text()
    ui_text.append(f"\n   🎵 {current_track}\n", style="bold magenta")
    ui_text.append(f"   📊 进度: [{index}/{total}]   状态: {status}\n", style="cyan")
    ui_text.append(f"   🎹 操作: [Space]暂停/播放  [Q]跳过  [9/0]音量\n", style="dim white")

    panel = Panel(
        ui_text,
        title="[bold light_blue]BiliBili Music Player[/]",
        subtitle="[dim pink]MTF Edition 2026[/]",
        border_style="bright_magenta",
        padding=(1, 2)
    )
    console.print(panel)