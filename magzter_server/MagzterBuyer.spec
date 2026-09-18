# -*- mode: python ; coding: utf-8 -*-
# Magzter Buyer bot -> single portable exe (browser + creds config bundled).
# Build:  python -m PyInstaller --noconfirm MagzterBuyer.spec
# Chalane se pehle: config.json exe ke BAGAL me rakho (usme SHEET_ID + GOOGLE_CREDENTIALS
# + proxy/OTP sab hai). Browser exe ke ANDAR bundled hai -> 'playwright install' ki zaroorat nahi.

from PyInstaller.utils.hooks import collect_all

datas = []
binaries = []
hiddenimports = [
    # local modules
    'sheet_db', 'settings_util', 'fingerprint',
    # google sheets
    'gspread', 'google.oauth2', 'google.oauth2.service_account',
    'google.auth', 'google.auth.transport.requests',
    # browser + misc
    'playwright', 'playwright.sync_api', 'playwright._impl',
    'requests', 'charset_normalizer',
]

for pkg in ('playwright', 'charset_normalizer', 'gspread', 'google.auth'):
    d, b, h = collect_all(pkg)
    datas += d
    binaries += b
    hiddenimports += h

a = Analysis(
    ['buyer.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'pandas', 'numpy', 'PIL', 'torch', 'transformers',
              'selenium', 'tkinter', 'scipy', 'IPython'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MagzterBuyer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
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
    upx=False,
    upx_exclude=[],
    name='MagzterBuyer',
)
