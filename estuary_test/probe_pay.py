#!/usr/bin/env python3
"""probe_pay.py -- Credit/Debit Card dabane ke BAAD panne par hai kya, ye naapo.

    python probe_pay.py
    python probe_pay.py --pack "Pack of 04" --product black-white-ginger-ale

KYUN CHAHIYE
------------
Magzter/casino wali script me card ke khaane seedhe `input#cardNumber`,
`#cardExpiry`, `#cardCvc` the -- Stripe ka apna panna, id pehle se maloom.
Yahan wo baat nahi hai: Estuary ka checkout Shiprocket ka hai
(fastrr-boost-ui.pickrr.com), aur usme Easebuzz ka gateway EK AUR iframe ke
andar khulta hai. Uske khaano ki id/name kisi ko maloom nahi -- tasveer me
sirf grey patti (skeleton) dikhi thi kyunki wo abhi load ho raha tha.

To pehle naapa jaata hai: card dabane ke baad har frame, har khaana, har
button -- 90 second tak baar baar. Jo mila wo `out/pay_probe.txt` me jaata
hai. Usi ke baad card bharne ka kadam likha jayega -- andaze se nahi.

Ye script kuch BHARTI NAHI hai. Sirf dekhti hai aur likh deti hai.
"""
import os
import sys
import json
import time
import argparse

from playwright.sync_api import sync_playwright

import place_order as po

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
SHOP = "https://estuaryworld.com"
os.makedirs(OUT, exist_ok=True)

REPORT = open(os.path.join(OUT, "pay_probe.txt"), "w", encoding="utf-8")


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    REPORT.write(s + "\n")
    REPORT.flush()


def dump_frames(page, tag):
    """Har frame ka poora naksha: url, aur usme dikhne wale khaane/button.

    `:visible` par zor hai. Checkout ke DOM me chhupe hue khaane pade rehte
    hain (pata wale form ka `#email` isi tarah dhokha de chuka hai), aur unhe
    ginne se galat nateeja nikalta hai.
    """
    log("\n" + "=" * 70)
    log("[%s]  URL: %s" % (tag, (page.url or "")[:110]))
    log("=" * 70)
    for i, fr in enumerate(page.frames):
        u = (fr.url or "")[:100]
        try:
            body = (fr.locator("body").inner_text() or "").strip()
        except Exception as e:
            log("  frame %-2d %s  -> padha nahi gaya (%s)" % (i, u, str(e)[:50]))
            continue
        try:
            fields = fr.locator("input:visible, select:visible, textarea:visible"
                                ).evaluate_all(
                "els => els.map(e => e.tagName"
                " + ' id=' + (e.id || '-')"
                " + ' name=' + (e.name || '-')"
                " + ' type=' + (e.type || '-')"
                " + ' ph=' + (e.placeholder || '-')"
                " + ' aria=' + (e.getAttribute('aria-label') || '-')"
                " + ' maxlen=' + (e.maxLength > 0 ? e.maxLength : '-'))")
        except Exception:
            fields = []
        try:
            btns = fr.locator("button:visible, [role=button]:visible"
                              ).evaluate_all(
                "els => els.map(e => (e.textContent||'').trim().slice(0,40)"
                "                    + ' /id=' + (e.id||'-'))")
        except Exception:
            btns = []

        # Jis frame me na khaana hai na likha hua kuch -- use chhod do.
        if not fields and not btns and len(body) < 40:
            continue
        log("\n  --- frame %d : %s" % (i, u))
        if body:
            flat = " | ".join(l.strip() for l in body.splitlines() if l.strip())
            log("      likha hai : %s" % flat[:400])
        for f in fields[:25]:
            log("      KHAANA    : %s" % f[:150])
        for bt in btns[:15]:
            if bt.strip(" /id=-"):
                log("      BUTTON    : %s" % bt[:100])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--product", default="black-white-ginger-ale")
    ap.add_argument("--pack", default="Pack of 04")
    ap.add_argument("--session", default="")
    ap.add_argument("--watch", type=int, default=90,
                    help="card dabane ke baad itne second tak naapte raho")
    a = ap.parse_args()

    path = a.session or po.newest_session()
    if not path:
        log("koi session nahi mili -- pehle make_accounts.py chalao")
        return 1
    if not os.path.isabs(path):
        p2 = os.path.join(po.SESSIONS, path)
        path = p2 if os.path.exists(p2) else path
    d = json.load(open(path, encoding="utf-8"))
    log("account : %s / %s" % (d.get("phone"), d.get("email")))

    with sync_playwright() as p:
        b = p.chromium.launch(headless=False, args=["--start-maximized"])
        ctx = b.new_context(storage_state=d["state"], locale="en-IN",
                            viewport={"width": 1500, "height": 950})
        page = ctx.new_page()

        log("\n1) product : %s" % a.product)
        page.goto("%s/products/%s" % (SHOP, a.product),
                  wait_until="domcontentloaded", timeout=90000)
        page.wait_for_timeout(5000)
        po.pick(page, a.pack)

        log("2) add to cart")
        sel = po.find(page, po.ADD_TO_CART)
        if not sel:
            log("   FAIL: add to cart ka button nahi mila")
            b.close()
            return 2
        page.locator(sel).first.click()
        page.wait_for_timeout(6000)

        log("3) checkout")
        if not po.find(page, po.CHECKOUT):
            s2 = po.find(page, po.CART_OPEN)
            if s2:
                page.locator(s2).first.click()
                page.wait_for_timeout(5000)
        sel = po.find(page, po.CHECKOUT)
        if not sel:
            log("   FAIL: checkout ka button nahi mila")
            b.close()
            return 3
        newpage = None
        try:
            with ctx.expect_page(timeout=15000) as np:
                page.locator(sel).first.click()
            newpage = np.value
        except Exception:
            pass
        pay = newpage or page
        pay.wait_for_timeout(12000)

        log("4) pata : %s" % po.ship_address(pay, d))
        pay.wait_for_timeout(5000)
        log("5) email : %s" % po.confirm_email(pay, d))
        pay.wait_for_timeout(4000)

        # Card DABANE SE PEHLE ka naksha -- taki baad me pata chale ki naya
        # kya aaya. Warna Shiprocket ke apne frames aur Easebuzz ke frames
        # ghul-mil kar ek jaise dikhte hain.
        dump_frames(pay, "CARD DABANE SE PEHLE")

        log("\n6) Credit/Debit Card daba rahe hain")
        log("   %s" % po.pick_card(pay))

        # Easebuzz DHEERE aata hai. Tasveer me sirf grey patti dikhi thi --
        # matlab uska panna abhi khud ko bana raha tha. Isliye ek baar dekh kar
        # nateeja nikalna galat hai; har 15 second par dobara naapa jaata hai.
        end = time.time() + a.watch
        n = 0
        while time.time() < end:
            pay.wait_for_timeout(15000)
            n += 1
            dump_frames(pay, "CARD DABANE KE BAAD +%ds" % (n * 15))
            try:
                pay.screenshot(path=os.path.join(OUT, "pay_probe_%d.png" % n))
            except Exception as e:
                log("   (tasveer nahi bani: %s)" % str(e)[:60])

        log("\nnaksha likh diya: out/pay_probe.txt")
        log("tasveerein   : out/pay_probe_1.png ... _%d.png" % n)
        pay.wait_for_timeout(20000)
        try:
            b.close()
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
