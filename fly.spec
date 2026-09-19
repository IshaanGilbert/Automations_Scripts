# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_all

# --- Playwright package (driver: node.exe + cli.js + package/) ---
pw_datas, pw_binaries, pw_hiddenimports = collect_all("playwright")

# --- Bundle the Chromium browsers next to the exe under ms-playwright/ ---
LOCAL = os.environ["LOCALAPPDATA"]
MS = os.path.join(LOCAL, "ms-playwright")
BROWSERS = ["chromium-1208", "chromium_headless_shell-1208"]

browser_datas = []
for b in BROWSERS:
    src = os.path.join(MS, b)
    if os.path.isdir(src):
        browser_datas.append((src, os.path.join("ms-playwright", b)))

datas = pw_datas + browser_datas

block_cipher = None

a = Analysis(
    ["fly.py"],
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
    name="FlyBot",
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
    name="FlyBot",
)
