"""
MPRIS2 控制器 - 用于与桌面环境的媒体控制集成
支持 Hyprland/Waybar/任何支持 MPRIS 的环境
"""

import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
import threading
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MPRISInterface(dbus.service.Object):
    """
    MPRIS2 接口实现
    提供标准的媒体播放器控制接口
    """
    
    MPRIS_IFACE = "org.mpris.MediaPlayer2"
    MPRIS_PLAYER_IFACE = "org.mpris.MediaPlayer2.Player"
    MPRIS_PATH = "/org/mpris/MediaPlayer2"
    
    def __init__(self, bus_name, callback_handler):
        """
        初始化 MPRIS 接口
        
        Args:
            bus_name: D-Bus 总线名称
            callback_handler: 回调处理器,包含播放控制方法
        """
        super().__init__(bus_name, self.MPRIS_PATH)
        self.callback = callback_handler
        
        # 播放器状态
        self._playback_status = "Stopped"  # Playing, Paused, Stopped
        self._metadata = {}
        self._volume = 1.0
        self._position = 0  # 微秒
        
    # ==================== org.mpris.MediaPlayer2 接口 ====================
    
    @dbus.service.method(MPRIS_IFACE)
    def Raise(self):
        """提升播放器窗口（终端应用不适用）"""
        pass
    
    @dbus.service.method(MPRIS_IFACE)
    def Quit(self):
        """退出播放器"""
        if hasattr(self.callback, 'quit'):
            self.callback.quit()
    
    @dbus.service.method(dbus.PROPERTIES_IFACE, in_signature='ss', out_signature='v')
    def Get(self, interface_name, property_name):
        """获取属性"""
        return self.GetAll(interface_name)[property_name]
    
    @dbus.service.method(dbus.PROPERTIES_IFACE, in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface_name):
        """获取所有属性"""
        if interface_name == self.MPRIS_IFACE:
            return {
                'CanQuit': True,
                'CanRaise': False,
                'HasTrackList': False,
                'Identity': 'BiliBili Music Player',
                'DesktopEntry': 'biliplayer',
                'SupportedUriSchemes': dbus.Array([], signature='s'),
                'SupportedMimeTypes': dbus.Array([], signature='s'),
            }
        elif interface_name == self.MPRIS_PLAYER_IFACE:
            return {
                'PlaybackStatus': self._playback_status,
                'Rate': 1.0,
                'Metadata': dbus.Dictionary(self._metadata, signature='sv'),
                'Volume': self._volume,
                'Position': dbus.Int64(self._position),
                'MinimumRate': 1.0,
                'MaximumRate': 1.0,
                'CanGoNext': True,
                'CanGoPrevious': True,
                'CanPlay': True,
                'CanPause': True,
                'CanSeek': False,
                'CanControl': True,
            }
        return {}
    
    @dbus.service.method(dbus.PROPERTIES_IFACE, in_signature='ssv')
    def Set(self, interface_name, property_name, new_value):
        """设置属性"""
        if interface_name == self.MPRIS_PLAYER_IFACE:
            if property_name == 'Volume':
                self._volume = new_value
                if hasattr(self.callback, 'set_volume'):
                    self.callback.set_volume(new_value)
    
    @dbus.service.signal(dbus.PROPERTIES_IFACE, signature='sa{sv}as')
    def PropertiesChanged(self, interface_name, changed_properties, invalidated_properties):
        """属性变化信号"""
        pass
    
    # ==================== org.mpris.MediaPlayer2.Player 接口 ====================
    
    @dbus.service.method(MPRIS_PLAYER_IFACE)
    def Next(self):
        """下一曲"""
        logger.info("MPRIS: Next called")
        if hasattr(self.callback, 'next'):
            self.callback.next()
    
    @dbus.service.method(MPRIS_PLAYER_IFACE)
    def Previous(self):
        """上一曲"""
        logger.info("MPRIS: Previous called")
        if hasattr(self.callback, 'previous'):
            self.callback.previous()
    
    @dbus.service.method(MPRIS_PLAYER_IFACE)
    def Pause(self):
        """暂停"""
        logger.info("MPRIS: Pause called")
        if hasattr(self.callback, 'pause'):
            self.callback.pause()
            self.update_playback_status("Paused")
    
    @dbus.service.method(MPRIS_PLAYER_IFACE)
    def PlayPause(self):
        """播放/暂停切换"""
        logger.info("MPRIS: PlayPause called")
        if hasattr(self.callback, 'play_pause'):
            new_status = self.callback.play_pause()
            self.update_playback_status(new_status)
    
    @dbus.service.method(MPRIS_PLAYER_IFACE)
    def Stop(self):
        """停止"""
        logger.info("MPRIS: Stop called")
        if hasattr(self.callback, 'stop'):
            self.callback.stop()
            self.update_playback_status("Stopped")
    
    @dbus.service.method(MPRIS_PLAYER_IFACE)
    def Play(self):
        """播放"""
        logger.info("MPRIS: Play called")
        if hasattr(self.callback, 'play'):
            self.callback.play()
            self.update_playback_status("Playing")
    
    @dbus.service.method(MPRIS_PLAYER_IFACE, in_signature='x')
    def Seek(self, offset):
        """相对定位（微秒）"""
        logger.info(f"MPRIS: Seek called with offset {offset}")
        if hasattr(self.callback, 'seek'):
            self.callback.seek(offset / 1000000)  # 转换为秒
    
    @dbus.service.method(MPRIS_PLAYER_IFACE, in_signature='ox')
    def SetPosition(self, track_id, position):
        """绝对定位（微秒）"""
        logger.info(f"MPRIS: SetPosition called with position {position}")
        if hasattr(self.callback, 'set_position'):
            self.callback.set_position(position / 1000000)  # 转换为秒
    
    @dbus.service.method(MPRIS_PLAYER_IFACE, in_signature='s')
    def OpenUri(self, uri):
        """打开URI"""
        logger.info(f"MPRIS: OpenUri called with {uri}")
        if hasattr(self.callback, 'open_uri'):
            self.callback.open_uri(uri)
    
    @dbus.service.signal(MPRIS_PLAYER_IFACE, signature='x')
    def Seeked(self, position):
        """定位完成信号"""
        pass
    
    # ==================== 状态更新方法 ====================
    
    def update_playback_status(self, status):
        """
        更新播放状态
        
        Args:
            status: "Playing", "Paused", "Stopped"
        """
        if self._playback_status != status:
            self._playback_status = status
            self.PropertiesChanged(
                self.MPRIS_PLAYER_IFACE,
                {'PlaybackStatus': status},
                []
            )
            logger.info(f"Playback status updated to: {status}")
    
    def update_metadata(self, track_info):
        """
        更新曲目元数据
        
        Args:
            track_info: 字典,包含 title, artist, album, length 等
        """
        metadata = {
            'mpris:trackid': dbus.ObjectPath(f'/org/biliplayer/track/{track_info.get("id", "0")}'),
            'xesam:title': track_info.get('title', 'Unknown'),
            'xesam:artist': dbus.Array([track_info.get('artist', 'BiliBili')], signature='s'),
            'xesam:album': track_info.get('album', 'BiliBili Music'),
            'mpris:length': dbus.Int64(track_info.get('length', 0) * 1000000),  # 转换为微秒
        }
        
        # 可选字段
        if 'cover_url' in track_info:
            metadata['mpris:artUrl'] = track_info['cover_url']
        
        if 'url' in track_info:
            metadata['xesam:url'] = track_info['url']
        
        self._metadata = metadata
        self.PropertiesChanged(
            self.MPRIS_PLAYER_IFACE,
            {'Metadata': dbus.Dictionary(metadata, signature='sv')},
            []
        )
        logger.info(f"Metadata updated: {track_info.get('title', 'Unknown')}")
    
    def update_position(self, position_seconds):
        """
        更新播放位置
        
        Args:
            position_seconds: 播放位置（秒）
        """
        self._position = int(position_seconds * 1000000)  # 转换为微秒
        self.Seeked(self._position)


class MPRISController:
    """
    MPRIS 控制器主类
    管理 D-Bus 连接和事件循环
    """
    
    def __init__(self, callback_handler):
        """
        初始化控制器
        
        Args:
            callback_handler: 播放器回调处理器
        """
        self.callback = callback_handler
        self.interface = None
        self.loop = None
        self.thread = None
        self._running = False
    
    def start(self):
        """启动 MPRIS 服务"""
        try:
            # 初始化 D-Bus 主循环
            DBusGMainLoop(set_as_default=True)
            
            # 获取会话总线
            bus = dbus.SessionBus()
            
            # 请求总线名称
            bus_name = dbus.service.BusName(
                'org.mpris.MediaPlayer2.biliplayer',
                bus=bus
            )
            
            # 创建 MPRIS 接口
            self.interface = MPRISInterface(bus_name, self.callback)
            
            # 创建 GLib 主循环
            self.loop = GLib.MainLoop()
            
            # 在独立线程中运行事件循环
            self._running = True
            self.thread = threading.Thread(target=self._run_loop, daemon=True)
            self.thread.start()
            
            logger.info("MPRIS controller started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start MPRIS controller: {e}")
            return False
    
    def _run_loop(self):
        """运行 GLib 主循环"""
        try:
            self.loop.run()
        except Exception as e:
            logger.error(f"Error in MPRIS event loop: {e}")
    
    def stop(self):
        """停止 MPRIS 服务"""
        self._running = False
        if self.loop:
            self.loop.quit()
        if self.thread:
            self.thread.join(timeout=2)
        logger.info("MPRIS controller stopped")
    
    # ==================== 便捷方法 ====================
    
    def update_status(self, status):
        """更新播放状态"""
        if self.interface:
            self.interface.update_playback_status(status)
    
    def update_track(self, track_info):
        """更新曲目信息"""
        if self.interface:
            self.interface.update_metadata(track_info)
    
    def update_position(self, position):
        """更新播放位置"""
        if self.interface:
            self.interface.update_position(position)


# ==================== 示例回调处理器 ====================

class PlaybackCallbackHandler:
    """
    播放回调处理器示例
    你需要在实际项目中实现这些方法
    """
    
    def __init__(self):
        self.is_playing = False
    
    def play_pause(self):
        """播放/暂停切换"""
        self.is_playing = not self.is_playing
        return "Playing" if self.is_playing else "Paused"
    
    def play(self):
        """播放"""
        self.is_playing = True
    
    def pause(self):
        """暂停"""
        self.is_playing = False
    
    def stop(self):
        """停止"""
        self.is_playing = False
    
    def next(self):
        """下一曲"""
        print("Next track")
    
    def previous(self):
        """上一曲"""
        print("Previous track")
    
    def seek(self, offset_seconds):
        """相对定位"""
        print(f"Seek {offset_seconds} seconds")
    
    def set_position(self, position_seconds):
        """绝对定位"""
        print(f"Set position to {position_seconds} seconds")
    
    def set_volume(self, volume):
        """设置音量"""
        print(f"Set volume to {volume}")
    
    def quit(self):
        """退出"""
        print("Quit requested")


# ==================== 测试代码 ====================

if __name__ == '__main__':
    import time
    
    # 创建回调处理器
    handler = PlaybackCallbackHandler()
    
    # 创建并启动 MPRIS 控制器
    controller = MPRISController(handler)
    
    if controller.start():
        print("MPRIS service started. Testing...")
        
        # 模拟播放
        controller.update_track({
            'id': '1',
            'title': '测试歌曲',
            'artist': 'BiliBili',
            'album': 'Test Album',
            'length': 240,  # 4分钟
        })
        
        controller.update_status("Playing")
        
        # 模拟播放进度
        for i in range(10):
            controller.update_position(i * 10)
            time.sleep(1)
        
        print("Test completed. Press Ctrl+C to exit...")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping...")
            controller.stop()
    else:
        print("Failed to start MPRIS service")