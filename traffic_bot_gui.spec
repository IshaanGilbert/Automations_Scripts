# -*- mode: python ; coding: utf-8 -*-
# Build:  pyinstaller --clean --noconfirm traffic_bot_gui.spec
# Output: dist\TrafficBot\TrafficBot.exe  (pura TrafficBot folder portable hai)

from PyInstaller.utils.hooks import collect_all

datas = []
binaries = []
hiddenimports = [
    # selenium webdrivers (frozen build me explicitly chahiye)
    'selenium.webdriver.chrome.webdriver',
    'selenium.webdriver.firefox.webdriver',
    'selenium.webdriver.edge.webdriver',
    'selenium.webdriver.safari.webdriver',
    'selenium.webdriver.remote.webdriver',
    # selenium-wire ke common runtime deps
    'blinker', 'brotli', 'h2', 'hpack', 'hyperframe',
    'kaitaistruct', 'wsproto', 'certifi', 'OpenSSL',
]

# selenium-wire + selenium ka sab kuch (CA cert, submodules, data files) grab karo
for pkg in ('seleniumwire', 'selenium'):
    d, b, h = collect_all(pkg)
    datas += d
    binaries += b
    hiddenimports += h

a = Analysis(
    ['traffic_bot_gui.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

# ---- Portable Firefox + geckodriver ko bundle karo (resource_path inhe dhundta hai) ----
a.datas += Tree('firefox_portable', prefix='firefox_portable')
a.datas += Tree('geckodriver-v0.36.0-win64', prefix='geckodriver-v0.36.0-win64')

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='TrafficBot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,          # GUI app -> koi caali console window nahi
    disable_windowed_traceback=False,
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
    name='TrafficBot',
)
