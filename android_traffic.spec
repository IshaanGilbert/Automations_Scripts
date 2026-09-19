# -*- mode: python ; coding: utf-8 -*-
# Portable build for android_traffic.py
#
# Produces dist/AndroidTrafficBot/ -> a self-contained folder that runs on any
# Windows 10/11 machine with NOTHING installed (no Python, no Playwright, no
# Chrome). Chromium ships inside the folder under ms-playwright/.
#
# Build:  pyinstaller android_traffic.spec --noconfirm
import os
from PyInstaller.utils.hooks import collect_all

# --- Playwright package (driver: node.exe + cli.js + package/) ---
pw_datas, pw_binaries, pw_hiddenimports = collect_all("playwright")

# NOTE: playwright/driver/package/.local-browsers is a SECOND full copy of
# Chromium (~650 MB). Filtering it here does not help - Playwright ships its own
# PyInstaller hook (playwright/_impl/__pyinstaller) that re-adds every data file
# via collect_data_files(). It is deleted from dist/ after COLLECT instead;
# see the cleanup at the bottom of this file.

# --- Bundle the Chromium browsers next to the exe under ms-playwright/ ---
# 1208 is the build Playwright 1.58 expects. chromium = headed runs,
# chromium_headless_shell = the "Headless" checkbox.
LOCAL = os.environ["LOCALAPPDATA"]
MS = os.path.join(LOCAL, "ms-playwright")
BROWSERS = ["chromium-1208", "chromium_headless_shell-1208"]

browser_datas = []
for b in BROWSERS:
    src = os.path.join(MS, b)
    if os.path.isdir(src):
        browser_datas.append((src, os.path.join("ms-playwright", b)))
    else:
        raise SystemExit(f"Missing browser {src} - run: python -m playwright install chromium")

datas = pw_datas + browser_datas

# Keep the build small/fast: none of these are used by the bot.
EXCLUDES = [
    "numpy", "pandas", "matplotlib", "scipy", "PIL", "cv2", "torch",
    "transformers", "selenium", "IPython", "notebook", "pytest",
    "sqlalchemy", "bs4", "lxml", "requests", "urllib3", "cryptography",
]

block_cipher = None

a = Analysis(
    ["android_traffic.py"],
    pathex=[],
    binaries=pw_binaries,
    datas=datas,
    hiddenimports=pw_hiddenimports + [
        "tkinter", "tkinter.ttk", "tkinter.scrolledtext", "tkinter.messagebox",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=EXCLUDES,
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
    name="AndroidTrafficBot",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,                # UPX would slow every start-up; keep it off
    console=False,            # GUI app -> no black console window
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
    name="AndroidTrafficBot",
)

# --- Post-build cleanup -------------------------------------------------
# COLLECT has finished copying, so now drop the duplicate Chromium that
# Playwright's own hook pulled in. We ship our own copy under ms-playwright/
# and _configure_bundled_browsers() points PLAYWRIGHT_BROWSERS_PATH at it,
# so this copy is never read. Saves ~650 MB.
import shutil

_dup = os.path.join(DISTPATH, "AndroidTrafficBot", "_internal",
                    "playwright", "driver", "package", ".local-browsers")
if os.path.isdir(_dup):
    shutil.rmtree(_dup, ignore_errors=True)
    print(f"[spec] removed duplicate browsers: {_dup}")
