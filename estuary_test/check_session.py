"""check_session.py -- saved session sach me chalti hai ya nahi.

Cookies file me hona ek baat hai; un cookies se account ka panna KHUL jaana
doosri. Ye script sirf wahi doosri baat jaanchti hai: ek bilkul naya browser
kholo, sirf saved cookies daalo, aur /account par jaakar dekho ki Nykaa jaisa
"login karo" wapas to nahi bhej raha.

    python check_session.py                 # sabse nayi session
    python check_session.py <file.json>
"""
import os
import sys
import json
import glob

from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
SESSIONS = os.path.join(HERE, "sessions")
ACCOUNT_URL = "https://estuaryworld.com/account"


def newest():
    fs = sorted(glob.glob(os.path.join(SESSIONS, "*.json")), key=os.path.getmtime)
    return fs[-1] if fs else None


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else newest()
    if not path:
        print("koi session file nahi mili")
        return 1
    if not os.path.isabs(path):
        p2 = os.path.join(SESSIONS, path)
        path = p2 if os.path.exists(p2) else path

    d = json.load(open(path, encoding="utf-8"))
    print("file   :", os.path.basename(path))
    print("number :", d.get("phone"))
    print("email  :"test@example.com"email"))
    print("cookies:", len(d.get("state", {}).get("cookies", [])))

    with sync_playwright() as p:
        b = p.chromium.launch(headless=False)
        ctx = b.new_context(storage_state=d["state"], locale="en-IN")
        page = ctx.new_page()
        page.goto(ACCOUNT_URL, wait_until="domcontentloaded", timeout=90000)
        page.wait_for_timeout(6000)
        print("\nURL    :", page.url)
        try:
            txt = page.inner_text("body") or ""
        except Exception:
            txt = ""
        lines = [l.strip() for l in txt.splitlines() if l.strip()][:14]
        for l in lines:
            print("   ", l[:90])
        low = txt.lower()
        live = ("/account" in page.url and "login" not in page.url) or \
               any(w in low for w in ("logout", "log out", "my orders"))
        print("\nsession zinda hai:", live)
        page.screenshot(path=os.path.join(HERE, "out", "session_check.png"))
        page.wait_for_timeout(2000)
        b.close()
    return 0 if live else 1


if __name__ == "__main__":
    sys.exit(main())
