import subprocess
import asyncio
from bilibili_api import video, Credential
from bilibili_api.exceptions import ArgsException

async def play_audio_stream(bvid):
    """获取音频流并直接通过 mpv 播放 (修复了 cid 缺失问题)"""
    # 1. 实例化视频对象
    # 如果你有 SESSDATA，建议传入 Credential 以获取高音质
    v = video.Video(bvid=bvid)
    
    try:
        # 2. 获取视频的分 P 信息 (必须拿到 cid 才能获取播放地址)
        pages = await v.get_pages()
        # 默认播放第 1 个分 P (索引为 0)
        target_page = pages[0]
        cid = target_page['cid']
        
        # 3. 获取播放地址，现在传入了 page_index
        # 也可以直接传 cid=cid
        download_url_data = await v.get_download_url(page_index=0)
        
        # 提取音频流 URL
        if 'dash' in download_url_data:
            # DASH 格式 (通常音质更好)
            audio_url = download_url_data['dash']['audio'][0]['base_url']
        else:
            # 兼容模式 (旧的 MP4 格式，音视频合一)
            audio_url = download_url_data['durl'][0]['url']
        
        # 4. 构造 mpv 命令
        cmd = [
            "mpv",
            audio_url,
            "--no-video",
            f"--referrer=https://www.bilibili.com/video/{bvid}",
            "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            # 设置终端标题显示正在播放的内容
            f"--title=BiliPlayer - {bvid}",
            "--terminal=yes"
        ]
        
        print(f"\n  >> 正在从云端拉取流音频...")
        print(f"  >> [Q] 退出当前 | [Space] 暂停 | [9/0] 减/加音量\n")
        
        # 5. 启动进程
        # 使用 subprocess.run 会阻塞直到 mpv 关闭
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    except ArgsException as e:
        print(f"参数错误喵: {e}")
    except Exception as e:
        print(f"播放出错喵: {e}")

if __name__ == "__main__":
    # 测试用例：之前你提到的那个 BV 号
    test_bvid = "BV1sQvQBGEJe" 
    asyncio.run(play_audio_stream(test_bvid))