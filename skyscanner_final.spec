# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

# --- Playwright package (driver: node.exe + cli.js + package/) ---
# NOTE: we do NOT bundle a Chromium here. skyscanner_final.py uses the system's
# real Google Chrome (channel="chrome") to pass PerimeterX, so the target
# machine only needs Google Chrome installed.
pw_datas, pw_binaries, pw_hiddenimports = collect_all("playwright")

datas = pw_datas

block_cipher = None

a = Analysis(
    ["skyscanner_final.py"],
    pathex=[],
    binaries=pw_binaries,
    datas=datas,
    hiddenimports=pw_hiddenimports + ["tkinter", "tkinter.ttk", "tkinter.scrolledtext", "tkinter.messagebox"],
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
    [],
    exclude_binaries=True,
    name="SkyscannerBot",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,           # GUI app -> no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="SkyscannerBot",
)
