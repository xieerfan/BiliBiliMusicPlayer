import click
import asyncio
import os
import json
import sys
import readchar
from rich.table import Table
from utils.banner import print_banner, console
from utils.parser import extract_bvid, parse_range
from core.api import fetch_all_videos, get_single_video_info

# 配置路径
CONFIG_DIR = os.path.expanduser("~/.config/BiliBiliMusicPlayer")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")

def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {"tracks": []}
    return {"tracks": []}

def save_config(config_data):
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config_data, f, ensure_ascii=False, indent=4)

def display_interface(videos, page, page_size, input_buffer, mode_title):
    """渲染低饱和度样式的列表"""
    os.system('clear')
    print_banner()
    
    start = page * page_size
    current_batch = videos[start : start + page_size]
    total_pages = (len(videos) - 1) // page_size + 1
    
    # 顶部状态栏 (Lavender 配色)
    console.print(f" [#b4befe]MODE:[/] {mode_title} [#6c7086]({page+1}/{total_pages} 页)[/]")
    console.print(f" [#6c7086]← → 翻页 | 输入范围回车 | ESC 返回[/]\n")
    
    # 使用 Rich Table 布局列表
    table = Table(show_header=False, box=None, padding=(0, 1), show_edge=False)
    for _ in range(4): table.add_column(width=20) # 4 列布局

    row = []
    for i, v in enumerate(current_batch, start + 1):
        v_title = (v['title'][:12] + "..") if len(v['title']) > 12 else v['title'].ljust(12)
        # ID 使用 Mauve, 标题使用 Text 色
        row.append(f"[#cba6f7]{i:02d}[/] [#cdd6f4]{v_title}[/]")
        if len(row) == 4:
            table.add_row(*row)
            row = []
    if row:
        while len(row) < 4: row.append("")
        table.add_row(*row)
    
    console.print(table)
    console.print(f"\n [#6c7086]{'━' * 48}[/]")
    console.print(f" [#a6e3a1]>> INPUT:[/] [#cdd6f4]{input_buffer}[/]", end="")
    sys.stdout.flush()

@click.command()
def setup():
    """初始化配置/管理歌单 (Catppuccin 配色版)"""
    
    while True:
        os.system('clear')
        print_banner()
        
        current_config = load_config()
        track_count = len(current_config.get("tracks", []))
        
        # 主菜单
        console.print(f" [#bac2de]Library:[/] [#a6e3a1]{track_count}[/] [#bac2de]tracks[/]\n")
        console.print(" [#cba6f7]1.[/] [#cdd6f4]Add Single (Append)[/]")
        console.print(" [#cba6f7]2.[/] [#cdd6f4]Import Collection (Append)[/]")
        console.print(" [#cba6f7]3.[/] [#cdd6f4]Manage Playlist[/]")
        console.print(" [#f38ba8]4. Exit Setup[/]") # Red for Exit
        
        mode = click.prompt("\n [#b4befe]Select[/]", type=click.Choice(['1', '2', '3', '4']), default='4', show_choices=False)

        if mode == '4':
            console.print("\n [#a6e3a1]Settings saved. Goodbye![/]")
            break

        # 模式 1：单个追加
        if mode == '1':
            url_input = click.prompt(" [#cdd6f4]URL / BVID[/]")
            bvid = extract_bvid(url_input)
            if bvid:
                try:
                    title = asyncio.run(get_single_video_info(bvid))
                    current_config["tracks"].append({"bvid": bvid, "title": title})
                    save_config(current_config)
                    console.print(f" [#a6e3a1]✓ Added:[/] {title}")
                except Exception as e:
                    console.print(f" [#f38ba8]Error:[/] {e}")
            click.pause()

        # 模式 2：合集导入
        elif mode == '2':
            sid = click.prompt(" [#cdd6f4]Season ID[/]", type=int)
            try:
                videos = asyncio.run(fetch_all_videos(sid))
                curr_page, buf = 0, ""
                while True:
                    display_interface(videos, curr_page, 40, buf, "IMPORT COLLECTION")
                    k = readchar.readkey()
                    if k == readchar.key.RIGHT and (curr_page + 1) * 40 < len(videos): curr_page += 1
                    elif k == readchar.key.LEFT and curr_page > 0: curr_page -= 1
                    elif k in (readchar.key.BACKSPACE, '\x7f'): buf = buf[:-1]
                    elif k == readchar.key.ENTER: break
                    elif k == readchar.key.ESC: break
                    elif len(k) == 1 and (k.isdigit() or k in "-,al"): buf += k
                
                if k != readchar.key.ESC:
                    idx_list = parse_range(buf, len(videos))
                    for i in idx_list:
                        current_config["tracks"].append({"bvid": videos[i-1]["bvid"], "title": videos[i-1]["title"]})
                    save_config(current_config)
                    console.print(f"\n [#a6e3a1]✓ Success added {len(idx_list)} tracks.[/]")
                click.pause()
            except Exception as e:
                console.print(f" [#f38ba8]Error:[/] {e}")
                click.pause()

        # 模式 3：删除管理
        elif mode == '3':
            tracks = current_config.get("tracks", [])
            if not tracks:
                console.print(" [#f38ba8]Playlist is empty.[/]")
                click.pause(); continue

            curr_page, buf = 0, ""
            while True:
                display_interface(tracks, curr_page, 40, buf, "MANAGE PLAYLIST")
                k = readchar.readkey()
                if k == readchar.key.RIGHT and (curr_page + 1) * 40 < len(tracks): curr_page += 1
                elif k == readchar.key.LEFT and curr_page > 0: curr_page -= 1
                elif k in (readchar.key.BACKSPACE, '\x7f'): buf = buf[:-1]
                elif k == readchar.key.ENTER: break
                elif k == readchar.key.ESC: break
                elif len(k) == 1 and (k.isdigit() or k in "-,al"): buf += k
            
            if k != readchar.key.ESC:
                del_idx = parse_range(buf, len(tracks))
                current_config["tracks"] = [t for i, t in enumerate(tracks, 1) if i not in del_idx]
                save_config(current_config)
                console.print(f"\n [#f38ba8]✗ Removed {len(del_idx)} tracks.[/]")
            click.pause()