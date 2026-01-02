import click
import asyncio
import os
import json
import sys
import readchar
from rich.table import Table
from rich.prompt import Prompt
from utils.banner import print_banner, console
from utils.parser import extract_bvid, parse_range
from utils.i18n import get_text
from core.api import fetch_all_videos, get_single_video_info

CONFIG_PATH = os.path.expanduser("~/.config/BiliBiliMusicPlayer/config.json")

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"tracks": [], "lang": "zh"}

def save_config(cfg):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=4)

def display_interface(videos, page, page_size, input_buffer, mode_key, lang):
    """通用的列表展示界面，支持导入和管理"""
    os.system('clear')
    print_banner(lang)
    start = page * page_size
    current_batch = videos[start : start + page_size]
    total_pages = (len(videos) - 1) // page_size + 1
    
    # 顶部状态
    console.print(f" [#b4befe]{get_text('mode', lang)}:[/] {get_text(mode_key, lang)} [#6c7086]({page+1}/{total_pages})[/]")
    console.print(f" [#6c7086]{get_text('help_nav', lang)}[/]\n")
    
    table = Table(show_header=False, box=None, padding=(0, 1), show_edge=False)
    for _ in range(4): table.add_column(width=25)
    
    row = []
    for i, v in enumerate(current_batch, start + 1):
        # 截取标题长度防止错位
        title_disp = v['title'][:12]
        row.append(f"[#cba6f7]{i:02d}[/] [#cdd6f4]{title_disp}[/]")
        if len(row) == 4:
            table.add_row(*row)
            row = []
    if row:
        while len(row) < 4: row.append("")
        table.add_row(*row)
    
    console.print(table)
    console.print(f"\n [#6c7086]{'━' * 50}[/]")
    console.print(f" [#a6e3a1]{get_text('input_prompt', lang)}[/] [#cdd6f4]{input_buffer}[/]", end="")
    sys.stdout.flush()

@click.command()
def setup():
    """配置管理主入口"""
    while True:
        os.system('clear')
        cfg = load_config()
        L = cfg.get("lang", "zh")
        print_banner(L)
        
        tracks = cfg.get("tracks", [])
        
        # 主菜单提示
        console.print(f" [#bac2de]{get_text('library', L)}:[/] [#a6e3a1]{len(tracks)}[/] [#bac2de]{get_text('tracks_unit', L)}[/]\n")
        console.print(f" [#cba6f7]1.[/] {get_text('menu_1', L)}")
        console.print(f" [#cba6f7]2.[/] {get_text('menu_2', L)}")
        console.print(f" [#cba6f7]3.[/] {get_text('menu_3', L)}")
        console.print(f" [#f38ba8]4.[/] {get_text('menu_4', L)}\n")
        
        # 修复数字重复：关闭 show_choices
        mode = Prompt.ask(f"[#b4befe]{get_text('select', L)}[/]", choices=['1', '2', '3', '4'], show_choices=False)

        if mode == '4':
            console.print(f"\n [#a6e3a1]{get_text('save_exit', L)}[/]")
            break

        # --- 模式 1：添加单曲 ---
        if mode == '1':
            url_input = Prompt.ask(f" [#cdd6f4]{get_text('url_bvid', L)}[/]")
            bvid = extract_bvid(url_input)
            if bvid:
                try:
                    title = asyncio.run(get_single_video_info(bvid))
                    cfg["tracks"].append({"bvid": bvid, "title": title})
                    save_config(cfg)
                    console.print(f" [#a6e3a1]✓ {get_text('added', L)}[/] {title}")
                except Exception as e:
                    console.print(f" [#f38ba8]Error:[/] {e}")
            click.pause()

        # --- 模式 2：合集导入 ---
        elif mode == '2':
            sid_str = Prompt.ask(f" [#cdd6f4]{get_text('sid', L)}[/]")
            if sid_str.isdigit():
                try:
                    videos = asyncio.run(fetch_all_videos(int(sid_str)))
                    curr_page, buf = 0, ""
                    while True:
                        display_interface(videos, curr_page, 40, buf, "menu_2", L)
                        k = readchar.readkey()
                        if k == readchar.key.RIGHT and (curr_page + 1) * 40 < len(videos): curr_page += 1
                        elif k == readchar.key.LEFT and curr_page > 0: curr_page -= 1
                        elif k in (readchar.key.BACKSPACE, '\x7f'): buf = buf[:-1]
                        elif k == readchar.key.ENTER: break
                        elif k == readchar.key.ESC: break
                        elif len(k) == 1 and (k.isdigit() or k in "-,al"): buf += k
                    
                    if k != readchar.key.ESC and buf:
                        idx_list = parse_range(buf, len(videos))
                        for i in idx_list:
                            cfg["tracks"].append({"bvid": videos[i-1]["bvid"], "title": videos[i-1]["title"]})
                        save_config(cfg)
                        console.print(f"\n [#a6e3a1]✓ {get_text('success', L)} {len(idx_list)} {get_text('tracks_unit', L)}[/]")
                    click.pause()
                except Exception as e:
                    console.print(f" [#f38ba8]Error:[/] {e}")
                    click.pause()

        # --- 模式 3：列表管理 (删除) ---
        elif mode == '3':
            if not tracks:
                console.print(f" [#f38ba8]{get_text('empty', L)}[/]")
                click.pause(); continue
                
            curr_page, buf = 0, ""
            while True:
                display_interface(tracks, curr_page, 40, buf, "menu_3", L)
                k = readchar.readkey()
                if k == readchar.key.RIGHT and (curr_page + 1) * 40 < len(tracks): curr_page += 1
                elif k == readchar.key.LEFT and curr_page > 0: curr_page -= 1
                elif k in (readchar.key.BACKSPACE, '\x7f'): buf = buf[:-1]
                elif k == readchar.key.ENTER: break
                elif k == readchar.key.ESC: break
                elif len(k) == 1 and (k.isdigit() or k in "-,al"): buf += k
            
            if k != readchar.key.ESC and buf:
                del_idx = parse_range(buf, len(tracks))
                cfg["tracks"] = [t for i, t in enumerate(tracks, 1) if i not in del_idx]
                save_config(cfg)
                console.print(f"\n [#f38ba8]✗ {get_text('removed', L)} {len(del_idx)} {get_text('tracks_unit', L)}[/]")
            click.pause()