#!/usr/bin/env python3
"""scrape.py -- estuaryworld.com ka poora saamaan: naam, daam, aur har quantity.

DO RASTE, AUR KYUN
------------------
1. **Shopify ka apna feed** (`/products.json`). Site Shopify par hai, aur wo
   khud har product ka poora dhancha deta hai -- options ("SELECT UNIT SIZE",
   "SELECT PACK SIZE"), har variant ka daam, aur stock hai ya nahi. Panne se
   HTML nochne se ye sab zyada saaf aur zyada pakka milta hai, aur ek hi call
   me poora catalogue.

2. **Ek product ka asli panna, LOGIN ke saath** -- sirf milaan ke liye. Feed
   aur panna alag bol dein to us farq ka pata hona chahiye (login par daam
   badalna, ya koi variant chhupa hona). Bina milaye feed par bharosa karna
   wahi galti hai jo "screen kuch kehti hai, asliyat kuch aur" wali hai.

CHALANA
-------
    python scrape.py                  # sab kuch, milaan ke saath
    python scrape.py --no-check       # sirf feed (browser nahi khulega)

BANTA KYA HAI
-------------
    products.csv    -- ek line = ek quantity (variant): naam, unit, pack, daam, stock
    products.json   -- poora kacha data, aage kisi bhi kaam ke liye
"""
import os
import re
import csv
import sys
import json
import glob
import time
import argparse
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
SESSIONS = os.path.join(HERE, "sessions")
OUT = os.path.join(HERE, "out")
SHOP = "https://estuaryworld.com"
os.makedirs(OUT, exist_ok=True)


def log(*a):
    print(*a, flush=True)


def get_json(url, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.loads(r.read().decode("utf-8", "ignore"))
        except Exception as e:
            if i == tries - 1:
                log("   (nahi mila: %s)" % str(e)[:90])
                return None
            time.sleep(3)


def all_products():
    """Poora catalogue -- ek panne me 250, jab tak khaali na aa jaye.

    Ginti par bharosa nahi kiya jaata: agla panna khaali aane par hi ruka jaata
    hai. Shopify 250 se zyada ek baar me deta hi nahi, aur "73 mile to bas 73
    honge" maan lena wahi jagah hai jahan aadha catalogue chhoot jaata hai.
    """
    out, page = [], 1
    while True:
        d = get_json("%s/products.json?limit=250&page=%d" % (SHOP, page))
        got = (d or {}).get("products") or []
        if not got:
            break
        out.extend(got)
        log("   panna %d -> %d product (ab tak %d)" % (page, len(got), len(out)))
        page += 1
        if page > 40:
            break
    return out


def _kind(name):
    """Option ka naam har product par ek jaisa nahi hai.

    Catalogue me chhe alag naam mile: "SELECT UNIT SIZE", "SELECT PACK SIZE",
    "Pack Size", "Size", "Glass Sets", "BOTTLE TYPE", aur bina option wale par
    "Title". Sirf do naam pehchanne se aadha data `other` me chala jaata hai --
    isliye pehchan naam ke SHABDON se hoti hai, poore naam se nahi.
    """
    n = (name or "").strip().lower()
    if "pack" in n or "set" in n:
        return "pack"
    if "unit" in n or n in ("size", "select size"):
        return "unit"
    return "other"


def rows_of(p):
    """Ek product ke saare variant -- har ek apni line."""
    names = [o.get("name", "") for o in (p.get("options") or [])]
    rows = []
    for v in p.get("variants") or []:
        unit = pack = ""
        other = []
        for i, nm in enumerate(names, start=1):
            val = v.get("option%d" % i)
            if not val or val == "Default Title":
                continue
            k = _kind(nm)
            if k == "unit" and not unit:
                unit = val
            elif k == "pack" and not pack:
                pack = val
            else:
                other.append("%s=%s" % (nm, val))
        rows.append({
            "product": p.get("title"),
            "handle": p.get("handle"),
            "url": "%s/products/%s" % (SHOP, p.get("handle")),
            "vendor": p.get("vendor"),
            "type": p.get("product_type"),
            "variant": v.get("title"),
            "unit_size": unit,
            "pack_size": pack,
            "other_option": " | ".join(other),
            "price": v.get("price"),
            "mrp": v.get("compare_at_price") or "",
            "in_stock": "yes" if v.get("available") else "no",
            "sku": v.get("sku") or "",
            "variant_id": v.get("id"),
            "product_id": p.get("id"),
        })
    return rows


def check_dump(rows):
    """Ek saaf JSON jise AADMI khud kholkar milaa sake.

    `products.json` Shopify ka kacha data hai -- usme har product ke saath
    body_html, images, created_at sab hota hai, aur usme se aankh se kuch
    milaana mushkil hai. Ye file uska ulta hai: har product ki ek entry, sabse
    upar uska LINK, aur neeche uski saari quantity -- pack, daam, MRP, stock.
    Link kholo, panne se milao, bas.
    """
    by = {}
    for r in rows:
        p = by.setdefault(r["handle"], {
            "product": r["product"],
            "link": r["url"],
            "handle": r["handle"],
            "vendor": r["vendor"],
            "type": r["type"],
            "unit_sizes": [],
            "pack_sizes": [],
            "quantity_count": 0,
            "in_stock_count": 0,
            "price_from": None,
            "price_to": None,
            "quantities": [],
        })
        if r["unit_size"] and r["unit_size"] not in p["unit_sizes"]:
            p["unit_sizes"].append(r["unit_size"])
        if r["pack_size"] and r["pack_size"] not in p["pack_sizes"]:
            p["pack_sizes"].append(r["pack_size"])
        price = float(r["price"]) if r["price"] else None
        p["quantity_count"] += 1
        p["in_stock_count"] += 1 if r["in_stock"] == "yes" else 0
        if price is not None:
            p["price_from"] = price if p["price_from"] is None else min(p["price_from"], price)
            p["price_to"] = price if p["price_to"] is None else max(p["price_to"], price)
        p["quantities"].append({
            "unit_size": r["unit_size"] or None,
            "pack_size": r["pack_size"] or None,
            "other_option": r["other_option"] or None,
            "variant_name": r["variant"],
            "price": r["price"],
            "mrp": r["mrp"] or None,
            "in_stock": r["in_stock"] == "yes",
            "sku": r["sku"] or None,
            "variant_id": r["variant_id"],
        })

    out = {
        "shop": SHOP,
        "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_products": len(by),
        "total_quantities": sum(p["quantity_count"] for p in by.values()),
        "in_stock_quantities": sum(p["in_stock_count"] for p in by.values()),
        "products": sorted(by.values(), key=lambda p: p["product"].lower()),
    }
    path = os.path.join(HERE, "products_check.json")
    json.dump(out, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return path


def check_on_page(handle, want, headless=True):
    """Ek product ka asli panna, LOGIN ke saath -- feed se milta hai ya nahi.

    Panne se milaan HANDLE se hota hai, naam se nahi. Pehli baar naam se chuna
    tha aur wo galat nikla: "Godawan Estuary Premium Water" naam ke DO product
    hain -- ek me sirf 750ml, doosre me unit+pack. Naam se milaane par panna
    kisi aur product ka khula aur "mismatch" ka jhootha shak paida hua.
    """
    fs = sorted(glob.glob(os.path.join(SESSIONS, "*.json")), key=os.path.getmtime)
    if not fs:
        log("   (koi session nahi mili -- milaan chhod rahe hain)")
        return
    from playwright.sync_api import sync_playwright
    d = json.load(open(fs[-1], encoding="utf-8"))
    log("   session: %s (%s)" % (os.path.basename(fs[-1]), d.get("email")))
    log("   panna  : /products/%s" % handle)

    with sync_playwright() as p:
        b = p.chromium.launch(headless=headless)
        ctx = b.new_context(storage_state=d["state"], locale="en-IN",
                            viewport={"width": 1400, "height": 950})
        page = ctx.new_page()
        page.goto("%s/products/%s" % (SHOP, handle),
                  wait_until="domcontentloaded", timeout=90000)
        page.wait_for_timeout(5000)
        # Shopify ke theme me option ke button scroll par bante hain -- bina
        # jagaye wahan kuch hota hi nahi.
        for _ in range(4):
            page.mouse.wheel(0, 1200)
            page.wait_for_timeout(900)
        page.wait_for_timeout(2500)

        try:
            txt = page.inner_text("body") or ""
        except Exception:
            txt = ""
        low = txt.lower()
        log("   login dikh raha hai: %s"
            % any(w in low for w in ("logout", "log out", "my account", "order history")))

        for label in ("select unit size", "select pack size"):
            log("   panne par '%s': %s" % (label, label in low))
        miss = [v for v in want["units"] + want["packs"]
                if v and v.lower() not in low]
        log("   feed ke unit  : %s" % ", ".join(want["units"] or ["-"]))
        log("   feed ke pack  : %s" % ", ".join(want["packs"] or ["-"]))
        log("   panne par nahi mile: %s" % (", ".join(miss) if miss else "koi nahi"))
        rupees = sorted(set(re.findall(r"₹\s?([\d,]+)", txt)),
                        key=lambda s: int(s.replace(",", "")))
        log("   panne par daam: %s" % (rupees[:12] or "koi nahi"))
        log("   feed ka daam  : %s" % want["prices"][:12])
        page.screenshot(path=os.path.join(OUT, "product_check.png"), full_page=True)
        log("   tasveer: out/product_check.png")
        b.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-check", action="store_true",
                    help="sirf feed, browser mat kholo")
    ap.add_argument("--handle", default="",
                    help="kis product ka panna milana hai (url ka aakhri hissa)")
    ap.add_argument("--show", action="store_true", help="browser dikhao")
    a = ap.parse_args()

    log("1) poora catalogue utha rahe hain")
    prods = all_products()
    if not prods:
        log("   kuch nahi mila")
        return 1

    rows = []
    for p in prods:
        rows.extend(rows_of(p))

    with open(os.path.join(HERE, "products.csv"), "w", newline="",
              encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    json.dump(prods, open(os.path.join(HERE, "products.json"), "w",
                          encoding="utf-8"), ensure_ascii=False, indent=1)

    units = sorted({r["unit_size"] for r in rows if r["unit_size"]})
    packs = sorted({r["pack_size"] for r in rows if r["pack_size"]},
                   key=lambda s: (len(s), s))
    live = [r for r in rows if r["in_stock"] == "yes"]
    prices = sorted({float(r["price"]) for r in rows if r["price"]})

    log("\n================ jo mila ================")
    log("   product          : %d" % len(prods))
    log("   quantity (variant): %d" % len(rows))
    log("   stock me         : %d" % len(live))
    log("   stock khatam     : %d" % (len(rows) - len(live)))
    log("   daam             : Rs %g se Rs %g" % (min(prices), max(prices)))
    log("   unit size        : %s" % ", ".join(units))
    log("   pack size        : %s" % ", ".join(packs))

    # Ginti HANDLE se, naam se nahi -- ek hi naam ke do alag product hain
    # (do "Godawan Estuary Premium Water", do "The Estuary Personal Bar").
    per = {}
    for r in rows:
        per[r["handle"]] = per.get(r["handle"], 0) + 1
    name_of = {r["handle"]: r["product"] for r in rows}

    log("\n   sabse zyada quantity wale product:")
    for hnd, n in sorted(per.items(), key=lambda x: -x[1])[:8]:
        log("      %-52s %2d quantity" % (name_of[hnd][:52], n))

    top = a.handle or max(per, key=per.get)
    sample = [x for x in rows if x["handle"] == top]
    log("\n   namoona -- %s ki saari quantity:" % name_of.get(top, top))
    for r in sample[:14]:
        log("      %-10s %-14s Rs %-9s %s"
            % (r["unit_size"] or "-", r["pack_size"] or "-", r["price"],
               "stock me" if r["in_stock"] == "yes" else "khatam"))

    cpath = check_dump(rows)
    log("\n   files:")
    log("      products_check.json  <- HAR PRODUCT KA LINK + uski saari quantity")
    log("      products.csv         <- Excel me kholne ke liye (ek line = ek quantity)")
    log("      products.json        <- Shopify ka kacha data")

    if not a.no_check:
        log("\n2) ek product ka asli panna (login ke saath) -- milaan")
        check_on_page(top, {
            "units": sorted({x["unit_size"] for x in sample if x["unit_size"]}),
            "packs": sorted({x["pack_size"] for x in sample if x["pack_size"]}),
            "prices": sorted({x["price"] for x in sample}),
        }, headless=not a.show)
    return 0


if __name__ == "__main__":
    sys.exit(main())
