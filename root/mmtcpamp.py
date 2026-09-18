import asyncio
import json
import os
import sys
import socket
import random
import string
import threading
import queue
from datetime import datetime
from urllib.parse import urlparse


# When frozen into an .exe, point Playwright at the Chromium we bundle next to
# the executable (so nothing needs to be installed on the target machine).
def _configure_bundled_browsers():
    if getattr(sys, "frozen", False):
        base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
        bundled = os.path.join(base, "ms-playwright")
        if os.path.isdir(bundled):
            os.environ["PLAYWRIGHT_BROWSERS_PATH"] = bundled
        # Skip Playwright's own validation/host-requirements checks
        os.environ.setdefault("PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS", "1")


_configure_bundled_browsers()

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

from playwright.async_api import async_playwright

# ================= GEONODE CONFIG =================
GEONODE_USER_BASE = "geonode_xvmYN44Bvz-type-residential-country-{}"
GEONODE_PASS      = "CHANGE_ME_SECRET"
GEONODE_HOST      = "sg.proxy.geonode.io"
GEONODE_PORT      = "11000"

# ================= DEFAULTS =================
DEFAULT_URL     = "https://partners.marcadeo.com/click?oid=428&uid=416&lid=495"
DEFAULT_VISITS  = 1000
DEFAULT_GEOS    = "IN"
LOG_FILE        = "mmtc_visits.json"
TEXT_LOG_FILE   = "mmtc_visits.txt"

# A full-flow visit stays open this long (seconds), scrolling + random-clicking.
VISIT_SECONDS = (60, 90)

# A "bounce" visit just opens the landing page, stays this long, then leaves.
# Used to raise bounce rate on purpose (see Bounce rate % in the GUI).
BOUNCE_SECONDS = (5, 10)

# Default share of visits that are bounces. e.g. 30 => 30% of visits open the
# URL and close within 5-10s; the remaining 70% run the full engaged flow.
# 0 => every visit runs the full flow (lowest bounce rate).
DEFAULT_BOUNCE_PCT = 0

# Parallel sessions: how many visits run at the same time (each its own browser
# window + IP + fingerprint). 1 = one-at-a-time (original behaviour).
DEFAULT_PARALLEL = 1
MAX_PARALLEL     = 8

# Roughly this % of India visits use Uttar Pradesh IPs; the rest use other
# India states. Geonode does state targeting via "-city-<city>" in the username.
DEFAULT_UP_PCT = 50
UP_CITIES = ["lucknow", "kanpur", "noida", "ghaziabad", "varanasi",
             "agra", "meerut", "prayagraj", "bareilly", "aligarh",
             "moradabad", "gorakhpur", "jhansi", "mathura"]

# Top-level nav options (matched by text inside the header).
NAV_OPTIONS = ["Gold & Silver", "Buyback", "Partner With Us", "About Us", "Blog"]
# The Digital Gold & Silver mega-menu (Buy/Sell/Redeem for Gold and Silver).
DIGITAL_MENU = "Digital Gold & Silver"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
]


# ---------------- Proxy bridge (in-process, no dependencies) ----------------
# Chromium cannot authenticate SOCKS5 (username/password) proxies. So we run a
# tiny in-process HTTP proxy on 127.0.0.1 (no auth) that tunnels every connection
# through the authenticated Geonode SOCKS5 upstream. Chromium then uses the local
# no-auth proxy via Playwright's native proxy option. Pure asyncio, so it works
# fine inside a frozen .exe (no subprocess, no external package).
def _free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


async def _socks5_connect(dst_host, dst_port, user, pw):
    """Open a SOCKS5 tunnel to dst_host:dst_port via the Geonode upstream (RFC1928/1929)."""
    reader, writer = await asyncio.open_connection(GEONODE_HOST, int(GEONODE_PORT))
    # greeting: version 5, 1 method, username/password (0x02)
    writer.write(b"\x05\x01\x02")
    await writer.drain()
    resp = await reader.readexactly(2)
    if resp[1] != 0x02:
        raise OSError("SOCKS5 upstream refused username/password auth")
    # auth (RFC1929)
    ub = user.encode(); pb = pw.encode()
    writer.write(b"\x01" + bytes([len(ub)]) + ub + bytes([len(pb)]) + pb)
    await writer.drain()
    a = await reader.readexactly(2)
    if a[1] != 0x00:
        raise OSError("SOCKS5 auth failed")
    # connect request, address type = domain (0x03)
    db = dst_host.encode()
    writer.write(b"\x05\x01\x00\x03" + bytes([len(db)]) + db + int(dst_port).to_bytes(2, "big"))
    await writer.drain()
    r = await reader.readexactly(4)
    if r[1] != 0x00:
        raise OSError(f"SOCKS5 connect failed (code {r[1]})")
    atyp = r[3]
    if atyp == 0x01:
        await reader.readexactly(4)
    elif atyp == 0x03:
        ln = await reader.readexactly(1)
        await reader.readexactly(ln[0])
    elif atyp == 0x04:
        await reader.readexactly(16)
    await reader.readexactly(2)  # bound port
    return reader, writer


async def _pipe(src_reader, dst_writer):
    try:
        while True:
            data = await src_reader.read(65536)
            if not data:
                break
            dst_writer.write(data)
            await dst_writer.drain()
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
            # read request head
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
                client_writer.write(b"HTTP/1.1 200 Connection established\r\n\r\n")
                await client_writer.drain()
                if leftover:
                    up_writer.write(leftover)
                    await up_writer.drain()
            else:
                u = urlparse(target)
                host = u.hostname
                port = u.port or 80
                up_reader, up_writer = await _socks5_connect(host, int(port), username, GEONODE_PASS)
                path = u.path or "/"
                if u.query:
                    path += "?" + u.query
                rebuilt = header.replace(target.encode(), path.encode(), 1)
                up_writer.write(rebuilt)
                await up_writer.drain()

            await asyncio.gather(
                _pipe(client_reader, up_writer),
                _pipe(up_reader, client_writer),
            )
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
    """Start the in-process HTTP->SOCKS5 bridge. Returns (server, local_port)."""
    local_port = _free_port()
    tasks = set()
    server = await asyncio.start_server(_make_bridge_handler(username, tasks), "127.0.0.1", local_port)
    server._bridge_tasks = tasks
    return server, local_port


def _quiet_exception_handler(loop, context):
    """Swallow benign socket-reset noise from the proxy bridge on Windows.
    When the browser/remote abruptly closes a tunnelled connection, the Proactor
    transport raises ConnectionResetError (WinError 10054) inside its internal
    _call_connection_lost callback. It's harmless, so we silence just those and
    let any real error fall through to the default handler."""
    exc = context.get("exception")
    if isinstance(exc, (ConnectionResetError, ConnectionAbortedError, BrokenPipeError)):
        return
    if isinstance(exc, OSError) and getattr(exc, "winerror", None) in (10053, 10054, 10058):
        return
    if "_call_connection_lost" in str(context.get("message", "")):
        return
    loop.default_exception_handler(context)


def install_quiet_loop():
    """Attach the quiet exception handler to the currently running event loop."""
    try:
        asyncio.get_running_loop().set_exception_handler(_quiet_exception_handler)
    except Exception:
        pass


async def stop_proxy_bridge(server):
    if server is None:
        return
    try:
        server.close()
        await server.wait_closed()
    except Exception:
        pass
    # cancel any lingering tunnel tasks so they don't accumulate across visits
    for t in list(getattr(server, "_bridge_tasks", ())):
        if not t.done():
            t.cancel()


def new_click_id():
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=16))


def build_url(template):
    """Replace the {click_id} placeholder with a fresh random id for this visit."""
    cid = new_click_id()
    return template.replace("{click_id}", cid), cid


def save_log(data):
    logs = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except Exception:
            logs = []
    logs.append(data)
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)


def save_text_log(data):
    """Append one human-readable line per visit to mmtc_visits.txt."""
    line = (
        f"[{data['timestamp']}] Visit #{data['run_number']:<4} "
        f"| {data['status'].upper():<7} "
        f"| {data.get('type', 'full').upper():<6} "
        f"| Geo: {data['geo']:<3} "
        f"| {data.get('state', 'other'):<12} "
        f"| IP: {data.get('ip', 'unknown'):<16} "
        f"| {data.get('seconds', 0):>3}s "
        f"| Nav: {data.get('nav', '')[:22]:<22} "
        f"| Clicks: {data.get('clicks', 0)}"
    )
    if data.get("error"):
        line += f" | Error: {data['error']}"
    with open(TEXT_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


async def get_proxy_ip(context):
    """Fetch the proxy exit IP using the browser (goes through the proxy bridge)."""
    ip = "unknown"
    tmp = None
    try:
        tmp = await context.new_page()
        await tmp.goto("https://api.ipify.org?format=json", timeout=30000, wait_until="domcontentloaded")
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


# ---------------- Human-like helpers ----------------
async def wait_fully_loaded(page, log=None, label="page"):
    """Wait until the page is FULLY loaded (load event + network idle) before
    doing anything, so the visit/click is properly tracked."""
    # 'load' = all resources (scripts/images) finished -> tracking has fired.
    try:
        await page.wait_for_load_state("load", timeout=60000)
    except Exception:
        pass
    # 'networkidle' as best-effort extra insurance, but short timeout so sites
    # with constant analytics beacons don't stall every visit.
    try:
        await page.wait_for_load_state("networkidle", timeout=8000)
    except Exception:
        pass
    # small settle pause
    await page.wait_for_timeout(random.randint(1200, 2500))
    if log:
        log(f"   ✅ {label} fully loaded: {page.url[:75]}")


async def human_scroll(page, rounds=None):
    """Scroll the page down (and sometimes up) a few times, like a human reading."""
    rounds = rounds or random.randint(2, 4)
    for _ in range(rounds):
        dy = random.randint(300, 800)
        if random.random() < 0.25:
            dy = -random.randint(200, 500)
        try:
            await page.mouse.wheel(0, dy)
        except Exception:
            pass
        await page.wait_for_timeout(random.randint(700, 1800))


async def random_click_card(page, log):
    """Scroll to and click a random visible card/link/product in the main content.
    Returns True if something was clicked."""
    try:
        handles = await page.evaluate_handle("""() => {
            const vh = window.innerHeight;
            const sel = 'a[href], [class*="card" i], [class*="product" i], article, [class*="tile" i], img, button';
            const els = [...document.querySelectorAll(sel)].filter(e => {
                const r = e.getBoundingClientRect();
                if (r.width < 40 || r.height < 30) return false;
                if (r.top < 70 || r.top > vh - 20) return false;   // skip header + offscreen
                const t = (e.textContent||'').toLowerCase();
                if (/log\\s*out|sign\\s*out|logout/.test(t)) return false;
                return true;
            });
            return els;
        }""")
        props = await handles.get_properties()
        els = [v.as_element() for v in props.values() if v.as_element()]
        if not els:
            return False
        el = random.choice(els)
        try:
            await el.scroll_into_view_if_needed(timeout=4000)
        except Exception:
            pass
        await page.wait_for_timeout(random.randint(400, 1000))
        label = (await el.text_content() or "").strip().replace("\n", " ")[:24]
        await el.click(timeout=5000)
        log(f"   🖱️  random click: '{label}'")
        return True
    except Exception:
        return False


async def close_popups(page):
    for sel in ['button[aria-label*="close" i]', 'button[title*="close" i]',
                '[class*="close" i]', 'button:has-text("Accept")', 'button:has-text("Got it")',
                'button:has-text("No thanks")', 'button:has-text("Allow")']:
        try:
            loc = page.locator(sel).first
            if await loc.count() > 0 and await loc.is_visible():
                await loc.click(timeout=1500)
                await page.wait_for_timeout(400)
        except Exception:
            pass


async def do_nav_action(page, log):
    """Pick a random nav option and click it. For 'Digital Gold & Silver', hover to
    open the mega-menu and click a random Buy/Sell/Redeem. Returns the nav label used."""
    # 40% chance to use the Digital Gold & Silver mega-menu, else a top nav option
    if random.random() < 0.4:
        try:
            menu = page.locator(f'header >> text="{DIGITAL_MENU}"').first
            if await menu.count() == 0:
                menu = page.locator(f'text="{DIGITAL_MENU}"').first
            await menu.hover(timeout=6000)
            await page.wait_for_timeout(1200)
            # collect visible Buy/Sell/Redeem links in the open mega-menu
            links = page.locator('a')
            picks = []
            n = await links.count()
            for i in range(n):
                a = links.nth(i)
                try:
                    t = (await a.text_content() or "").strip()
                    if t in ("Buy", "Sell", "Redeem") and await a.is_visible():
                        picks.append((t, a))
                except Exception:
                    pass
            if picks:
                t, a = random.choice(picks)
                href = await a.get_attribute("href")
                await a.click(timeout=6000)
                label = f"Digital > {t} ({href})"
                log(f"   🧭 nav: {label}")
                return label
        except Exception as e:
            log(f"   nav menu err {str(e)[:40]}")

    # top-level nav option
    choice = random.choice(NAV_OPTIONS)
    try:
        link = page.locator(f'header >> text="{choice}"').first
        if await link.count() == 0:
            link = page.locator(f'text="{choice}"').first
        await link.click(timeout=8000)
        log(f"   🧭 nav: {choice}")
        return choice
    except Exception as e:
        log(f"   nav click err {str(e)[:40]}")
        return "none"


# ---------------- One visit ----------------
async def run_one_visit(run_number, url_template, country_code, headless, log, up_city=None, bounce=False):
    install_quiet_loop()  # silence benign proxy-bridge socket-reset noise
    username = GEONODE_USER_BASE.format(country_code.lower())
    if up_city:
        username += f"-city-{up_city}"
    geo_label = f"{country_code}/UP-{up_city}" if up_city else country_code
    kind = "BOUNCE" if bounce else "FULL"
    log(f"\n🚀 Visit #{run_number} [{kind}] | Geo: {geo_label} | Proxy: {username}@{GEONODE_HOST}:{GEONODE_PORT}")

    status = "failed"
    err = None
    ip_addr = "unknown"
    nav_label = ""
    clicks = 0
    secs = 0

    url, cid = build_url(url_template)

    # Start the local proxy bridge for this visit (fresh upstream = rotating IP)
    bridge_server, local_port = await start_proxy_bridge(username)

    try:
      async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=headless,
            proxy={"server": f"http://127.0.0.1:{local_port}"},
            args=[
                "--start-maximized",
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-features=IsolateOrigins,site-per-process",
            ],
        )

        ctx_kwargs = dict(
            user_agent=random.choice(USER_AGENTS),
            locale="en-IN",
            timezone_id="Asia/Kolkata",
            ignore_https_errors=True,
            extra_http_headers={"Accept-Language": "en-IN,en;q=0.9"},
        )
        # Headless has no window to maximize -> give it a real desktop viewport so
        # the header nav renders normally (otherwise nav clicks miss).
        if headless:
            ctx_kwargs["viewport"] = {"width": 1366, "height": 768}
        else:
            ctx_kwargs["no_viewport"] = True
        context = await browser.new_context(**ctx_kwargs)
        await context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
        )

        page = await context.new_page()

        try:
            # 0) Capture the proxy exit IP for this visit
            ip_addr = await get_proxy_ip(context)
            log(f"   🌐 Exit IP: {ip_addr} | click_id={cid}")

            import time as _t

            if bounce:
                # BOUNCE visit: just open the landing page, stay briefly, leave.
                # No nav click, no engagement -> counts as a bounce.
                log(f"   ➡️  Opening URL, waiting for full load...")
                await page.goto(url, timeout=90000, wait_until="domcontentloaded")
                await wait_fully_loaded(page, log, "landing")
                await close_popups(page)
                target = random.randint(*BOUNCE_SECONDS)
                log(f"   👋 Bounce visit — staying ~{target}s on first page, then leaving")
                await page.wait_for_timeout(target * 1000)
                secs = target
                nav_label = "(bounce)"
                status = "success"
                log(f"   ✅ Visit #{run_number} done [BOUNCE] | {secs}s on landing page")
            else:
                # 1) Open the affiliate URL, then WAIT for the page to fully load
                #    before doing anything (so the visit is properly tracked).
                log(f"   ➡️  Opening URL, waiting for full load...")
                await page.goto(url, timeout=90000, wait_until="domcontentloaded")
                await wait_fully_loaded(page, log, "landing")
                await close_popups(page)

                # 2) Read + scroll the landing page like a human
                await human_scroll(page)

                # 3) Click a random nav option (or a Digital Gold/Silver menu item),
                #    then wait for that page to fully load before continuing.
                nav_label = await do_nav_action(page, log)
                await wait_fully_loaded(page, log, "nav page")
                await close_popups(page)

                # 4) Keep the visit alive for VISIT_SECONDS: scroll + random clicks
                target = random.randint(*VISIT_SECONDS)
                log(f"   ⏱️  Engaging for ~{target}s (scroll + random clicks)")
                start = _t.monotonic()
                loop_i = 0
                while _t.monotonic() - start < target:
                    await human_scroll(page, rounds=random.randint(1, 3))
                    # random card/link click — always try on the first loop, then often,
                    # so every visit does at least some random clicking.
                    if loop_i == 0 or random.random() < 0.75:
                        if await random_click_card(page, log):
                            clicks += 1
                            # if the click navigated, wait for the new page to load
                            await wait_fully_loaded(page)
                            await close_popups(page)
                    await page.wait_for_timeout(random.randint(1500, 3000))
                    loop_i += 1
                    if not context.pages:
                        break

                secs = int(_t.monotonic() - start)
                status = "success"
                log(f"   ✅ Visit #{run_number} done | nav={nav_label} | clicks={clicks} | {secs}s")

        except Exception as e:
            err = str(e)[:300]
            log(f"   ❌ Visit #{run_number} failed: {err}")
        finally:
            record = {
                "run_number": run_number,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "type": "bounce" if bounce else "full",
                "geo": country_code,
                "state": ("UP-" + up_city) if up_city else "other",
                "ip": ip_addr,
                "click_id": cid,
                "nav": nav_label,
                "clicks": clicks,
                "seconds": secs,
                "status": status,
                "error": err,
            }
            save_log(record)
            save_text_log(record)
            try:
                await browser.close()
            except Exception:
                pass
    finally:
        await stop_proxy_bridge(bridge_server)

    return status == "success"


# ---------------- Runner loop ----------------
async def run_all(url, total, geos, headless, log, stop_event, on_progress,
                  up_pct=DEFAULT_UP_PCT, bounce_pct=DEFAULT_BOUNCE_PCT, parallel=1):
    # Balanced UP schedule: ~up_pct% of visits flagged for a UP city, shuffled.
    up_count = round(total * up_pct / 100.0)
    up_schedule = [True] * up_count + [False] * (total - up_count)
    random.shuffle(up_schedule)
    log(f"📍 UP split: {up_count}/{total} visits will use Uttar Pradesh IPs, "
        f"{total - up_count} other India states.")

    # Bounce schedule: ~bounce_pct% of visits are quick bounces (open + 5-10s +
    # close); the rest run the full engaged flow. Balanced + shuffled.
    bounce_count = round(total * bounce_pct / 100.0)
    bounce_schedule = [True] * bounce_count + [False] * (total - bounce_count)
    random.shuffle(bounce_schedule)
    log(f"🎯 Bounce: {bounce_count}/{total} bounce visits ({bounce_pct}%), "
        f"{total - bounce_count} full-flow visits.")

    parallel = max(1, min(parallel, MAX_PARALLEL))
    log(f"🧵 Running {parallel} session(s) at a time.")

    counter = {"next": 1, "success": 0, "done": 0}

    async def worker(wid):
        while True:
            if stop_event.is_set():
                return
            i = counter["next"]
            if i > total:
                return
            counter["next"] += 1

            country = random.choice(geos)
            # UP city only for India visits; other countries use plain geo.
            up_city = None
            if country == "IN" and up_schedule[i - 1]:
                up_city = random.choice(UP_CITIES)
            is_bounce = bounce_schedule[i - 1]
            try:
                ok = await run_one_visit(i, url, country, headless, log,
                                         up_city=up_city, bounce=is_bounce)
                if ok:
                    counter["success"] += 1
            except Exception as e:
                log(f"   ❌ Unexpected error on visit #{i}: {str(e)[:200]}")

            counter["done"] += 1
            on_progress(counter["done"], total, counter["success"])

            # small stagger before this worker picks up its next visit
            if counter["next"] <= total and not stop_event.is_set():
                await asyncio.sleep(random.uniform(3, 8))

    workers = [asyncio.create_task(worker(w)) for w in range(parallel)]
    await asyncio.gather(*workers)

    done = counter["done"]
    success = counter["success"]
    if stop_event.is_set():
        log("\n⏹️  Stopped by user.")
    failed = done - success
    log(f"\n🎉 Finished. Total: {done} | ✅ Success: {success} | ❌ Failed: {failed}")
    log(f"📄 Detailed log: {TEXT_LOG_FILE}  |  JSON: {LOG_FILE}")


# ================= GUI =================
class MMTCBotGUI:
    def __init__(self, root):
        self.root = root
        root.title("MMTC-PAMP Traffic Bot")
        root.geometry("760x600")

        self.log_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.worker = None

        pad = {"padx": 8, "pady": 4}

        frm = ttk.Frame(root)
        frm.pack(fill="x", padx=10, pady=8)

        # URL (default fixed, editable)
        ttk.Label(frm, text="Click URL:").grid(row=0, column=0, sticky="w", **pad)
        self.url_var = tk.StringVar(value=DEFAULT_URL)
        ttk.Entry(frm, textvariable=self.url_var, width=70).grid(row=0, column=1, columnspan=3, sticky="we", **pad)

        # Total visits
        ttk.Label(frm, text="Total Visits:").grid(row=1, column=0, sticky="w", **pad)
        self.visits_var = tk.StringVar(value=str(DEFAULT_VISITS))
        ttk.Entry(frm, textvariable=self.visits_var, width=12).grid(row=1, column=1, sticky="w", **pad)

        # Geos
        ttk.Label(frm, text="Geos (e.g. IN  or  IN,US):").grid(row=2, column=0, sticky="w", **pad)
        self.geos_var = tk.StringVar(value=DEFAULT_GEOS)
        ttk.Entry(frm, textvariable=self.geos_var, width=30).grid(row=2, column=1, columnspan=2, sticky="w", **pad)

        # UP percentage
        ttk.Label(frm, text="UP IPs % (rest = other India):").grid(row=3, column=0, sticky="w", **pad)
        self.up_var = tk.StringVar(value=str(DEFAULT_UP_PCT))
        ttk.Entry(frm, textvariable=self.up_var, width=8).grid(row=3, column=1, sticky="w", **pad)

        # Bounce rate %: this share of visits just open the URL and close within
        # 5-10s (a bounce). The rest run the full engaged flow. 0 = no bounces.
        ttk.Label(frm, text="Bounce rate % (open + 5-10s + close):").grid(row=4, column=0, sticky="w", **pad)
        self.bounce_var = tk.StringVar(value=str(DEFAULT_BOUNCE_PCT))
        ttk.Entry(frm, textvariable=self.bounce_var, width=8).grid(row=4, column=1, sticky="w", **pad)
        ttk.Label(frm, text="↑ e.g. 30 → 30% bounce, 70% full flow  (0 = all full flow)").grid(
            row=5, column=1, sticky="w", padx=8)

        # Parallel sessions
        ttk.Label(frm, text="Parallel Sessions:").grid(row=6, column=0, sticky="w", **pad)
        self.par_var = tk.StringVar(value=str(DEFAULT_PARALLEL))
        ttk.Entry(frm, textvariable=self.par_var, width=8).grid(row=6, column=1, sticky="w", **pad)
        ttk.Label(frm, text=f"(1 - {MAX_PARALLEL}: how many run at the same time)").grid(
            row=7, column=1, sticky="w", padx=8)

        # Headless
        self.headless_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frm, text="Headless (no window)", variable=self.headless_var).grid(
            row=8, column=1, sticky="w", **pad)

        frm.columnconfigure(1, weight=1)

        # Buttons
        btns = ttk.Frame(root)
        btns.pack(fill="x", padx=10)
        self.start_btn = ttk.Button(btns, text="▶ Start", command=self.start)
        self.start_btn.pack(side="left", padx=5)
        self.stop_btn = ttk.Button(btns, text="⏹ Stop", command=self.stop, state="disabled")
        self.stop_btn.pack(side="left", padx=5)

        # Progress
        self.progress_var = tk.StringVar(value="Idle")
        ttk.Label(root, textvariable=self.progress_var).pack(anchor="w", padx=12, pady=(6, 0))
        self.progress = ttk.Progressbar(root, mode="determinate")
        self.progress.pack(fill="x", padx=10, pady=4)

        # Log box
        self.log_box = scrolledtext.ScrolledText(root, height=22, wrap="word", state="disabled")
        self.log_box.pack(fill="both", expand=True, padx=10, pady=8)

        self.root.after(100, self.drain_log)

    def log(self, msg):
        self.log_queue.put(msg)

    def drain_log(self):
        while not self.log_queue.empty():
            msg = self.log_queue.get_nowait()
            self.log_box.configure(state="normal")
            self.log_box.insert("end", msg + "\n")
            self.log_box.see("end")
            self.log_box.configure(state="disabled")
        self.root.after(100, self.drain_log)

    def set_progress(self, done, total, success):
        def _update():
            self.progress["maximum"] = total
            self.progress["value"] = done
            self.progress_var.set(f"Progress: {done}/{total}  |  Success: {success}")
        self.root.after(0, _update)

    def start(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "URL cannot be empty")
            return
        try:
            total = int(self.visits_var.get().strip())
            if total <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Total Visits must be a positive number")
            return

        geos = [g.strip().upper() for g in self.geos_var.get().split(",") if g.strip()]
        if not geos:
            messagebox.showerror("Error", "Enter at least one geo (e.g. IN)")
            return

        try:
            up_pct = int(self.up_var.get().strip())
            if not (0 <= up_pct <= 100):
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "UP IPs % must be between 0 and 100")
            return

        try:
            bounce_pct = int(self.bounce_var.get().strip())
            if not (0 <= bounce_pct <= 100):
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Bounce rate % must be between 0 and 100")
            return

        try:
            parallel = int(self.par_var.get().strip())
            if not (1 <= parallel <= MAX_PARALLEL):
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", f"Parallel Sessions must be between 1 and {MAX_PARALLEL}")
            return

        headless = self.headless_var.get()

        self.stop_event.clear()
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.log(f"=== Starting: {total} visits | Geos: {', '.join(geos)} | UP: {up_pct}% "
                 f"| Bounce: {bounce_pct}% | Parallel: {parallel} | Headless: {headless} ===")

        self.worker = threading.Thread(
            target=self._run_thread,
            args=(url, total, geos, headless, up_pct, bounce_pct, parallel),
            daemon=True,
        )
        self.worker.start()

    def _run_thread(self, url, total, geos, headless, up_pct, bounce_pct, parallel):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(
                run_all(url, total, geos, headless, self.log, self.stop_event,
                        self.set_progress, up_pct, bounce_pct, parallel)
            )
        except Exception as e:
            self.log(f"❌ Fatal: {str(e)[:300]}")
        finally:
            loop.close()
            self.root.after(0, self._on_done)

    def _on_done(self):
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.progress_var.set(self.progress_var.get() + "  |  DONE")

    def stop(self):
        self.stop_event.set()
        self.log("⏹️  Stop requested... finishing current visit.")
        self.stop_btn.configure(state="disabled")


def _selftest():
    """Non-GUI smoke test: run one headless visit and write the result.
    Used to validate a frozen build end-to-end (bundled Chromium + proxy bridge).
    Windowed-safe: also logs to selftest.log since a GUI exe has no console."""
    logf = open("selftest.log", "w", encoding="utf-8")

    def log(m):
        try:
            print(m, flush=True)
        except Exception:
            pass
        try:
            logf.write(str(m) + "\n")
            logf.flush()
        except Exception:
            pass

    # shorten visit duration for the smoke test
    global VISIT_SECONDS
    VISIT_SECONDS = (20, 25)

    async def _main():
        stop = threading.Event()
        # 2 headed visits (headed = how the tool is actually used), 50% UP,
        # 50% bounce -> exercises both the full flow and a bounce visit.
        await run_all(DEFAULT_URL, 2, ["IN"], False, log, stop, lambda d, t, s: None,
                      up_pct=50, bounce_pct=50)
        return True

    asyncio.run(_main())
    logf.close()
    sys.exit(0)


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        _selftest()
    else:
        root = tk.Tk()
        app = MMTCBotGUI(root)
        root.mainloop()
