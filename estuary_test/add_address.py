#!/usr/bin/env python3
"""add_address.py -- account par ek delivery ka pata jodo.

Order lagne se pehle account par pata hona zaroori hai. Ye script wahi ek kaam
karti hai: saved session se account kholo, "Add new address" ka form bharo, aur
sach me jud gaya ya nahi -- ye page se hi padh kar batao.

PINCODE SE SHEHAR AUR RAJYA
---------------------------
Shopify ka rajya wala dropdown country chunne par hi bharta hai, aur pincode se
apne aap kuch nahi hota. Isliye teenon (pincode, shehar, rajya) yahin ek jagah
likhe hain -- 000000 Kanpur, Uttar Pradesh ka hai.

    python add_address.py                       # sabse nayi session par
    python add_address.py --session <file>
    python add_address.py --pincode 000000
"""
import os
import re
import sys
import glob
import json
import random
import argparse

from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
SESSIONS = os.path.join(HERE, "sessions")
OUT = os.path.join(HERE, "out")
ACCOUNT = "https://estuaryworld.com/account"
os.makedirs(OUT, exist_ok=True)

# Pincode -> (shehar, rajya). Naya pincode chahiye to yahin ek line jodni hai.
PINS = {
    "000000": ("Kanpur", "Uttar Pradesh"),
    "208014": ("Kanpur", "Uttar Pradesh"),
}

STREETS = ["Saket Nagar", "Shastri Nagar", "Kakadeo", "Govind Nagar",
           "Arya Nagar", "Kidwai Nagar", "Ratan Lal Nagar"]


def log(*a):
    print(*a, flush=True)


def newest_session():
    fs = sorted(glob.glob(os.path.join(SESSIONS, "*.json")), key=os.path.getmtime)
    return fs[-1] if fs else None


def dummy(email, phone, pin):
    city, state = PINS.get(pin, ("Kanpur", "Uttar Pradesh"))
    base = re.split(r"[._\d]", (email or "user").split("@")[0])
    first = (base[0] or "Ishan").capitalize()
    last = (base[1] if len(base) > 1 and base[1] else "Gupta").capitalize()
    return {
        "first_name": first,
        "last_name": last,
        "company": "",
        "address1": "CHANGE_ME_ADDR1" % (random.randint(10, 199), random.randint(1, 99),
                                  random.choice(STREETS)),
        "address2": "CHANGE_ME_ADDR2" % random.choice(STREETS),
        "city": city,
        "country": "India",
        "province": state,
        "zip": pin,
        "phone": phone or "9%09d" % random.randint(0, 999999999),
    }


def add(page, a):
    btn = page.locator("button:has-text('Add new address')")
    if not btn.count():
        return False, "'Add new address' ka button hi nahi mila"
    btn.first.click()
    page.wait_for_timeout(2500)

    page.fill("#address_first_name_new", a["first_name"])
    page.fill("#address_last_name_new", a["last_name"])
    page.fill("#address_address1_new", a["address1"])
    page.fill("#address_address2_new", a["address2"])
    page.fill("#address_city_new", a["city"])

    # KRAM MAAYNE RAKHTA HAI. Rajya ka dropdown country chunne par hi bharta
    # hai -- pehle rajya chunne ki koshish karne par wo list khaali hoti hai.
    page.select_option("#address_country_new", a["country"])
    page.wait_for_timeout(1500)

    # RAJYA KA DROPDOWN IS PANNE PAR KHAALI REHTA HAI.
    #
    # Naap kar dekha: India chunne ke BAAD bhi us select me 0 option hain aur
    # uska dabba `display:none` hai -- theme ki wo JS chalti hi nahi jo rajye
    # bharti hai. Isliye `select_option` wahan hamesha timeout deta hai (30
    # second, aur kuch nahi hota).
    #
    # To rajya ka naam khud daal kar chun liya jaata hai. Ye "dhoka" nahi hai:
    # form ko wahi value jaati hai jo aadmi dropdown se chunne par jaati, aur
    # `change` bhi bheja jaata hai taaki theme ko pata chale.
    n = page.locator("#address_province_new").evaluate("e => e.options.length")
    if n:
        page.select_option("#address_province_new", a["province"])
    else:
        page.evaluate(
            """(v) => {
                 const s = document.querySelector('#address_province_new');
                 if (!s) return;
                 let o = [...s.options].find(x => x.value === v);
                 if (!o) { o = document.createElement('option');
                           o.value = v; o.text = v; s.add(o); }
                 s.value = v;
                 s.dispatchEvent(new Event('change', {bubbles: true}));
               }""", a["province"])
        log("      (rajya ka dropdown khaali tha -- naam khud daala)")

    page.fill("#address_zip_new", a["zip"])
    page.fill("#address_phone_new", a["phone"])

    # Pehla pata default bhi hona chahiye, warna checkout par chunna padta hai.
    try:
        box = page.locator("#address_default_address_new")
        if box.count() and not box.is_checked():
            box.check()
    except Exception:
        pass

    page.screenshot(path=os.path.join(OUT, "address_filled.png"), full_page=True)

    # "Add Address" ka BUTTON dabane se form jaata hi nahi.
    #
    # Naap kar dekha: button dabane par ek POST gaya, par `/cart/add` par --
    # `/account/addresses` par kuch nahi. Yaani panne ki apni JS us click ko
    # pakad leti hai. Form khud bilkul theek hai (action=/account/addresses,
    # method=post, kisi doosre form ke andar nahi).
    #
    # Isliye form SEEDHA submit kiya jaata hai. Ye koi chor rasta nahi -- wahi
    # POST jaata hai jo button dabane par jaana chahiye tha, aur uske baad
    # panna sach me /account/addresses par pahunchta hai.
    try:
        with page.expect_navigation(timeout=30000):
            page.evaluate("() => document.querySelector('#address_form_new').submit()")
    except Exception as e:
        return False, "form bheja nahi ja saka (%s)" % str(e)[:70]
    page.wait_for_timeout(4000)
    return True, ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--session", default="")
    ap.add_argument("--pincode", default="000000")
    ap.add_argument("--headless", action="store_true")
    a = ap.parse_args()

    path = a.session or newest_session()
    if not path:
        log("koi session file nahi mili -- pehle make_accounts.py chalao")
        return 1
    if not os.path.isabs(path):
        p2 = os.path.join(SESSIONS, path)
        path = p2 if os.path.exists(p2) else path
    d = json.load(open(path, encoding="utf-8"))
    log("session : %s" % os.path.basename(path))
    log("account : %s / %s" % (d.get("phone"), d.get("email")))

    info = dummy(d.get("email"), d.get("phone"), a.pincode)
    log("pata    : %s, %s, %s, %s - %s"
        % (info["address1"], info["address2"], info["city"],
           info["province"], info["zip"]))

    with sync_playwright() as p:
        b = p.chromium.launch(headless=a.headless)
        ctx = b.new_context(storage_state=d["state"], locale="en-IN",
                            viewport={"width": 1400, "height": 950})
        page = ctx.new_page()
        page.goto(ACCOUNT, wait_until="domcontentloaded", timeout=90000)
        page.wait_for_timeout(6000)

        if "login" in page.url:
            log("FAIL: session mar chuki hai -- login ka panna khul gaya")
            b.close()
            return 2

        ok, why = add(page, info)
        if not ok:
            log("FAIL: %s" % why)
            page.screenshot(path=os.path.join(OUT, "address_fail.png"), full_page=True)
            b.close()
            return 3

        # JUDA YA NAHI -- PAGE SE POOCHHO. Form submit ho jaana kaamyaabi nahi
        # hai; pata list me dikhna kaamyaabi hai.
        #
        # List /account par nahi, /account/addresses par dikhti hai -- account
        # wale panne ka "Addresses" dabba is theme me khaali hi rehta hai.
        page.goto("https://estuaryworld.com/account/addresses",
                  wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(5000)
        try:
            txt = page.inner_text("body") or ""
        except Exception:
            txt = ""
        added = info["zip"] in txt and info["city"].lower() in txt.lower()
        log("\npata jud gaya: %s" % added)
        if added:
            for line in [l.strip() for l in txt.splitlines() if info["zip"] in l]:
                log("   panne par: %s" % line[:110])
        page.screenshot(path=os.path.join(OUT, "address_done.png"), full_page=True)
        log("tasveer: out/address_done.png")

        # Session me pata judne ke baad cookies badal sakti hain -- wapas likh
        # do, warna agla kadam purani session se chalega.
        try:
            d["state"] = ctx.storage_state()
            d["address"] = info
            json.dump(d, open(path, "w", encoding="utf-8"),
                      ensure_ascii=False, indent=1)
            log("session file me pata bhi likh diya")
        except Exception as e:
            log("(session wapas nahi likhi: %s)" % str(e)[:70])

        page.wait_for_timeout(1500)
        b.close()
    return 0 if added else 4


if __name__ == "__main__":
    sys.exit(main())
