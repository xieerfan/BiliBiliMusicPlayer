import click
import json
import os
import asyncio
from core.player import play_audio_stream, PlayerCallbackHandler
from core.mpris_controller import MPRISController


def load_config():
    cfg_path = os.path.expanduser("~/.config/BiliBiliMusicPlayer/config.json")
    if os.path.exists(cfg_path):
        with open(cfg_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"tracks": [], "lang": "zh"}


@click.command()
@click.option('--no-mpris', is_flag=True, help='禁用 MPRIS 媒体控制')
def play(no_mpris):
    """播放歌单（支持 MPRIS 媒体控制）"""
    config = load_config()
    tracks = config.get("tracks", [])
    lang = config.get("lang", "zh")
    
    if not tracks:
        click.echo("歌单为空，请先添加歌曲")
        return
    
    # 初始化 MPRIS 控制器
    mpris_controller = None
    callback_handler = None
    
    if not no_mpris:
        try:
            callback_handler = PlayerCallbackHandler()
            mpris_controller = MPRISController(callback_handler)
            
            if mpris_controller.start():
                click.echo("✓ MPRIS 媒体控制已启用")
            else:
                click.echo("⚠ MPRIS 启动失败，继续播放...")
                mpris_controller = None
        except Exception as e:
            click.echo(f"⚠ MPRIS 初始化失败: {e}")
            mpris_controller = None
    
    try:
        idx = 0
        while True:  # 无限循环播放列表
            # 边界检查
            if idx >= len(tracks):
                idx = 0  # 回到第一首
            if idx < 0:
                idx = len(tracks) - 1  # 回到最后一首
            
            # 重置回调处理器状态
            if callback_handler:
                callback_handler.should_skip = False
                callback_handler.should_previous = False
                callback_handler.should_exit = False
                callback_handler.is_paused = False
            
            # 播放当前曲目
            result = asyncio.run(
                play_audio_stream(
                    tracks[idx], 
                    tracks, 
                    idx + 1, 
                    len(tracks), 
                    lang,
                    mpris_controller,
                    callback_handler
                )
            )
            
            # 根据返回值决定下一步
            if result == "exit":
                # ESC 退出或 MPRIS 停止
                click.echo("\n✓ 播放已停止")
                break
            elif result == "previous":
                # 上一曲
                idx -= 1
            elif result == "skip":
                # Q 跳过或 MPRIS 下一曲
                idx += 1
            elif result == "next":
                # 自然播放完成，下一曲
                idx += 1
            else:
                # 其他情况，默认下一曲
                idx += 1
    
    except KeyboardInterrupt:
        click.echo("\n✓ 用户中断播放")
    
    finally:
        # 停止 MPRIS 服务
        if mpris_controller:
            mpris_controller.stop()
            click.echo("✓ MPRIS 服务已停止")


if __name__ == '__main__':
    play()