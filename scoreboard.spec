# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
import nicegui


a = Analysis(
    ['scoreboard\\main.py'],
    pathex=[],
    binaries=[],
    datas=[
        (f'{Path(nicegui.__file__).parent}', 'nicegui'),
        ('scoreboard/emoji_events.ico', 'scoreboard')
    ],
    hiddenimports=['tortoise.backends.sqlite'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='scoreboard',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['scoreboard\\emoji_events.ico'],
)
