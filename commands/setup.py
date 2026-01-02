import click
import asyncio
import os
import json
import sys
import readchar
from colorama import Fore, Style
from utils.banner import print_banner
from utils.parser import extract_bvid, parse_range
from core.api import fetch_all_videos, get_single_video_info

CONFIG_DIR = os.path.expanduser("~/.config/BiliBiliMusicPlayer")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")

def load_config():
    """读取现有配置，如果不存在则返回空模板"""
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {"tracks": []}
    return {"tracks": []}

def save_config(config_data):
    """保存配置到 JSON"""
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config_data, f, ensure_ascii=False, indent=4)

def display_interface(videos, page, page_size, input_buffer, mode_title="视频列表"):
    """渲染 UI 界面"""
    sys.stdout.write("\033[H\033[J")
    print_banner()
    start = page * page_size
    current_batch = videos[start:start+page_size]
    total_pages = (len(videos) - 1) // page_size + 1
    
    click.echo(f"{Fore.GREEN}--- {mode_title} (第 {page+1}/{total_pages} 页) ---")
    click.echo(f"{Fore.WHITE}方向键 {Fore.YELLOW}← →{Fore.WHITE} 翻页 | 输入范围后回车确认 | {Fore.RED}ESC{Fore.WHITE} 返回主菜单\n")
    
    line = ""
    for i, v in enumerate(current_batch, start + 1):
        idx_f = f"{i:3}"
        title = (v['title'][:10] + "..") if len(v['title']) > 10 else v['title'].ljust(10)
        line += f"{Fore.WHITE}[{idx_f}] {Fore.CYAN}{title}  "
        if (i - start + 1) % 4 == 0:
            click.echo(line)
            line = ""
    if line: click.echo(line)
    print("\n" + Fore.WHITE + "-" * 60)
    sys.stdout.write(f"{Fore.YELLOW}请输入索引范围进行操作: {Fore.WHITE}{input_buffer}")
    sys.stdout.flush()

@click.command()
def setup():
    """初始化配置/管理歌单喵"""
    
    while True:
        sys.stdout.write("\033[H\033[J") # 清屏
        print_banner()
        
        # 显示当前歌单统计
        current_config = load_config()
        track_count = len(current_config.get("tracks", []))
        click.echo(f"{Fore.CYAN}当前歌单内共有 {Fore.YELLOW}{track_count}{Fore.CYAN} 首音乐\n")

        # 模式选择
        click.echo(Fore.WHITE + "请选择操作:")
        click.echo("  1. 添加单个视频 (追加)")
        click.echo("  2. 从合集导入视频 (追加)")
        click.echo("  3. 管理/删除现有歌单")
        click.echo(Fore.RED + "  4. 退出设置")
        
        mode = click.prompt(Fore.WHITE + "\n请输入编号", type=click.Choice(['1', '2', '3', '4']), default='4', show_choices=False)

        if mode == '4':
            click.echo(Fore.GREEN + "已退出设置，喵！")
            break

        # 模式 1：单个追加
        if mode == '1':
            url_input = click.prompt(Fore.WHITE + "请输入视频 URL 或 BV 号")
            bvid = extract_bvid(url_input)
            if bvid:
                click.echo(f"{Fore.YELLOW}正在获取信息...")
                try:
                    title = asyncio.run(get_single_video_info(bvid))
                    current_config["tracks"].append({"bvid": bvid, "title": title})
                    save_config(current_config)
                    click.echo(Fore.GREEN + f"✨ 已添加: {title}")
                    click.pause(Fore.WHITE + "按任意键继续...")
                except Exception as e:
                    click.echo(Fore.RED + f"失败: {e}")
                    click.pause()
            else:
                click.echo(Fore.RED + "无法识别 BV 号！")
                click.pause()

        # 模式 2：合集导入 (改为追加)
        elif mode == '2':
            sid = click.prompt(Fore.WHITE + "请输入 season_id", type=int)
            click.echo(f"{Fore.YELLOW}正在获取合集列表...")
            try:
                videos = asyncio.run(fetch_all_videos(sid))
                if not videos:
                    click.echo(Fore.RED + "合集为空或不存在。")
                    click.pause()
                    continue

                current_page, page_size, input_buffer = 0, 40, ""
                while True:
                    display_interface(videos, current_page, page_size, input_buffer, "选择要添加的视频")
                    key = readchar.readkey()
                    if key == readchar.key.RIGHT and (current_page + 1) * page_size < len(videos): current_page += 1
                    elif key == readchar.key.LEFT and current_page > 0: current_page -= 1
                    elif key in (readchar.key.BACKSPACE, '\x7f'): input_buffer = input_buffer[:-1]
                    elif key == readchar.key.ENTER: break
                    elif key == readchar.key.ESC: break
                    elif len(key) == 1 and (key.isdigit() or key in "-,alAL"): input_buffer += key
                
                if key == readchar.key.ESC: continue # 返回主菜单

                idx_list = parse_range(input_buffer, len(videos))
                for i in idx_list:
                    current_config["tracks"].append({"bvid": videos[i-1]["bvid"], "title": videos[i-1]["title"]})
                save_config(current_config)
                click.echo(Fore.GREEN + f"✨ 成功追加 {len(idx_list)} 首音乐。")
                click.pause()
            except Exception as e:
                click.echo(Fore.RED + f"错误: {e}")
                click.pause()

        # 模式 3：查看/删除
        elif mode == '3':
            tracks = current_config.get("tracks", [])
            if not tracks:
                click.echo(Fore.RED + "歌单是空的。")
                click.pause()
                continue

            current_page, page_size, input_buffer = 0, 40, ""
            while True:
                display_interface(tracks, current_page, page_size, input_buffer, "管理歌单")
                key = readchar.readkey()
                if key == readchar.key.RIGHT and (current_page + 1) * page_size < len(tracks): current_page += 1
                elif key == readchar.key.LEFT and current_page > 0: current_page -= 1
                elif key in (readchar.key.BACKSPACE, '\x7f'): input_buffer = input_buffer[:-1]
                elif key == readchar.key.ENTER: break
                elif key == readchar.key.ESC: break
                elif len(key) == 1 and (key.isdigit() or key in "-,alAL"): input_buffer += key
            
            if key == readchar.key.ESC: continue

            del_idx = parse_range(input_buffer, len(tracks))
            current_config["tracks"] = [t for i, t in enumerate(tracks, 1) if i not in del_idx]
            save_config(current_config)
            click.echo(Fore.GREEN + f"✨ 已更新，删除了 {len(del_idx)} 首音乐。")
            click.pause()