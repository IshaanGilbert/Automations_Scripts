# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

# creds exe ke saath dist folder me chali jayengi (script wahin se padhta hai)
datas = [
    ('creds1.json', '.'), ('creds2.json', '.'), ('creds3.json', '.'),
    ('creds4.json', '.'), ('creds5.json', '.'), ('creds6.json', '.'),
    ('google_credentials.json', '.'),
]
binaries = []
hiddenimports = [
    'playwright', 'playwright.async_api', 'playwright._impl',
    'gspread', 'google.oauth2', 'google.oauth2.service_account',
    'google.auth', 'google.auth.transport.requests',
    'charset_normalizer',
]

for pkg in ('playwright', 'charset_normalizer', 'gspread', 'google.auth'):
    d, b, h = collect_all(pkg)
    datas += d
    binaries += b
    hiddenimports += h

a = Analysis(
    ['magzter_orders.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'pandas', 'numpy', 'PIL', 'torch', 'transformers', 'selenium', 'tkinter'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MagzterOrders',
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
    name='MagzterOrders',
)
