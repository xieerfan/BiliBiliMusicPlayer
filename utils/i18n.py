LANG_DICT = {
    "zh": {
        "playing": "播放中",
        "paused": "已暂停",
        "track_label": "曲目",
        "time_label": "时间",
        "library": "曲库",
        "tracks_unit": "首歌曲",
        "menu_1": "添加单曲 (BVID/URL)",
        "menu_2": "导入合集 (Season ID)",
        "menu_3": "管理现有歌单",
        "menu_4": "退出并保存",
        "select": "请选择操作",
        "input_prompt": ">> 输入:",
        "help_nav": "← → 翻页 | 输入范围后回车 | ESC 返回",
        "url_bvid": "请输入 URL 或 BVID",
        "sid": "请输入合集 Season ID",
        "empty": "歌单空空如也喵。",
        "save_exit": "配置已保存，再见！"
    },
    "en": {
        "playing": "PLAYING",
        "paused": "PAUSED",
        "track_label": "TRACK",
        "time_label": "TIME",
        "library": "Library",
        "tracks_unit": "tracks",
        "menu_1": "Add Single Track",
        "menu_2": "Import Collection",
        "menu_3": "Manage Playlist",
        "menu_4": "Exit & Save",
        "select": "Select Action",
        "input_prompt": ">> INPUT:",
        "help_nav": "← → Flip | Enter Range | ESC Back",
        "url_bvid": "Enter URL / BVID",
        "sid": "Enter Season ID",
        "empty": "Playlist is empty.",
        "save_exit": "Settings saved. Goodbye!"
    }
}

def get_text(key, lang="zh"):
    return LANG_DICT.get(lang, LANG_DICT["zh"]).get(key, key)