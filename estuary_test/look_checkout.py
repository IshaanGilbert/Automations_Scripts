"""look_checkout.py -- checkout ke andar wala address form kaisa hai.

Account par pata jodne se kaam poora nahi hota: Checkout dabane par Shiprocket
apna alag "Add shipping address" ka form dikhata hai (pincode, naam, flat,
area, city, state, email). Us form ke khaane pehle dekh lene chahiye, warna
script wahin andhere me haath maarti hai.
"""
import os
import sys
import glob
import json

from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
SESSIONS = os.path.join(HERE, "sessions")
OUT = os.path.join(HERE, "out")
SHOP = "https://estuaryworld.com"
os.makedirs(OUT, exist_ok=True)

PRODUCT = "black-white-ginger-ale"
PACK = "Pack of 04"


def dump(scope, tag):
    try:
        rows = scope.locator("input, select, textarea, button").evaluate_all(
            "els => els.map(e => e.tagName + ' | id=' + (e.id||'-')"
            " + ' | name=' + (e.name||'-') + ' | ph=' + (e.placeholder||'-')"
            " + ' | type=' + (e.type||'-') + ' | txt='"
            " + (e.textContent||'').trim().slice(0,28))")
    except Exception as e:
        print("   (%s: %s)" % (tag, str(e)[:60]))
        return
    print("\n=== %s ===" % tag)
    for r in rows[:45]:
        if "hidden" not in r:
            print("   ", r[:150])


def main():
    f = sorted(glob.glob(os.path.join(SESSIONS, "*.json")), key=os.path.getmtime)[-1]
    d = json.load(open(f, encoding="utf-8"))
    print("account:", d.get("phone"), d.get("email"))

    with sync_playwright() as p:
        b = p.chromium.launch(headless=False, args=["--start-maximized"])
        ctx = b.new_context(storage_state=d["state"], locale="en-IN",
                            viewport={"width": 1500, "height": 950})
        page = ctx.new_page()
        page.goto("%s/products/%s" % (SHOP, PRODUCT),
                  wait_until="domcontentloaded", timeout=90000)
        page.wait_for_timeout(5000)
        page.evaluate("""(v) => { const r=[...document.querySelectorAll('input[type=radio]')]
              .find(x=>(x.value||'').trim()===v); if (r && !r.checked) r.click(); }""", PACK)
        page.wait_for_timeout(2500)
        page.locator("button.add-to-cart").first.click()
        page.wait_for_timeout(6000)
        page.locator("#yt-checkout-button").first.click()
        page.wait_for_timeout(15000)

        print("\nURL:", page.url)
        print("frames:")
        for fr in page.frames:
            print("   ", (fr.url or "")[:110])

        # Jis bhi jagah "shipping address" likha ho, wahi hamara form hai.
        for fr in page.frames:
            try:
                t = (fr.locator("body").inner_text() or "").lower()
            except Exception:
                continue
            if "shipping address" in t or "pincode" in t:
                dump(fr, "FRAME " + (fr.url or "")[:70])
        page.screenshot(path=os.path.join(OUT, "checkout_form.png"))
        print("\ntasveer: out/checkout_form.png")
        page.wait_for_timeout(3000)
        b.close()


if __name__ == "__main__":
    main()
