#!/usr/bin/env python3
"""chrome_proxy_test.py — Chrome bridge se kyun nahi guzarta, ye pakka karne ke liye.

Ab tak jo pakka hai:
    curl  + bridge -> sab site chalti hain (15 sequential, 8 parallel, sab pass)
    Chrome+ bridge -> koi site nahi chalti (nykaa.com bhi, google.com bhi)
    Chrome bina proxy -> sab chalta hai

Yaani masla site ka nahi, proxy ke zinda hone ka nahi — Chrome ke TLS ka hai. Ye script
ek hi bridge pe Chrome ko alag-alag TLS settings me chala kar batati hai kaun si setting
kaam karti hai. Jo pass hoti hai, wahi bot me daalni hai.

    sudo venv/bin/python3 chrome_proxy_test.py
"""
import asyncio

import nykaa_login as nk

try:
    from patchright.async_api import async_playwright
    ENGINE = "patchright"
except ImportError:
    from playwright.async_api import async_playwright
    ENGINE = "playwright"

URLS = ["https://example.com/", "https://www.google.com/", "https://www.nykaa.com/"]

BASE = ["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage",
        "--disable-gpu", "--window-size=1440,900"]

# Har row: (naam, extra args). Naam wahi hai jo nateeje me chhapega.
CONFIGS = [
    ("1. jaisa bot abhi chalata hai",
     ["--disable-features=site-per-process,PostQuantumKyber,UseMLKEM"]),
    ("2. TLS 1.2 tak seemit",
     ["--ssl-version-max=tls1.2"]),
    ("3. sirf post-quantum band (teeno naam)",
     ["--disable-features=PostQuantumKyber,UseMLKEM,X25519MLKEM768,X25519Kyber768"]),
    ("4. bilkul saada (koi extra flag nahi)",
     []),
]


async def try_config(p, label, extra, proxy_url):
    args = BASE + extra
    line = f"{label:<42}"
    try:
        browser = await p.chromium.launch(
            headless=True, args=args, proxy={"server": proxy_url})
    except Exception as e:
        print(f"{line} LAUNCH FAIL: {str(e).splitlines()[0][:80]}")
        return
    results = []
    try:
        ctx = await browser.new_context(ignore_https_errors=True)
        ctx.set_default_navigation_timeout(45000)
        page = await ctx.new_page()
        for url in URLS:
            try:
                r = await page.goto(url, wait_until="domcontentloaded")
                results.append(f"{url.split('//')[1][:18]}={r.status if r else '?'}")
            except Exception as e:
                msg = str(e).splitlines()[0]
                short = "SSL" if "SSL_PROTOCOL" in msg else (
                        "TIMEOUT" if "TIMED_OUT" in msg else msg[-28:])
                results.append(f"{url.split('//')[1][:18]}=FAIL({short})")
    finally:
        try:
            await browser.close()
        except Exception:
            pass
    print(f"{line} {'  '.join(results)}")


async def main():
    user = nk.GEONODE_USER_BASE.format(nk.GEONODE_COUNTRY)
    server, port = await nk.start_proxy_bridge(user)
    proxy_url = f"http://127.0.0.1:{port}"
    print(f"engine {ENGINE} | bridge {proxy_url}")
    print(f"geonode {nk.GEONODE_HOST}:{nk.GEONODE_PORT} country={nk.GEONODE_COUNTRY}\n")
    try:
        async with async_playwright() as p:
            print("--- BRIDGE (proxy) ke through ---")
            for label, extra in CONFIGS:
                await try_config(p, label, extra, proxy_url)
    finally:
        await nk.stop_proxy_bridge(server)

    print("\nPadhne ka tareeka:")
    print("  koi row sab site pe status deti hai  -> wahi flags bot me daalne hain")
    print("  har row me FAIL(SSL)                 -> masla flags ka nahi, bridge/Geonode ka")


if __name__ == "__main__":
    asyncio.run(main())
