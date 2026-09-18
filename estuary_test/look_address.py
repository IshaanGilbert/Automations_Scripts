"""look_address.py -- address ka form kaisa hai, pehle dekho.

Bharne se pehle dekhna zaroori hai: form ke aadhe khaane (state, pincode, phone)
uss HTML me the hi nahi jo diya gaya, aur Shopify ka state wala dropdown country
chunne par hi bharta hai. Bina dekhe likhi hui script wahin toot-ti.
"""
import os
import sys
import glob
import json

from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
SESSIONS = os.path.join(HERE, "sessions")
ACCOUNT = "https://estuaryworld.com/account"


def newest():
    fs = sorted(glob.glob(os.path.join(SESSIONS, "*.json")), key=os.path.getmtime)
    return fs[-1] if fs else None


def main():
    f = newest()
    if not f:
        print("koi session nahi mili")
        return 1
    d = json.load(open(f, encoding="utf-8"))
    print("session:", os.path.basename(f), "|", d.get("email"))

    with sync_playwright() as p:
        b = p.chromium.launch(headless=False)
        ctx = b.new_context(storage_state=d["state"], locale="en-IN",
                            viewport={"width": 1400, "height": 950})
        page = ctx.new_page()
        page.goto(ACCOUNT, wait_until="domcontentloaded", timeout=90000)
        page.wait_for_timeout(6000)
        print("URL:", page.url)

        btn = page.locator("button:has-text('Add new address')")
        print("'Add new address' button:", btn.count())
        if btn.count():
            btn.first.click()
            page.wait_for_timeout(2500)

        print("\n--- form ke saare khaane ---")
        for h in page.locator("#address_form_new input, #address_form_new select,"
                              " #address_form_new textarea").evaluate_all(
                "els => els.map(e => e.tagName + ' | id=' + (e.id||'-')"
                " + ' | name=' + (e.name||'-') + ' | type=' + (e.type||'-'))"):
            print("   ", h)

        print("\n--- form ke button ---")
        for h in page.locator("#address_form_new button, #address_form_new input[type=submit]"
                              ).evaluate_all(
                "els => els.map(e => e.tagName + ' | ' + (e.type||'') + ' | '"
                " + (e.textContent||e.value||'').trim().slice(0,40))"):
            print("   ", h)

        page.screenshot(path=os.path.join(HERE, "out", "address_form.png"),
                        full_page=True)
        print("\ntasveer: out/address_form.png")
        page.wait_for_timeout(2000)
        b.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
