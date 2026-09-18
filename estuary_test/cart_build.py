#!/usr/bin/env python3
"""cart_build.py -- diye hue daam ke daayre me, alag alag items se cart bharo.

KYUN
----
Automation ka niyam ye hai: "500 se 1000 ke beech 100 order lagane hain, aur ek
account par zyada se zyada 2000 tak ka maal." To har order ke liye ek cart
chahiye jiska kul daam us daayre me aaye -- aur cheezein alag alag hon, taaki
har order ek jaisa na dikhe.

KAISE
-----
Daam scraped file (products_check.json) se aata hai, site se nahi -- 159
in-stock variant wahin darj hain. Un me se chun kar cart Shopify ki apni
/cart/add.js se bhara jaata hai (button dabane se nahi): wahi call browser khud
karta hai, isliye ye tez bhi hai aur bharosemand bhi. Aakhir me /cart.js se
milaan hota hai -- jo cart me sach me gaya wahi ginti hai.

CHALANA (sirf jaanch -- order nahi lagta)
    python cart_build.py --min 500 --max 2000
    python cart_build.py --min 1900 --max 2000 --items 4
    python cart_build.py --min 500 --max 1000 --dry     # bina browser, sirf chunav
"""
import os
import sys
import json
import random
import argparse

HERE = os.path.dirname(os.path.abspath(__file__))
CATALOG = os.path.join(HERE, "products_check.json")

# Ek account par itne se zyada ka maal nahi -- upar wala niyam.
ACCOUNT_MAX = 2000.0


def load_variants(path=CATALOG, only_in_stock=True):
    """Scraped file se chunne layak variants -- ek saaf list."""
    d = json.load(open(path, encoding="utf-8"))
    out = []
    for p in d.get("products", []):
        for q in p.get("quantities", []):
            if only_in_stock and not q.get("in_stock"):
                continue
            try:
                price = float(q.get("price"))
            except (TypeError, ValueError):
                continue
            if price <= 0 or not q.get("variant_id"):
                continue
            out.append({
                "product": p.get("product"),
                "handle": p.get("handle"),
                "variant_id": int(q["variant_id"]),
                "variant_name": q.get("variant_name") or "",
                "price": price,
            })
    return out


def pick_cart(variants, lo, hi, max_items=6, one_per_product=True, tries=3000,
              seed=None):
    """Aise items chuno ki kul daam [lo, hi] ke beech aaye.

    Seedha-sada tareeka: har koshish me items ko phenta jaata hai aur ek ek
    karke jodte hain jab tak `hi` paar na ho. `lo` par pahunch gaye to kaam
    khatam. Sabse achhi koshish yaad rakhi jaati hai, taaki `lo` tak na
    pahunchne par bhi jo sabse paas thi wahi mile.

    one_per_product: ek product sirf ek baar -- warna cart me ek hi cheez ke
    kai pack chale jaate hain aur "alag alag items" ka matlab hi khatam.
    """
    if hi > ACCOUNT_MAX:
        hi = ACCOUNT_MAX
    rnd = random.Random(seed)
    usable = [v for v in variants if v["price"] <= hi]
    if not usable:
        return [], 0.0

    best, best_total = [], 0.0
    for _ in range(tries):
        pool = usable[:]
        rnd.shuffle(pool)
        chosen, seen, total = [], set(), 0.0
        for v in pool:
            if len(chosen) >= max_items:
                break
            if one_per_product and v["handle"] in seen:
                continue
            if total + v["price"] > hi:
                continue
            chosen.append(v)
            seen.add(v["handle"])
            total += v["price"]
            if total >= lo:
                break
        if lo <= total <= hi:
            # jitna hi ke kareeb, utna achha
            if total > best_total or not best:
                best, best_total = chosen, total
            if hi - total < 1:        # isse behtar milega nahi
                break
        elif total > best_total:
            best, best_total = chosen, total
    return best, round(best_total, 2)


# ---------------------------------------------------------------- browser
def clear_cart(page):
    """Purana cart hata do -- warna pichhli koshish ka maal jud jaata hai."""
    return page.evaluate_async(
        "const cb = arguments[arguments.length - 1];"
        "fetch('/cart/clear.js', {method: 'POST'})"
        ".then(r => r.json()).then(j => cb(j)).catch(e => cb(null));")


def cart_now(page):
    return page.evaluate_async(
        "const cb = arguments[arguments.length - 1];"
        "fetch('/cart.js').then(r => r.json()).then(j => cb(j))"
        ".catch(e => cb(null));") or {}


def add_items(page, items, log=print):
    """Chune hue items cart me daalo -- ek ek karke.

    Ek saath bhejne me ek bhi variant out-of-stock ho to POORA call fail hota
    hai. Ek ek bhejne se sirf wahi item chhoot ta hai, baaki cart me chala
    jaata hai -- aur hume pata chal jaata hai kaun chhoota.
    """
    gaye, chhoote = [], []
    for it in items:
        res = page.evaluate_async(
            "const cb = arguments[arguments.length - 1];"
            "fetch('/cart/add.js', {method: 'POST',"
            " headers: {'Content-Type': 'application/json'},"
            " body: JSON.stringify({items: [{id: arguments[0], quantity: 1}]})})"
            ".then(r => r.json().then(j => cb({ok: r.ok, body: j})))"
            ".catch(e => cb({ok: false, body: String(e)}));",
            it["variant_id"])
        if res and res.get("ok"):
            gaye.append(it)
            log("      + %-34s %-12s Rs %8.2f" % (
                it["product"][:34], it["variant_name"][:12], it["price"]))
        else:
            chhoote.append(it)
            why = ""
            if isinstance(res, dict):
                b = res.get("body")
                why = (b.get("description") or b.get("message") or "")[:60] \
                    if isinstance(b, dict) else str(b)[:60]
            log("      x %-34s %-12s -- %s" % (
                it["product"][:34], it["variant_name"][:12], why or "nahi gaya"))
    return gaye, chhoote


def build_on_page(page, lo, hi, max_items=6, log=print, seed=None,
                  catalog=CATALOG):
    """Poora kaam: cart khaali karo -> chuno -> daalo -> milaan karo."""
    variants = load_variants(catalog)
    log("   catalog: %d in-stock variant" % len(variants))

    clear_cart(page)
    items, chuna_total = pick_cart(variants, lo, hi, max_items=max_items, seed=seed)
    if not items:
        return {"ok": False, "why": "is daayre ke liye koi chunav nahi mila"}
    log("   chunav: %d item, kul Rs %.2f (daayra %s-%s)"
        % (len(items), chuna_total, lo, hi))

    gaye, chhoote = add_items(page, items, log=log)

    # kam pad gaya (kuch item chhoot gaye) to bacha hua daam bharne ki koshish
    cart = cart_now(page)
    total = (cart.get("total_price", 0) or 0) / 100.0
    if total < lo and chhoote:
        bacha = hi - total
        aur = [v for v in variants
               if v["price"] <= bacha
               and v["handle"] not in {g["handle"] for g in gaye}]
        aur.sort(key=lambda v: -v["price"])
        for v in aur:
            if total >= lo:
                break
            g2, _ = add_items(page, [v], log=log)
            if g2:
                gaye.extend(g2)
                cart = cart_now(page)
                total = (cart.get("total_price", 0) or 0) / 100.0

    cart = cart_now(page)
    total = (cart.get("total_price", 0) or 0) / 100.0
    return {
        "ok": lo <= total <= hi,
        "total": total,
        "items": cart.get("item_count", 0),
        "chhoote": len(chhoote),
        "cart": cart,
        "chuna_total": chuna_total,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min", type=float, default=500, help="cart ka kam se kam daam")
    ap.add_argument("--max", type=float, default=2000, help="cart ka zyada se zyada daam")
    ap.add_argument("--items", type=int, default=6, help="cart me zyada se zyada itne item")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--dry", action="store_true",
                    help="browser mat kholo -- sirf chunav dikhao")
    ap.add_argument("--session", default="")
    ap.add_argument("--no-proxy", action="store_true")
    a = ap.parse_args()

    if a.max > ACCOUNT_MAX:
        print("CHETAVNI: ek account par %s se zyada nahi -- max ko %s kar diya"
              % (ACCOUNT_MAX, ACCOUNT_MAX))
        a.max = ACCOUNT_MAX

    variants = load_variants()
    print("catalog: %d in-stock variant | daam %.0f se %.0f"
          % (len(variants), min(v["price"] for v in variants),
             max(v["price"] for v in variants)))

    if a.dry:
        items, total = pick_cart(variants, a.min, a.max, max_items=a.items,
                                 seed=a.seed)
        print("\nchunav (%d item, kul Rs %.2f):" % (len(items), total))
        for it in items:
            print("   %-38s %-14s Rs %8.2f" % (it["product"][:38],
                                               it["variant_name"][:14], it["price"]))
        print("\ndaayre me hai?", a.min <= total <= a.max)
        return 0

    # ---- asli browser me jaanch ----
    import place_order as po
    path = a.session or po.newest_session()
    if not os.path.isabs(path):
        p2 = os.path.join(po.SESSIONS, path)
        path = p2 if os.path.exists(p2) else path
    d = json.load(open(path, encoding="utf-8"))
    print("account: %s / %s" % (d.get("phone"), d.get("email")))

    port, stop = (None, None)
    if not a.no_proxy:
        port, stop = po.start_geonode_bridge(po.geonode_username("in"))
        print("proxy  : 127.0.0.1:%d" % port)

    drv = po.launch_waterfox(proxy_port=port)
    try:
        po.load_session(drv, d)
        page = po.Scope(drv, drv.current_window_handle)
        page.goto(po.SHOP, timeout=120)
        page.wait_for_timeout(3000)

        res = build_on_page(page, a.min, a.max, max_items=a.items, seed=a.seed)
        print("\n================ NATIJA ================")
        if not res.get("ok") and "why" in res:
            print("   ", res["why"])
        else:
            print("   cart me item : %d" % res["items"])
            print("   cart ka daam : Rs %.2f" % res["total"])
            print("   daayra       : %.0f - %.0f" % (a.min, a.max))
            print("   daayre me?   : %s" % ("HAAN" if res["ok"] else "NAHI"))
            if res["chhoote"]:
                print("   chhoote item : %d (stock nahi tha)" % res["chhoote"])
            print("\n   cart me kya gaya:")
            for it in (res["cart"].get("items") or []):
                print("      %-38s %-14s Rs %8.2f" % (
                    (it.get("product_title") or "")[:38],
                    (it.get("variant_title") or "")[:14],
                    (it.get("line_price", 0) or 0) / 100.0))
    finally:
        try: drv.quit()
        except Exception: pass
        if stop is not None:
            stop.set()
    return 0


if __name__ == "__main__":
    sys.exit(main())
