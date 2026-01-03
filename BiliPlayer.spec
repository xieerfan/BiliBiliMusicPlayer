# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import copy_metadata

block_cipher = None

# 保持元数据修复
datas = copy_metadata('readchar')
# 增加 bilibili-api 的元数据以防万一
datas += copy_metadata('bilibili-api-python')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'bilibili_api',
        'bilibili_api.clients', # 增加这一行
        'bilibili_api.clients.CurlCFFIClient', # 显式指定报错缺失的模块
        'curl_cffi',
        'curl_cffi.requests',
        'rich.logging',
        'readchar.backends',
        'readchar.backends.linux',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='biliplayer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,     # 去除符号表，减小体积
    upx=True,       # 如果你安装了 upx，它会帮你压缩到更小
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)