# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['dexsport.py'],
    pathex=[],
    binaries=[],
    datas=[('firefox_portable', 'firefox_portable'), ('geckodriver-v0.36.0-win64', 'geckodriver-v0.36.0-win64')],
    hiddenimports=['selenium.webdriver.firefox.webdriver', 'selenium.webdriver.chrome.webdriver', 'selenium.webdriver.edge.webdriver', 'selenium.webdriver.safari.webdriver', 'seleniumwire'],
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
    name='dexsport',
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
    name='dexsport',
)
