"""
=====================================================================
 TRAFFIC BOT  (headless, Chromium, concurrent) — server/CLI version
=====================================================================
 - No GUI. Runs on a headless Ubuntu server.
 - Playwright + bundled Chromium (headless).
 - Geonode residential proxy with country targeting. Chromium can't auth
   SOCKS5, so a tiny in-process HTTP->SOCKS5 bridge handles it (no extra pkg).
 - Runs N visits, up to --concurrency at the SAME time (multiple sessions).
 - Each visit: open URL via a fresh country IP -> random scroll + random
   click -> stay a random duration -> close.
 - Logs to console + visit_log.json.

 Install (once):
     pip3 install playwright
     python3 -m playwright install chromium
     sudo python3 -m playwright install-deps chromium

 Run:
     # Sab kuch upar wale SETTINGS block me set karo, phir bas:
     python3 traffic_bot.py
     # (chaho to override:  python3 traffic_bot.py --visits 200 --concurrency 8)
=====================================================================
"""

import asyncio
import json
import os
import sys
import socket
import random
import argparse
import contextvars
from datetime import datetime
from urllib.parse import urlparse

# Prefer patchright (stealth/undetected Playwright) if present; else plain playwright.
try:
    from patchright.async_api import async_playwright
    _ENGINE = "patchright"
except ImportError:
    from playwright.async_api import async_playwright
    _ENGINE = "playwright"

# ================= GEONODE CONFIG =================
GEONODE_USER_BASE = "geonode_xvmYN44Bvz-type-residential-country-{}"
GEONODE_PASS      = "CHANGE_ME_SECRET"
GEONODE_HOST      = "sg.proxy.geonode.io"
GEONODE_PORT      = "11000"

# =====================================================================
#  SETTINGS  —  yahan values edit karo, phir bas chalao:  python traffic_bot.py
#  (command me kuch dene ki zaroorat nahi; chaho to CLI se override bhi kar sakte ho)
# =====================================================================
URL          = "https://partners.trackopia.com/click?aid=4&oid=311"   # target URL
COUNTRIES    = "GB,DE,FR,IT,ES,NL,SE,CA,IN,BR"   # worldwide geos (comma se)
TOTAL_VISITS = 100        # total kitni visits karni hain
CONCURRENCY  = 15         # ek saath kitne sessions chalein (is server pe safe max ~15)
MIN_STAY     = 20         # har visit kam-se-kam itne second (hold)
MAX_STAY     = 25         # har visit zyada-se-zyada itne second
HEADED       = True       # True = browser windows dikhein (server pe Xvfb :99 chahiye) | False = headless
# =====================================================================

MAX_CONCURRENCY = 20      # hard cap (is server pe 20 se upar mat jao — no swap = OOM risk)
LOG_FILE        = "visit_log.json"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
]

_visit_ctx = contextvars.ContextVar("visit_no", default=None)


def log(m):
    v = _visit_ctx.get()
    prefix = f"[V{v}] " if v is not None else ""
    print(prefix + str(m), flush=True)


# ---------------- Proxy bridge (in-process HTTP -> Geonode SOCKS5) ----------------
def _free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


async def _socks5_connect(dst_host, dst_port, user, pw):
    reader, writer = await asyncio.open_connection(GEONODE_HOST, int(GEONODE_PORT))
    writer.write(b"\x05\x01\x02"); await writer.drain()
    resp = await reader.readexactly(2)
    if resp[1] != 0x02:
        raise OSError("SOCKS5 upstream refused username/password auth")
    ub = user.encode(); pb = pw.encode()
    writer.write(b"\x01" + bytes([len(ub)]) + ub + bytes([len(pb)]) + pb); await writer.drain()
    a = await reader.readexactly(2)
    if a[1] != 0x00:
        raise OSError("SOCKS5 auth failed")
    db = dst_host.encode()
    writer.write(b"\x05\x01\x00\x03" + bytes([len(db)]) + db + int(dst_port).to_bytes(2, "big")); await writer.drain()
    r = await reader.readexactly(4)
    if r[1] != 0x00:
        raise OSError(f"SOCKS5 connect failed (code {r[1]})")
    atyp = r[3]
    if atyp == 0x01:
        await reader.readexactly(4)
    elif atyp == 0x03:
        ln = await reader.readexactly(1); await reader.readexactly(ln[0])
    elif atyp == 0x04:
        await reader.readexactly(16)
    await reader.readexactly(2)
    return reader, writer


async def _pipe(src_reader, dst_writer):
    try:
        while True:
            data = await src_reader.read(65536)
            if not data:
                break
            dst_writer.write(data); await dst_writer.drain()
    except Exception:
        pass
    finally:
        try:
            dst_writer.close()
        except Exception:
            pass


def _make_bridge_handler(username, tasks):
    async def handle(client_reader, client_writer):
        tasks.add(asyncio.current_task())
        up_writer = None
        try:
            header = b""
            while b"\r\n\r\n" not in header:
                chunk = await client_reader.read(65536)
                if not chunk:
                    return
                header += chunk
                if len(header) > 262144:
                    return
            head, _, leftover = header.partition(b"\r\n\r\n")
            request_line = head.split(b"\r\n", 1)[0].decode("latin1")
            method, target, _ver = request_line.split(" ", 2)
            if method.upper() == "CONNECT":
                host, _, port = target.rpartition(":")
                up_reader, up_writer = await _socks5_connect(host, int(port), username, GEONODE_PASS)
                client_writer.write(b"HTTP/1.1 200 Connection established\r\n\r\n"); await client_writer.drain()
                if leftover:
                    up_writer.write(leftover); await up_writer.drain()
            else:
                u = urlparse(target)
                host = u.hostname; port = u.port or 80
                up_reader, up_writer = await _socks5_connect(host, int(port), username, GEONODE_PASS)
                path = u.path or "/"
                if u.query:
                    path += "?" + u.query
                rebuilt = header.replace(target.encode(), path.encode(), 1)
                up_writer.write(rebuilt); await up_writer.drain()
            await asyncio.gather(_pipe(client_reader, up_writer), _pipe(up_reader, client_writer))
        except Exception:
            try:
                client_writer.close()
            except Exception:
                pass
            if up_writer is not None:
                try:
                    up_writer.close()
                except Exception:
                    pass
        finally:
            tasks.discard(asyncio.current_task())
    return handle


async def start_proxy_bridge(username):
    local_port = _free_port()
    tasks = set()
    server = await asyncio.start_server(_make_bridge_handler(username, tasks), "127.0.0.1", local_port)
    server._bridge_tasks = tasks
    return server, local_port


async def stop_proxy_bridge(server):
    if server is None:
        return
    try:
        server.close(); await server.wait_closed()
    except Exception:
        pass
    for t in list(getattr(server, "_bridge_tasks", ())):
        if not t.done():
            t.cancel()


def _quiet_exception_handler(loop, context):
    exc = context.get("exception")
    if isinstance(exc, (ConnectionResetError, ConnectionAbortedError, BrokenPipeError)):
        return
    if isinstance(exc, OSError) and getattr(exc, "winerror", None) in (10053, 10054, 10058):
        return
    if "_call_connection_lost" in str(context.get("message", "")):
        return
    loop.default_exception_handler(context)


def install_quiet_loop():
    try:
        asyncio.get_running_loop().set_exception_handler(_quiet_exception_handler)
    except Exception:
        pass


async def get_proxy_ip(context):
    ip = "unknown"
    tmp = None
    try:
        tmp = await context.new_page()
        await tmp.goto("https://api.ipify.org?format=json", timeout=40000, wait_until="domcontentloaded")
        body = await tmp.evaluate("() => document.body.innerText")
        ip = json.loads(body).get("ip", "unknown")
    except Exception:
        ip = "unknown"
    finally:
        if tmp is not None:
            try:
                await tmp.close()
            except Exception:
                pass
    return ip


# ---------------- engagement ----------------
async def random_click(page):
    try:
        handle = await page.evaluate_handle("""() => {
            const els=[...document.querySelectorAll("a[href], button, [role='button'], input[type='submit'], input[type='button']")].filter(e=>{
                const r=e.getBoundingClientRect();
                const st=getComputedStyle(e);
                if(r.width<20||r.height<12) return false;
                if(st.visibility==='hidden'||st.display==='none'||parseFloat(st.opacity||'1')<0.1) return false;
                const t=(e.textContent||'').toLowerCase();
                if(/logout|sign out|log out|unsubscribe|delete/.test(t)) return false;
                return true;
            });
            if(!els.length) return null;
            return els[Math.floor(Math.random()*els.length)];
        }""")
        el = handle.as_element()
        if not el:
            return False
        try:
            await el.scroll_into_view_if_needed(timeout=6000)
        except Exception:
            pass
        await page.wait_for_timeout(random.randint(400, 900))
        try:
            await el.click(timeout=6000)
        except Exception:
            await el.click(timeout=6000, force=True)
        return True
    except Exception:
        return False


async def navigate_click(page):
    """Click a random INTERNAL link to load another page on the same site.
    Extra pageviews = lower bounce rate (looks like a real browsing session).
    Returns True only if the URL actually changed (a real navigation)."""
    try:
        host = urlparse(page.url).netloc
        handle = await page.evaluate_handle("""(host) => {
            const links=[...document.querySelectorAll('a[href]')].filter(a=>{
                try{
                    const u=new URL(a.href, location.href);
                    if(u.host!==host) return false;                 // same site only
                    if(!/^https?:/.test(u.protocol)) return false;
                    if(u.href.split('#')[0]===location.href.split('#')[0]) return false;
                    const r=a.getBoundingClientRect();
                    if(r.width<10||r.height<8) return false;
                    const t=(a.textContent||'').toLowerCase();
                    if(/logout|sign ?out|unsubscribe|delete/.test(t)) return false;
                    return true;
                }catch(e){return false;}
            });
            if(!links.length) return null;
            return links[Math.floor(Math.random()*links.length)];
        }""", host)
        el = handle.as_element()
        if not el:
            return False
        try:
            await el.scroll_into_view_if_needed(timeout=6000)
        except Exception:
            pass
        await page.wait_for_timeout(random.randint(400, 900))
        url_before = page.url
        try:
            await el.click(timeout=6000)
        except Exception:
            try:
                await el.click(timeout=6000, force=True)
            except Exception:
                return False
        # wait for the new page to load
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=15000)
        except Exception:
            pass
        await page.wait_for_timeout(random.randint(800, 1500))
        return page.url.split("#")[0] != url_before.split("#")[0]
    except Exception:
        return False


# ---------------- one visit ----------------
async def run_one_visit(visit_no, url, country, min_stay, max_stay, headless=True):
    _visit_ctx.set(visit_no)
    username = GEONODE_USER_BASE.format(country.lower())
    log(f"=== Visit #{visit_no} | Country: {country} ===")

    server, port = await start_proxy_bridge(username)
    browser = None
    ip_used = "unknown"
    landed = ""
    clicked = False
    pageviews = 0
    clicks = 0
    status = "error"
    err = None
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=headless,
                proxy={"server": f"http://127.0.0.1:{port}"},
                args=["--no-sandbox", "--disable-dev-shm-usage",
                      "--disable-blink-features=AutomationControlled"],
            )
            ctx = await browser.new_context(
                user_agent=random.choice(USER_AGENTS),
                viewport={"width": random.choice([1366, 1440, 1536, 1920]),
                          "height": random.choice([768, 900, 1080])},
                ignore_https_errors=True,
            )
            await ctx.add_init_script(
                "Object.defineProperty(navigator,'webdriver',{get:()=>undefined});"
            )
            page = await ctx.new_page()

            ip_used = await get_proxy_ip(ctx)
            log(f"🌐 IP: {ip_used} | Country: {country}")

            try:
                await page.goto(url, timeout=75000, wait_until="domcontentloaded")
            except Exception:
                log("   page slow — continuing with what loaded")
                try:
                    await page.evaluate("window.stop()")
                except Exception:
                    pass
            # full-load wait so the tracking pixel fires reliably
            try:
                await page.wait_for_load_state("load", timeout=30000)
            except Exception:
                pass
            await page.wait_for_timeout(random.randint(2500, 4500))
            try:
                landed = page.url
            except Exception:
                landed = url
            log(f"📍 Landed: {landed[:90]}")
            pageviews = 1

            # initial human scroll on the landing page
            for _ in range(random.randint(2, 4)):
                try:
                    await page.mouse.wheel(0, random.randint(300, 800))
                except Exception:
                    pass
                await page.wait_for_timeout(random.randint(700, 1500))

            # engage for the hold window: scroll + navigate to other pages +
            # random clicks. Navigation gives extra pageviews => low bounce rate.
            stay = random.uniform(min_stay, max_stay)
            log(f"⏳ Engaging ~{stay:.0f}s (scroll + navigation + clicks) ...")
            start = asyncio.get_event_loop().time()
            navigated_once = False
            while asyncio.get_event_loop().time() - start < stay:
                if not ctx.pages:
                    break
                r = random.random()
                if r < 0.45:
                    try:
                        await page.mouse.wheel(0, random.randint(250, 800))
                    except Exception:
                        pass
                elif r < 0.72:
                    if await navigate_click(page):
                        pageviews += 1
                        clicks += 1
                        navigated_once = True
                        log(f"   ➤ navigated to page {pageviews}: {page.url[:70]}")
                        for _ in range(random.randint(1, 3)):
                            try:
                                await page.mouse.wheel(0, random.randint(300, 800))
                            except Exception:
                                pass
                            await page.wait_for_timeout(random.randint(700, 1400))
                else:
                    if await random_click(page):
                        clicks += 1
                await page.wait_for_timeout(random.randint(1200, 2600))

            # guarantee at least one navigation (kills bounce) if none happened
            if not navigated_once and ctx.pages:
                if await navigate_click(page):
                    pageviews += 1
                    clicks += 1
                    log(f"   ➤ navigated to page {pageviews}: {page.url[:70]}")
                    await page.wait_for_timeout(random.randint(1500, 3000))

            clicked = clicks > 0
            status = "success"
            log(f"✅ Visit #{visit_no} done | {country} | IP {ip_used} | {stay:.0f}s | pageviews={pageviews} | clicks={clicks}")
    except Exception as e:
        err = str(e)[:200]
        log(f"❌ Visit #{visit_no} error: {err}")
    finally:
        try:
            if browser is not None:
                await browser.close()
        except Exception:
            pass
        await stop_proxy_bridge(server)

    _save_log({
        "visit_number": visit_no,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "country": country,
        "ip": ip_used,
        "landed_url": landed[:150],
        "pageviews": pageviews,
        "clicks": clicks,
        "random_click": clicked,
        "status": status,
        "error": err,
    })
    return status == "success"


_LOG_LOCK_LIST = []   # simple in-loop guard (single event loop = atomic sync writes)


def _save_log(data):
    logs = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except Exception:
            logs = []
    logs.append(data)
    try:
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


# ---------------- runner (concurrent) ----------------
async def run_all(url, total, countries, concurrency, min_stay, max_stay, headless=True):
    install_quiet_loop()
    concurrency = max(1, min(concurrency, MAX_CONCURRENCY))
    mode = "headless" if headless else "HEADED (visible)"
    log(f"🚀 START | engine: {_ENGINE} | mode: {mode} | visits: {total} | concurrent: {concurrency} | countries: {', '.join(countries)}")
    log(f"🎯 URL: {url}")

    counter = {"next": 1, "ok": 0, "done": 0}

    async def worker(wid):
        while True:
            n = counter["next"]
            if n > total:
                return
            counter["next"] += 1
            country = random.choice(countries)
            try:
                ok = await run_one_visit(n, url, country, min_stay, max_stay, headless)
            except Exception as e:
                log(f"   worker error on #{n}: {str(e)[:80]}")
                ok = False
            counter["done"] += 1
            if ok:
                counter["ok"] += 1
            log(f"   [progress] {counter['done']}/{total} done, {counter['ok']} ok")
            # one session closes -> next opens almost immediately (tiny stagger)
            await asyncio.sleep(random.uniform(0.2, 0.8))

    workers = [asyncio.create_task(worker(w)) for w in range(concurrency)]
    await asyncio.gather(*workers)
    log(f"\n🎉 DONE: {counter['ok']}/{total} visits succeeded. Log -> {LOG_FILE}")


def main():
    # All defaults come from the SETTINGS block at the top, so `python
    # traffic_bot.py` (no args) just uses those. CLI flags are optional overrides.
    ap = argparse.ArgumentParser(description="Concurrent traffic bot (Geonode residential).")
    ap.add_argument("--url", default=URL, help="target URL")
    ap.add_argument("--visits", type=int, default=TOTAL_VISITS, help="total visits")
    ap.add_argument("--concurrency", type=int, default=CONCURRENCY, help="sessions at the same time")
    ap.add_argument("--countries", default=COUNTRIES, help="comma list e.g. IN,US,FR")
    ap.add_argument("--min", type=float, default=MIN_STAY, dest="min_stay", help="min stay seconds")
    ap.add_argument("--max", type=float, default=MAX_STAY, dest="max_stay", help="max stay seconds")
    ap.add_argument("--headed", action="store_true",
                    help="force browser windows (else uses HEADED from SETTINGS)")
    args = ap.parse_args()

    countries = [c.strip().upper() for c in args.countries.split(",") if c.strip()] or ["IN"]
    headless = not (args.headed or HEADED)
    asyncio.run(run_all(args.url, args.visits, countries, args.concurrency,
                        args.min_stay, args.max_stay, headless=headless))


if __name__ == "__main__":
    main()
