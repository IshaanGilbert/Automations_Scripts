#!/usr/bin/env python3
"""probe_card.py -- SAHI card button daba kar Easebuzz ke khaano ka naksha lo.

Pichhli probe ne galti se UPI khola tha: `label:has-text('Credit/Debit Card')`
ne galat cheez dabaayi. Naksha se asli button mila -- `#payment-method-button-
Card`. Ye probe usi ko dabati hai, phir Easebuzz ka gateway (jo ek NESTED
iframe -- shayad easebuzz.in -- me khulta hai) ke andar tak jaa kar har khaana
padhti hai. Card number/expiry/cvv apne apne iframe me ho sakte hain, isliye
har iframe -- chahe kitna bhi andar ho -- alag se dikhaya jaata hai.

Ye kuch BHARTI NAHI. Sirf dekh kar out/card_probe.txt me likh deti hai.
"""
import os
import sys
import json

from playwright.sync_api import sync_playwright

import place_order as po

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
SHOP = "https://estuaryworld.com"
os.makedirs(OUT, exist_ok=True)

PRODUCT = "black-white-ginger-ale"
PACK = "Pack of 04"
REPORT = open(os.path.join(OUT, "card_probe.txt"), "w", encoding="utf-8")


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    REPORT.write(s + "\n")
    REPORT.flush()


def fastrr(page):
    for fr in page.frames:
        if "fastrr-boost-ui.pickrr.com" in (fr.url or ""):
            try:
                if (fr.locator("body").inner_text() or "").strip():
                    return fr
            except Exception:
                pass
    return None


def dump_all(page, tag):
    """HAR frame (Easebuzz ke nested tak) ke dikhne wale khaane aur button."""
    log("\n" + "=" * 72)
    log("[%s]" % tag)
    log("=" * 72)
    for i, fr in enumerate(page.frames):
        u = (fr.url or "")[:96]
        try:
            fields = fr.locator(
                "input:visible, select:visible, textarea:visible"
            ).evaluate_all(
                "els => els.map(e => e.tagName"
                " + ' id=' + (e.id||'-')"
                " + ' name=' + (e.name||'-')"
                " + ' type=' + (e.type||'-')"
                " + ' ph=' + (e.placeholder||'-')"
                " + ' aria=' + (e.getAttribute('aria-label')||'-')"
                " + ' maxlen=' + (e.maxLength>0 ? e.maxLength : '-'))")
        except Exception:
            fields = []
        # Card ke khaane aksar iframe me hote hain -- easebuzz/pickrr wale
        # frame ki url bhi dikha do bhale usme abhi field na ho.
        show = fields or any(k in u.lower() for k in
                             ("easebuzz", "eazypay", "axis", "icici", "3ds",
                              "challenge", "pickrr", "payment"))
        if not show:
            continue
        log("\n  frame %d : %s" % (i, u))
        for f in fields[:30]:
            log("      KHAANA : %s" % f[:160])
        try:
            btns = fr.locator("button:visible, [role=button]:visible"
                              ).evaluate_all(
                "els => els.map(e => (e.textContent||'').trim().slice(0,36)"
                "                    + ' /id=' + (e.id||'-'))")
            for bt in btns[:12]:
                if bt.strip(" /id=-"):
                    log("      BUTTON : %s" % bt[:90])
        except Exception:
            pass


def main():
    path = po.newest_session()
    d = json.load(open(path, encoding="utf-8"))
    log("account : %s / %s" % (d.get("phone"), d.get("email")))

    with sync_playwright() as p:
        b = p.chromium.launch(headless=False, args=["--start-maximized"])
        ctx = b.new_context(storage_state=d["state"], locale="en-IN",
                            viewport={"width": 1500, "height": 950})
        page = ctx.new_page()
        page.goto("%s/products/%s" % (SHOP, PRODUCT),
                  wait_until="domcontentloaded", timeout=90000)
        page.wait_for_timeout(5000)
        po.pick(page, PACK)
        page.locator(po.find(page, po.ADD_TO_CART)).first.click()
        page.wait_for_timeout(6000)
        if not po.find(page, po.CHECKOUT):
            s2 = po.find(page, po.CART_OPEN)
            if s2:
                page.locator(s2).first.click()
                page.wait_for_timeout(5000)
        sel = po.find(page, po.CHECKOUT)
        newpage = None
        try:
            with ctx.expect_page(timeout=15000) as np:
                page.locator(sel).first.click()
            newpage = np.value
        except Exception:
            pass
        pay = newpage or page
        pay.wait_for_timeout(12000)
        log("pata  : %s" % po.ship_address(pay, d))
        pay.wait_for_timeout(4000)
        log("email : %s" % po.confirm_email(pay, d))
        pay.wait_for_timeout(4000)

        fr = fastrr(pay)
        if not fr:
            log("FAIL: fastrr frame nahi mila")
            b.close()
            return 1

        # ASLI BUTTON -- id se. `label:has-text` wali galti dobara nahi.
        btn = fr.locator("#payment-method-button-Card")
        log("\ncard button mila: %d" % btn.count())
        if btn.count():
            box = btn.first.bounding_box()
            if box:
                pay.mouse.move(box["x"] + box["width"] / 2,
                               box["y"] + box["height"] / 2, steps=10)
                pay.wait_for_timeout(300)
                pay.mouse.down()
                pay.wait_for_timeout(90)
                pay.mouse.up()
            else:
                btn.first.click()
        else:
            log("id se nahi mila -- text se koshish")
            fr.locator("button:has-text('Credit/Debit Card')").first.click()

        # Easebuzz dheere khulta hai -- har 12s par naapo, 6 baar.
        for n in range(1, 7):
            pay.wait_for_timeout(12000)
            dump_all(pay, "CARD BUTTON KE BAAD +%ds" % (n * 12))
            try:
                pay.screenshot(path=os.path.join(OUT, "card_probe_%d.png" % n))
            except Exception as e:
                log("   (tasveer nahi: %s)" % str(e)[:50])

        log("\nnaksha: out/card_probe.txt | tasveer: out/card_probe_1..6.png")
        pay.wait_for_timeout(15000)
        b.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
