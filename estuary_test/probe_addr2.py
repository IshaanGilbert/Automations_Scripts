import glob, json, os, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.sync_api import sync_playwright
f = sorted(glob.glob("sessions/*.json"), key=os.path.getmtime)[-1]
d = json.load(open(f, encoding="utf-8"))
SHOP = "https://estuaryworld.com"
with sync_playwright() as p:
    b = p.chromium.launch(headless=False, args=["--start-maximized"])
    ctx = b.new_context(storage_state=d["state"], locale="en-IN",
                        viewport={"width":1500,"height":950})
    pg = ctx.new_page()
    pg.goto(SHOP+"/products/black-white-ginger-ale", wait_until="domcontentloaded", timeout=120000)
    pg.wait_for_timeout(5000)
    pg.evaluate("""(v)=>{const r=[...document.querySelectorAll('input[type=radio]')]
        .find(x=>(x.value||'').trim()===v); if(r&&!r.checked) r.click();}""", "Pack of 04")
    pg.wait_for_timeout(2000)
    pg.locator("button.add-to-cart").first.click(); pg.wait_for_timeout(6000)
    pg.locator("#yt-checkout-button").first.click(); pg.wait_for_timeout(14000)
    fr = None
    for _ in range(20):
        for x in pg.frames:
            if "fastrr-boost-ui" in (x.url or "") and x.locator("#pincode").count():
                fr = x; break
        if fr: break
        pg.wait_for_timeout(1500)
    fr.locator("#pincode").fill("000000"); pg.wait_for_timeout(4000)
    fr.locator("#name").fill("Ishan"); fr.locator("#lastName").fill("Gupta")
    fr.locator("#line1").fill("168/87 Shastri Nagar")
    fr.locator("#line2").fill("Near Kidwai Nagar Market")
    fr.locator("#email").fill(d.get("email") or "test@example.com")
    pg.wait_for_timeout(1500)
    print("values:", fr.evaluate("""()=>({pin:document.querySelector('#pincode').value,
        city:document.querySelector('#city').value, state:document.querySelector('#state').value,
        email:document.querySelector('#email').value})"""))
    # ASLI MOUSE -- Nykaa wale Proceed par yahi zaroori pada tha
    box = fr.locator("#addAddressBtn").bounding_box()
    print("button box:", box)
    if box:
        pg.mouse.move(box["x"]+box["width"]/2, box["y"]+box["height"]/2, steps=12)
        pg.wait_for_timeout(400); pg.mouse.down(); pg.wait_for_timeout(90); pg.mouse.up()
    for i in range(5):
        pg.wait_for_timeout(4000)
        try:
            t = fr.locator("body").inner_text().replace("\n"," | ")
        except Exception as e:
            t = "frame gaya: %s" % str(e)[:40]
        gone = "Add shipping address" not in t
        print("\n[%ds] address ka form gaya: %s" % ((i+1)*4, gone))
        print("   ", t[:300])
        if gone: break
    pg.screenshot(path="out/probe_addr2.png")
    b.close()
