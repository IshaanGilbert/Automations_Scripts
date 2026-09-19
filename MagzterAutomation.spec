# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['mag.py'],
    pathex=[],
    binaries=[],
    datas=[('google_credentials.json', '.'), ('config.json', '.')],
    hiddenimports=['playwright.sync_api', 'gspread', 'google.oauth2.service_account', 'google.auth.transport.requests'],
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
    [],
    exclude_binaries=True,
    name='MagzterAutomation',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
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
    upx=True,
    upx_exclude=[],
    name='MagzterAutomation',
)
