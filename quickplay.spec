# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['quickplay.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('./_internal/folders.txt', '.'),
        ('./_internal/quickplay.txt', '.'),
        ('./_internal/icon.ico', '.'),
        ('./_internal/icon.png', '.'),
        ('./_internal/styles.qss', '.'),
    ],
    hiddenimports=[],
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
    [],
    exclude_binaries=True,
    name='quickplay',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='./_internal/icon.ico',
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='quickplay',
)
