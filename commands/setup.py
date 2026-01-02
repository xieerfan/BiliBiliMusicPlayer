import click
import asyncio
import os
import json
import sys
import readchar
from colorama import Fore
from utils.banner import print_banner
from utils.parser import extract_bvid, parse_range
from core.api import fetch_all_videos, get_single_video_info

CONFIG_DIR = os.path.expanduser("~/.config/BiliBiliMusicPlayer")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")

def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f: return json.load(f)
        except: return {"tracks": []}
    return {"tracks": []}

def save_config(config_data):
    if not os.path.exists(CONFIG_DIR): os.makedirs(CONFIG_DIR)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config_data, f, ensure_ascii=False, indent=4)

def display_list(videos, page, page_size, input_buffer, title):
    sys.stdout.write("\033[H\033[J")
    print_banner()
    start = page * page_size
    current_batch = videos[start:start+page_size]
    total_pages = (len(videos) - 1) // page_size + 1
    click.echo(f"{Fore.GREEN}--- {title} (第 {page+1}/{total_pages} 页) ---")
    line = ""
    for i, v in enumerate(current_batch, start + 1):
        idx_f = f"{i:3}"
        v_title = (v['title'][:10] + "..") if len(v['title']) > 10 else v['title'].ljust(10)
        line += f"{Fore.WHITE}[{idx_f}] {Fore.CYAN}{v_title}  "
        if (i - start) % 4 == 0:
            click.echo(line); line = ""
    if line: click.echo(line)
    sys.stdout.write(f"\n{Fore.YELLOW}输入范围后回车: {Fore.WHITE}{input_buffer}")
    sys.stdout.flush()

@click.command()
def setup():
    while True:
        os.system('clear')
        print_banner()
        conf = load_config()
        click.echo(f"{Fore.WHITE}当前歌曲数: {len(conf['tracks'])}\n")
        click.echo("1. 单个添加 | 2. 合集导入 | 3. 管理删除 | 4. 退出")
        mode = click.prompt("请选择", type=click.Choice(['1','2','3','4']), default='4', show_choices=False)

        if mode == '4': break
        
        if mode == '1':
            url = click.prompt("URL/BV")
            bvid = extract_bvid(url)
            if bvid:
                title = asyncio.run(get_single_video_info(bvid))
                conf['tracks'].append({"bvid": bvid, "title": title})
                save_config(conf)
            click.pause()
        
        elif mode == '2':
            sid = click.prompt("season_id", type=int)
            vids = asyncio.run(fetch_all_videos(sid))
            curr, buf = 0, ""
            while True:
                display_list(vids, curr, 40, buf, "合集导入")
                k = readchar.readkey()
                if k == readchar.key.RIGHT and (curr+1)*40 < len(vids): curr += 1
                elif k == readchar.key.LEFT and curr > 0: curr -= 1
                elif k in (readchar.key.BACKSPACE, '\x7f'): buf = buf[:-1]
                elif k == readchar.key.ENTER: break
                elif k == readchar.key.ESC: break
                elif len(k)==1 and (k.isdigit() or k in "-,al"): buf += k
            if k != readchar.key.ESC:
                idx = parse_range(buf, len(vids))
                for i in idx: conf['tracks'].append({"bvid": vids[i-1]["bvid"], "title": vids[i-1]["title"]})
                save_config(conf)
            click.pause()

        elif mode == '3':
            trks = conf['tracks']
            curr, buf = 0, ""
            while True:
                display_list(trks, curr, 40, buf, "歌单管理")
                k = readchar.readkey()
                if k == readchar.key.RIGHT and (curr+1)*40 < len(trks): curr += 1
                elif k == readchar.key.LEFT and curr > 0: curr -= 1
                elif k in (readchar.key.BACKSPACE, '\x7f'): buf = buf[:-1]
                elif k == readchar.key.ENTER: break
                elif k == readchar.key.ESC: break
                elif len(k)==1 and (k.isdigit() or k in "-,al"): buf += k
            if k != readchar.key.ESC:
                del_idx = parse_range(buf, len(trks))
                conf['tracks'] = [t for i, t in enumerate(trks, 1) if i not in del_idx]
                save_config(conf)
            click.pause()