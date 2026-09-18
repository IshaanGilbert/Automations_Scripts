# -*- mode: python ; coding: utf-8 -*-
"""EstuaryAccountCreator -- account banane wali exe.

Ye spec isliye likhi gayi hai (seedha `pyinstaller script.py` ke bajaye) kyunki
exe ko doosre system par chalne ke liye teen bahari cheezein chahiye, aur unka
faisla yahin ek jagah hona chahiye:

    geckodriver.exe   -- 4 MB, HAMESHA exe ke andar chala jaata hai
    google_creds.json -- Sheet ka service account (WITH_CREDS)
    Waterfox\\         -- 311 MB ka poora browser (WITH_WATERFOX)

Waterfox ko andar rakhne par exe ~320 MB ka ho jaata hai par kisi bhi system
par bina kuch rakhe chal jaata hai. Bahar rakhne par exe ~40 MB ka rehta hai,
par uske BAGAL me Waterfox folder rakhna padta hai. Neeche do switch hain --
jo chahiye wo True/False kar do.

BANANA
    pyinstaller --noconfirm EstuaryAccountCreator.spec
    # nateeja: dist\\EstuaryAccountCreator\\EstuaryAccountCreator.exe
"""
import os
import json

from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Selenium apne webdriver ko naam se (import string bana kar) uthata hai, isliye
# PyInstaller khud dekh kar nahi samajh pata ki kaun kaun se hisse chahiye.
# Pehli build me theek yahi hua tha:
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

# Sheet ke credentials: magzter ke config me se sirf service-account nikaal kar
# ek alag file bana lete hain -- poora config (DB password waghairah) exe me
# daalne ki koi zaroorat nahi.
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

# products_check.json -- cart banane wali logic isi se daam padhti hai
pc = os.path.join(HERE, "products_check.json")
if os.path.isfile(pc):
    datas.append((pc, "."))

# poora browser
if WITH_WATERFOX and os.path.isdir(WATERFOX_DIR):
    datas.append((WATERFOX_DIR, "Waterfox"))
elif WITH_WATERFOX:
    print("!! Waterfox folder nahi mila:", WATERFOX_DIR)


a = Analysis(
    ["account_gui.py"],
    pathex=[HERE],
    binaries=[],
    datas=datas,
    hiddenimports=AUTO_HIDDEN + [
        "place_order",
        "sheet_log",
        "otpd",
        "cart_build",
        "make_accounts_wf",
        "tkinter",
        "tkinter.ttk",
        "tkinter.messagebox",
    ],
    hookspath=[],
    runtime_hooks=[],
    # bhaari cheezein jinka is kaam se koi lena dena nahi
    # tkinter ab chahiye (GUI) -- excludes me se hata diya
    excludes=["matplotlib", "numpy", "pandas", "PIL",
              "playwright", "PyQt5", "PySide2", "notebook", "scipy"],
    noarchive=False,
)

pyz = PYZ(a.pure)

# onedir rakha hai, onefile nahi: onefile har chalane par 300 MB temp me
# kholta hai -- shuruaat slow aur antivirus bhi bidakta hai. onedir me exe
# turant khulta hai aur sessions/accounts.csv usi folder me dikhte hain.
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="EstuaryAccountCreator",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    # GUI hai, isliye console nahi. Har line window ke log me aur gui_log.txt
    # me jaati hai -- console na hone par bhi kuch chhupta nahi.
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
    name="EstuaryAccountCreator",
)
