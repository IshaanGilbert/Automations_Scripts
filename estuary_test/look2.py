"""look2.py -- popup ek IFRAME ke andar hai, uske andar jhaanko.

Panne par `#mobile` mila hi nahi tha, aur wajah ye nikli: login ka popup
Shiprocket ka apna widget hai jo ek iframe me chalta hai
(`fastrr-boost-ui.pickrr.com`). Isliye har selector us frame ke andar dhoondhna
padega, panne par nahi.
"""
import os
import sys
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

URL = "https://estuaryworld.com/account/login?return_url=%2Faccount"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT, exist_ok=True)
POPUP = "shiprocketLogin"


def main():
    with sync_playwright() as p:
        b = p.chromium.launch(headless=False, args=["--start-maximized"])
        ctx = b.new_context(viewport=None, locale="en-IN")
        page = ctx.new_page()
        page.goto(URL, wait_until="domcontentloaded", timeout=90000)
        page.wait_for_timeout(8000)

        f = None
        for fr in page.frames:
            if POPUP in (fr.url or ""):
                f = fr
                break
        if not f:
            print("login wala frame mila hi nahi. Saare frame:")
            for fr in page.frames:
                print("   ", fr.url[:110])
            b.close()
            return

        print("frame:", f.url[:120])
        print("\n--- frame ke andar input ---")
        for h in f.locator("input").evaluate_all(
                "els => els.map(e => e.outerHTML.slice(0,170))"):
            print("   ", h)

        print("\n--- frame ke andar button/span jinpar likha ho ---")
        for h in f.locator("button, span[class*='Login'], div[role='button']").evaluate_all(
                "els => els.map(e => (e.tagName+' | '+(e.className||'')+' | '"
                "+(e.textContent||'').trim().slice(0,40)))"):
            if h.strip():
                print("   ", h[:150])

        for sel in ("#mobile", "span.Login_inputAddonRight__ptvZb",
                    "input[autocomplete='one-time-code']"):
            print("   %-42s -> %s" % (sel, f.locator(sel).count()))

        page.screenshot(path=os.path.join(OUT, "look2.png"))
        print("\ntasveer: out/look2.png")
        page.wait_for_timeout(3000)
        b.close()


if __name__ == "__main__":
    main()
