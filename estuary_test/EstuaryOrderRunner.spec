# -*- mode: python ; coding: utf-8 -*-
"""EstuaryOrderRunner -- order lagane wali exe.

Ye teesri exe hai. Baaki do account banati hain (mobile+OTP wali aur email
wali); ye unke banaye hue accounts se ORDER lagati hai. Teeno alag hain, alag
folder me banti hain, aur ek doosre ko chhedti nahi.

User se sirf links, cart ki hadd, ginti aur phone poochhe jaate hain -- baaki
sab sheet se aata hai (pata, discount code, card) aur har lage order ka record
'Order_Records' tab me jaata hai.

Doosre system par chalne ke liye teen bahari cheezein chahiye, aur unka faisla
yahin ek jagah hota hai:

    geckodriver.exe   -- 4 MB, HAMESHA exe ke andar
    google_creds.json -- Sheet ka service account (WITH_CREDS)
    Waterfox\\         -- 311 MB ka poora browser (WITH_WATERFOX)

BANANA
    pyinstaller --noconfirm EstuaryOrderRunner.spec
    # nateeja: dist\\EstuaryEmailAccounts\\EstuaryEmailAccounts.exe
"""
import os
import json

from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Selenium apne webdriver ko naam se (import string bana kar) uthata hai, isliye
# PyInstaller khud dekh kar nahi samajh pata ki kaun kaun se hisse chahiye --
# pehli baar theek yahi hua tha:
#     No module named 'selenium.webdriver.firefox.webdriver'
# Isliye selenium (aur gspread/google-auth) ke SAARE submodule haath se jode
# jaate hain -- guess nahi, poori list.
AUTO_HIDDEN = (collect_submodules("selenium")
               + collect_submodules("gspread")
               + collect_submodules("google.auth")
               + collect_submodules("google.oauth2"))

# ---------------- do faisle ----------------
WITH_WATERFOX = True     # False = Waterfox exe ke BAGAL me rakhna padega
WITH_CREDS = True        # False = google_creds.json exe ke BAGAL me rakhna padega

HERE = os.path.abspath(os.getcwd())
ROOT = os.path.dirname(HERE)                      # D:\streakads

WATERFOX_DIR = os.path.join(ROOT, "Waterfox")
GECKO = os.path.join(ROOT, "geckodriver-v0.36.0-win64", "geckodriver.exe")
MAGZTER_CFG = os.path.join(ROOT, "magzter-v3-server", "config.json")
CREDS_OUT = os.path.join(HERE, "google_creds.json")

# selenium apne saath kuch data files bhi rakhta hai (bidi ki json waghairah)
datas = collect_data_files("selenium")

# geckodriver -- ye hamesha andar. 4 MB hai aur iske bina kuch nahi chalta.
if os.path.isfile(GECKO):
    datas.append((GECKO, "."))
else:
    print("!! geckodriver.exe nahi mila:", GECKO)

# Sheet ke credentials
if WITH_CREDS:
    if not os.path.isfile(CREDS_OUT) and os.path.isfile(MAGZTER_CFG):
        try:
            cfg = json.load(open(MAGZTER_CFG, encoding="utf-8"))
            g = cfg.get("GOOGLE_CREDENTIALS")
            if g and g.get("private_key"):
                json.dump(g, open(CREDS_OUT, "w", encoding="utf-8"), indent=1)
                print("google_creds.json bana diya (magzter config se)")
        except Exception as e:
            print("!! credentials nahi nikale:", e)
    if os.path.isfile(CREDS_OUT):
        datas.append((CREDS_OUT, "."))
    else:
        print("!! google_creds.json nahi mila -- Sheet band rahegi")

# poora browser
if WITH_WATERFOX and os.path.isdir(WATERFOX_DIR):
    datas.append((WATERFOX_DIR, "Waterfox"))
elif WITH_WATERFOX:
    print("!! Waterfox folder nahi mila:", WATERFOX_DIR)


a = Analysis(
    ["order_gui.py"],
    pathex=[HERE],
    binaries=[],
    datas=datas,
    hiddenimports=AUTO_HIDDEN + [
        "place_order",
        "order_plan",
        "order_batch",
        "sheet_log",
        "tkinter",
        "tkinter.ttk",
        "tkinter.messagebox",
    ],
    hookspath=[],
    runtime_hooks=[],
    # bhaari cheezein jinka is kaam se koi lena dena nahi
    excludes=["matplotlib", "numpy", "pandas", "PIL",
              "playwright", "PyQt5", "PySide2", "notebook", "scipy"],
    noarchive=False,
)

pyz = PYZ(a.pure)

# onedir rakha hai, onefile nahi: onefile har chalane par 300 MB temp me
# kholta hai -- shuruaat slow aur antivirus bhi bidakta hai. onedir me exe
# turant khulta hai aur sessions/ usi folder me dikhta hai.
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="EstuaryOrderRunner",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    # GUI hai, isliye console nahi. Har line window ke log me aur
    # gui_log_order.txt me jaati hai -- console na hone par bhi kuch chhupta nahi.
    console=False,
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
    name="EstuaryOrderRunner",
)
