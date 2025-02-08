# -*- mode: python ; coding: utf-8 -*-

import sys
import os

# 获取图标路径
icon_path = os.path.join('resources', 'icon.ico' if sys.platform.startswith('win') else 'icon.icns')

a = Analysis(
    ['src/gui.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['PIL._tkinter_finder', 'PIL', 'dateutil', 'imagehash', 'exifread'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='PhotoOrganizer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path
)

if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='PhotoOrganizer.app',
        icon=icon_path,
        bundle_identifier='com.jessie.photoorganizer',
        info_plist={
            'LSMinimumSystemVersion': '10.12',
            'NSHighResolutionCapable': 'True',
        },
    )
