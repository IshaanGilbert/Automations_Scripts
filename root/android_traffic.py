"""
Android Traffic Bot
-------------------
Same engine as mmtcpamp.py (Geonode residential SOCKS5 -> in-process HTTP bridge
-> Playwright Chromium), but every visit is opened as an ANDROID PHONE:

  * Android Chrome / Android WebView user-agent
  * phone viewport + device pixel ratio (Pixel / Galaxy / Redmi ...)
  * is_mobile + has_touch  -> the site serves its mobile layout
  * navigator.platform / userAgentData / screen patched to Android
  * scrolling uses real TOUCH swipes (CDP Input.dispatchTouchEvent), not a
    mouse wheel, and clicks are finger taps

You only give a URL - nothing site-specific is hardcoded.
"""

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
DEFAULT_URL     = "https://cric.s932f.com/?lp=arena365.com/sports/?provider=marINR&utm_source=meta.signup"
DEFAULT_VISITS  = 1000
DEFAULT_GEOS    = "IN"
LOG_FILE        = "android_visits.json"
TEXT_LOG_FILE   = "android_visits.txt"

# A full-flow visit stays open this long (seconds), swiping + tapping.
VISIT_SECONDS = (60, 90)

# A "bounce" visit just opens the landing page, stays this long, then leaves.
BOUNCE_SECONDS = (5, 10)

# Default share of visits that are bounces. Real human traffic usually bounces
# 40-60% of the time, so a mid-range value keeps the analytics profile natural
# (0 => every visit is full flow, which looks unnaturally engaged).
DEFAULT_BOUNCE_PCT = 40

# Parallel sessions: how many visits run at the same time.
DEFAULT_PARALLEL = 1
MAX_PARALLEL     = 8

# Roughly this % of India visits use Uttar Pradesh IPs; the rest other states.
DEFAULT_UP_PCT = 20
UP_CITIES = ["lucknow", "kanpur", "noida", "ghaziabad", "varanasi",
             "agra", "meerut", "prayagraj", "bareilly", "aligarh",
             "moradabad", "gorakhpur", "jhansi", "mathura"]

# ================= ANDROID DEVICE PROFILES =================
# Real phone metrics. "chrome" = normal Android Chrome UA, "webview" = the
# in-app browser UA (has the "; wv" token) used when an app like Instagram /
# Facebook / Gmail opens a link inside itself.
ANDROID_DEVICES = [
    # (name, android_ver, model, build, width, height, dpr)
    ("Pixel 8",           "14", "Pixel 8",     "UP1A.231005.007", 412, 915, 2.625),
    ("Pixel 7",           "13", "Pixel 7",     "TQ3A.230805.001", 412, 915, 2.625),
    ("Pixel 6a",          "13", "Pixel 6a",    "TQ2A.230505.002", 412, 892, 2.625),
    ("Galaxy S23",        "14", "SM-S911B",    "UP1A.231005.007", 360, 780, 3.0),
    ("Galaxy S22",        "13", "SM-S901E",    "TP1A.220624.014", 360, 780, 3.0),
    ("Galaxy A54",        "13", "SM-A546E",    "TP1A.220624.014", 360, 800, 3.0),
    ("Galaxy M14",        "13", "SM-M146B",    "TP1A.220624.014", 360, 800, 3.0),
    ("OnePlus 11",        "13", "CPH2447",     "TP1A.220905.001", 412, 919, 3.5),
    ("OnePlus Nord CE3",  "13", "CPH2569",     "TP1A.220905.001", 393, 873, 2.75),
    ("Redmi Note 12",     "13", "23021RAAEG",  "TP1A.220624.014", 393, 873, 2.75),
    ("Redmi Note 11",     "12", "21091116AI",  "SP1A.210812.016", 393, 873, 2.75),
    ("Poco X5 Pro",       "13", "22101320G",   "TP1A.220624.014", 393, 873, 2.75),
    ("Vivo Y100",         "13", "V2239",       "TP1A.220624.014", 393, 873, 2.75),
    ("Realme 11 Pro",     "13", "RMX3771",     "TP1A.220624.014", 393, 873, 2.75),
    ("Moto G84",          "13", "moto g84 5G", "TP1A.220624.014", 393, 873, 2.75),
]

# Chrome major versions seen on Android in the wild.
CHROME_VERSIONS = ["131.0.6778.200", "132.0.6834.163", "133.0.6943.121",
                   "134.0.6998.135", "135.0.7049.95"]


def pick_android(view_mode="mixed"):
    """Return one random Android device profile + its user agent.

    view_mode: "chrome"  -> Android Chrome UA
               "webview" -> Android WebView / in-app browser UA
               "mixed"   -> ~50/50 between the two
    """
    name, android_ver, model, build, w, h, dpr = random.choice(ANDROID_DEVICES)
    chrome_full = random.choice(CHROME_VERSIONS)
    chrome_major = chrome_full.split(".")[0]

    mode = random.choice(["chrome", "webview"]) if view_mode == "mixed" else view_mode

    if mode == "webview":
        ua = (f"Mozilla/5.0 (Linux; Android {android_ver}; {model} Build/{build}; wv) "
              f"AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 "
              f"Chrome/{chrome_full} Mobile Safari/537.36")
    else:
        ua = (f"Mozilla/5.0 (Linux; Android {android_ver}; {model}) "
              f"AppleWebKit/537.36 (KHTML, like Gecko) "
              f"Chrome/{chrome_full} Mobile Safari/537.36")

    return {
        "name": name,
        "mode": mode,
        "model": model,
        "android": android_ver,
        "ua": ua,
        "chrome_major": chrome_major,
        "width": w,
        "height": h,
        "dpr": dpr,
    }


# ---------------- Proxy bridge (in-process, no dependencies) ----------------
# Chromium cannot authenticate SOCKS5 proxies, so we run a tiny local HTTP proxy
# (no auth) that tunnels every connection through the authenticated Geonode
# SOCKS5 upstream. Pure asyncio, so it also works inside a frozen .exe.
def _free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


async def _socks5_connect(dst_host, dst_port, user, pw):
    """Open a SOCKS5 tunnel to dst_host:dst_port via Geonode (RFC1928/1929)."""
    reader, writer = await asyncio.open_connection(GEONODE_HOST, int(GEONODE_PORT))
    writer.write(b"\x05\x01\x02")
    await writer.drain()
    resp = await reader.readexactly(2)
    if resp[1] != 0x02:
        raise OSError("SOCKS5 upstream refused username/password auth")
    ub = user.encode(); pb = pw.encode()
    writer.write(b"\x01" + bytes([len(ub)]) + ub + bytes([len(pb)]) + pb)
    await writer.drain()
    a = await reader.readexactly(2)
    if a[1] != 0x00:
        raise OSError("SOCKS5 auth failed")
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
    """Swallow benign socket-reset noise from the proxy bridge on Windows."""
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


async def stop_proxy_bridge(server):
    if server is None:
        return
    try:
        server.close()
        await server.wait_closed()
    except Exception:
        pass
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
    """Append one human-readable line per visit to android_visits.txt."""
    line = (
        f"[{data['timestamp']}] Visit #{data['run_number']:<4} "
        f"| {data['status'].upper():<7} "
        f"| {data.get('type', 'full').upper():<6} "
        f"| Geo: {data['geo']:<3} "
        f"| {data.get('state', 'other'):<12} "
        f"| IP: {data.get('ip', 'unknown'):<16} "
        f"| {data.get('device', ''):<16} "
        f"| {data.get('view', ''):<7} "
        f"| {data.get('seconds', 0):>3}s "
        f"| Pages: {data.get('pages', 1)} "
        f"| Taps: {data.get('clicks', 0)}"
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


# ---------------- Android fingerprint patch ----------------
def android_init_script(dev):
    """JS injected before any page script runs, so the page really believes it is
    a phone (platform, touch points, userAgentData, screen, no webdriver)."""
    return f"""
    Object.defineProperty(navigator, 'webdriver', {{get: () => undefined}});
    Object.defineProperty(navigator, 'platform', {{get: () => 'Linux armv8l'}});
    Object.defineProperty(navigator, 'maxTouchPoints', {{get: () => 5}});
    Object.defineProperty(navigator, 'vendor', {{get: () => 'Google Inc.'}});
    Object.defineProperty(navigator, 'hardwareConcurrency', {{get: () => 8}});
    Object.defineProperty(navigator, 'deviceMemory', {{get: () => 4}});
    try {{
      Object.defineProperty(navigator, 'userAgentData', {{
        get: () => ({{
          mobile: true,
          platform: 'Android',
          brands: [
            {{brand: 'Chromium', version: '{dev["chrome_major"]}'}},
            {{brand: 'Google Chrome', version: '{dev["chrome_major"]}'}},
            {{brand: 'Not?A_Brand', version: '24'}}
          ],
          getHighEntropyValues: async () => ({{
            architecture: '', bitness: '64', mobile: true,
            model: '{dev["model"]}', platform: 'Android',
            platformVersion: '{dev["android"]}',
            uaFullVersion: '{dev["chrome_major"]}.0.0.0'
          }})
        }})
      }});
    }} catch (e) {{}}
    try {{
      Object.defineProperty(window.screen, 'width',  {{get: () => {dev["width"]}}});
      Object.defineProperty(window.screen, 'height', {{get: () => {dev["height"]}}});
      Object.defineProperty(window.screen, 'availWidth',  {{get: () => {dev["width"]}}});
      Object.defineProperty(window.screen, 'availHeight', {{get: () => {dev["height"]}}});
      Object.defineProperty(window.screen, 'colorDepth',  {{get: () => 24}});
      Object.defineProperty(window.screen, 'orientation', {{
        get: () => ({{type: 'portrait-primary', angle: 0}})
      }});
    }} catch (e) {{}}
    try {{ window.ontouchstart = null; }} catch (e) {{}}
    """


# ---------------- Human-like (touch) helpers ----------------
async def wait_fully_loaded(page, log=None, label="page"):
    """Wait until the page is FULLY loaded (load event + network idle) before we
    touch anything, so the visit/click is properly tracked."""
    try:
        await page.wait_for_load_state("load", timeout=60000)
    except Exception:
        pass
    try:
        await page.wait_for_load_state("networkidle", timeout=8000)
    except Exception:
        pass
    await page.wait_for_timeout(random.randint(1200, 2500))
    if log:
        try:
            log(f"   [ok] {label} fully loaded: {page.url[:75]}")
        except Exception:
            pass


async def touch_swipe(page, up=True):
    """A real finger swipe: touchStart -> several touchMove -> touchEnd, sent via
    CDP so the page sees genuine touch events (not a mouse wheel)."""
    try:
        vw = page.viewport_size["width"]
        vh = page.viewport_size["height"]
    except Exception:
        vw, vh = 393, 873

    x = random.randint(int(vw * 0.35), int(vw * 0.65))
    dist = random.randint(int(vh * 0.35), int(vh * 0.70))
    if up:
        y0 = random.randint(int(vh * 0.65), int(vh * 0.85))
        y1 = max(40, y0 - dist)
    else:
        y0 = random.randint(int(vh * 0.20), int(vh * 0.40))
        y1 = min(vh - 40, y0 + dist)

    try:
        cdp = await page.context.new_cdp_session(page)
        await cdp.send("Input.dispatchTouchEvent", {
            "type": "touchStart",
            "touchPoints": [{"x": x, "y": y0, "radiusX": 12, "radiusY": 12, "force": 1}],
        })
        steps = random.randint(8, 14)
        for i in range(1, steps + 1):
            yy = y0 + (y1 - y0) * (i / steps)
            xx = x + random.randint(-3, 3)   # fingers wobble
            await cdp.send("Input.dispatchTouchEvent", {
                "type": "touchMove",
                "touchPoints": [{"x": xx, "y": yy, "radiusX": 12, "radiusY": 12, "force": 1}],
            })
            await page.wait_for_timeout(random.randint(12, 30))
        await cdp.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []})
        try:
            await cdp.detach()
        except Exception:
            pass
        return True
    except Exception:
        # Fallback: plain JS scroll if CDP is unavailable for this page
        try:
            dy = dist if up else -dist
            await page.evaluate("(d) => window.scrollBy({top: d, behavior: 'smooth'})", dy)
            return True
        except Exception:
            return False


async def human_scroll(page, rounds=None):
    """Swipe through the page a few times, mostly down, sometimes back up, with a
    pause after each swipe like someone actually reading."""
    rounds = rounds or random.randint(2, 4)
    for _ in range(rounds):
        await touch_swipe(page, up=(random.random() > 0.22))   # 22% swipe back up
        await page.wait_for_timeout(random.randint(700, 1900))


async def tap(page, el):
    """Tap an element the way a finger would: scroll it into view, then dispatch
    touchStart/touchEnd at its centre (falls back to a normal click)."""
    try:
        await el.scroll_into_view_if_needed(timeout=4000)
    except Exception:
        pass
    await page.wait_for_timeout(random.randint(300, 900))
    try:
        box = await el.bounding_box()
        if box:
            x = box["x"] + box["width"] / 2 + random.uniform(-4, 4)
            y = box["y"] + box["height"] / 2 + random.uniform(-4, 4)
            cdp = await page.context.new_cdp_session(page)
            await cdp.send("Input.dispatchTouchEvent", {
                "type": "touchStart",
                "touchPoints": [{"x": x, "y": y, "radiusX": 12, "radiusY": 12, "force": 1}],
            })
            await page.wait_for_timeout(random.randint(60, 140))
            await cdp.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []})
            try:
                await cdp.detach()
            except Exception:
                pass
            return True
    except Exception:
        pass
    try:
        await el.click(timeout=5000)
        return True
    except Exception:
        return False


async def open_mobile_menu(page, log):
    """Phones hide the nav behind a hamburger. Try to open it so the menu links
    are actually tappable. Returns True if a menu was opened."""
    for sel in ['button[aria-label*="menu" i]', '[aria-label*="menu" i]',
                'button[class*="hamburger" i]', '[class*="hamburger" i]',
                '[class*="menu-toggle" i]', '[class*="mobile-menu" i] button',
                'header button:has(svg)']:
        try:
            loc = page.locator(sel).first
            if await loc.count() > 0 and await loc.is_visible():
                await tap(page, loc)
                await page.wait_for_timeout(random.randint(800, 1600))
                log("   [menu] opened mobile menu")
                return True
        except Exception:
            pass
    return False


async def close_popups(page):
    for sel in ['button[aria-label*="close" i]', 'button[title*="close" i]',
                '[class*="close" i]', 'button:has-text("Accept")',
                'button:has-text("Accept All")', 'button:has-text("Got it")',
                'button:has-text("No thanks")', 'button:has-text("Allow")',
                'button:has-text("Continue")', '[id*="onetrust-accept" i]']:
        try:
            loc = page.locator(sel).first
            if await loc.count() > 0 and await loc.is_visible():
                await loc.click(timeout=1500)
                await page.wait_for_timeout(400)
        except Exception:
            pass


async def tap_internal_link(page, log):
    """Pick a random visible SAME-SITE link on screen and tap it, so the visit
    moves to a second page (this is what kills the bounce). Fully generic."""
    try:
        handles = await page.evaluate_handle("""() => {
            const vh = window.innerHeight, host = location.hostname;
            const bad = /log\\s*out|sign\\s*out|logout|unsubscribe|mailto:|tel:|javascript:|\\.pdf$/i;
            return [...document.querySelectorAll('a[href]')].filter(a => {
                const href = a.getAttribute('href') || '';
                if (bad.test(href) || bad.test(a.textContent || '')) return false;
                let u; try { u = new URL(a.href, location.href); } catch (e) { return false; }
                if (!/^https?:$/.test(u.protocol)) return false;
                if (u.hostname !== host) return false;                  // same site only
                if (u.href.replace(/#.*$/, '') === location.href.replace(/#.*$/, '')) return false;
                const r = a.getBoundingClientRect();
                if (r.width < 30 || r.height < 20) return false;
                if (r.top < 0 || r.top > vh - 20) return false;         // must be on screen
                return true;
            });
        }""")
        props = await handles.get_properties()
        els = [v.as_element() for v in props.values() if v.as_element()]
        if not els:
            return False, ""
        el = random.choice(els)
        label = (await el.text_content() or "").strip().replace("\n", " ")[:28]
        href = await el.get_attribute("href")
        if await tap(page, el):
            log(f"   [tap] link: '{label}' -> {str(href)[:50]}")
            return True, (label or href or "link")
        return False, ""
    except Exception:
        return False, ""


async def tap_anything(page, log):
    """Tap a random visible card/image/button in the content area - engagement
    even when there is no obvious link to follow."""
    try:
        handles = await page.evaluate_handle("""() => {
            const vh = window.innerHeight;
            const sel = 'a[href], [class*="card" i], [class*="product" i], article, [class*="tile" i], img, button';
            return [...document.querySelectorAll(sel)].filter(e => {
                const r = e.getBoundingClientRect();
                if (r.width < 40 || r.height < 30) return false;
                if (r.top < 60 || r.top > vh - 20) return false;
                const t = (e.textContent || '').toLowerCase();
                if (/log\\s*out|sign\\s*out|logout/.test(t)) return false;
                return true;
            });
        }""")
        props = await handles.get_properties()
        els = [v.as_element() for v in props.values() if v.as_element()]
        if not els:
            return False
        el = random.choice(els)
        label = (await el.text_content() or "").strip().replace("\n", " ")[:24]
        if await tap(page, el):
            log(f"   [tap] '{label}'")
            return True
        return False
    except Exception:
        return False


# ---------------- One visit ----------------
async def run_one_visit(run_number, url_template, country_code, headless, log,
                        up_city=None, bounce=False, view_mode="mixed"):
    install_quiet_loop()  # silence benign proxy-bridge socket-reset noise
    username = GEONODE_USER_BASE.format(country_code.lower())
    if up_city:
        username += f"-city-{up_city}"
    geo_label = f"{country_code}/UP-{up_city}" if up_city else country_code
    kind = "BOUNCE" if bounce else "FULL"

    dev = pick_android(view_mode)
    log(f"\n[Visit #{run_number}] [{kind}] | Geo: {geo_label} "
        f"| {dev['name']} (Android {dev['android']}, {dev['mode']}) "
        f"{dev['width']}x{dev['height']}@{dev['dpr']}x")
    log(f"   Proxy: {username}@{GEONODE_HOST}:{GEONODE_PORT}")

    status = "failed"
    err = None
    ip_addr = "unknown"
    nav_label = ""
    clicks = 0
    pages_seen = 1
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
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-features=IsolateOrigins,site-per-process",
                # phone-sized window so the headed run also looks like a phone
                f"--window-size={dev['width']},{dev['height'] + 120}",
                f"--user-agent={dev['ua']}",
            ],
        )

        # THE ANDROID VIEW: phone viewport + DPR + touch + mobile flag.
        context = await browser.new_context(
            user_agent=dev["ua"],
            viewport={"width": dev["width"], "height": dev["height"]},
            screen={"width": dev["width"], "height": dev["height"]},
            device_scale_factor=dev["dpr"],
            is_mobile=True,
            has_touch=True,
            locale="en-IN",
            timezone_id="Asia/Kolkata",
            ignore_https_errors=True,
            extra_http_headers={
                "Accept-Language": "en-IN,en;q=0.9",
                "sec-ch-ua-mobile": "9999999999",
                "sec-ch-ua-platform": '"Android"',
            },
        )
        await context.add_init_script(android_init_script(dev))

        page = await context.new_page()

        try:
            # 0) Capture the proxy exit IP for this visit
            ip_addr = await get_proxy_ip(context)
            log(f"   Exit IP: {ip_addr} | click_id={cid}")

            import time as _t

            # 1) Open the URL and WAIT for a full load before touching anything,
            #    so the visit is properly tracked.
            log("   Opening URL in Android view, waiting for full load...")
            await page.goto(url, timeout=90000, wait_until="domcontentloaded")
            await wait_fully_loaded(page, log, "landing")
            await close_popups(page)

            if bounce:
                # BOUNCE visit: land, stay briefly, leave. No engagement.
                target = random.randint(*BOUNCE_SECONDS)
                log(f"   Bounce visit - staying ~{target}s on the landing page")
                await page.wait_for_timeout(target * 1000)
                secs = target
                nav_label = "(bounce)"
                status = "success"
                log(f"   [ok] Visit #{run_number} done [BOUNCE] | {secs}s")
            else:
                # 2) Read the landing page with finger swipes
                await human_scroll(page)

                # 3) Move to a second page: a hamburger-menu link if there is one,
                #    otherwise any same-site link on screen.
                opened = await open_mobile_menu(page, log)
                moved, nav_label = await tap_internal_link(page, log)
                if opened and not moved:
                    # menu was open but nothing tappable -> close it and retry
                    try:
                        await page.keyboard.press("Escape")
                    except Exception:
                        pass
                    await page.wait_for_timeout(600)
                    moved, nav_label = await tap_internal_link(page, log)
                if moved:
                    pages_seen += 1
                    clicks += 1
                    await wait_fully_loaded(page, log, "next page")
                    await close_popups(page)
                else:
                    nav_label = "(no link)"
                    log("   no internal link found - staying on the landing page")

                # 4) Keep the visit alive for VISIT_SECONDS: swipe + tap around
                target = random.randint(*VISIT_SECONDS)
                log(f"   Engaging for ~{target}s (touch swipes + taps)")
                start = _t.monotonic()
                loop_i = 0
                while _t.monotonic() - start < target:
                    await human_scroll(page, rounds=random.randint(1, 3))
                    # always tap on the first loop, then often, so every visit
                    # does at least some real engagement
                    if loop_i == 0 or random.random() < 0.7:
                        before = page.url
                        did = False
                        if random.random() < 0.6:
                            did, _lbl = await tap_internal_link(page, log)
                        if not did:
                            did = await tap_anything(page, log)
                        if did:
                            clicks += 1
                            await wait_fully_loaded(page)
                            await close_popups(page)
                            if page.url != before:
                                pages_seen += 1
                    # occasional back-navigation, like a real phone user
                    if pages_seen > 1 and random.random() < 0.15:
                        try:
                            await page.go_back(timeout=15000)
                            log("   [back]")
                            await wait_fully_loaded(page)
                        except Exception:
                            pass
                    await page.wait_for_timeout(random.randint(1500, 3000))
                    loop_i += 1
                    if not context.pages:
                        break

                secs = int(_t.monotonic() - start)
                status = "success"
                log(f"   [ok] Visit #{run_number} done | pages={pages_seen} "
                    f"| taps={clicks} | {secs}s")

        except Exception as e:
            err = str(e)[:300]
            log(f"   [x] Visit #{run_number} failed: {err}")
        finally:
            record = {
                "run_number": run_number,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "type": "bounce" if bounce else "full",
                "geo": country_code,
                "state": ("UP-" + up_city) if up_city else "other",
                "ip": ip_addr,
                "click_id": cid,
                "device": dev["name"],
                "view": dev["mode"],
                "android": dev["android"],
                "user_agent": dev["ua"],
                "viewport": f"{dev['width']}x{dev['height']}@{dev['dpr']}x",
                "nav": nav_label,
                "pages": pages_seen,
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
                  up_pct=DEFAULT_UP_PCT, bounce_pct=DEFAULT_BOUNCE_PCT,
                  parallel=1, view_mode="mixed"):
    # Balanced UP schedule: ~up_pct% of visits flagged for a UP city, shuffled.
    up_count = round(total * up_pct / 100.0)
    up_schedule = [True] * up_count + [False] * (total - up_count)
    random.shuffle(up_schedule)
    log(f"UP split: {up_count}/{total} visits will use Uttar Pradesh IPs, "
        f"{total - up_count} other India states.")

    # Bounce schedule: ~bounce_pct% quick bounces, the rest full flow.
    bounce_count = round(total * bounce_pct / 100.0)
    bounce_schedule = [True] * bounce_count + [False] * (total - bounce_count)
    random.shuffle(bounce_schedule)
    log(f"Bounce: {bounce_count}/{total} bounce visits ({bounce_pct}%), "
        f"{total - bounce_count} full-flow visits.")

    log(f"Android view mode: {view_mode}"
        f"{' (Chrome + WebView mixed)' if view_mode == 'mixed' else ''}")

    parallel = max(1, min(parallel, MAX_PARALLEL))
    log(f"Running {parallel} session(s) at a time.")

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
            # UP city only for India visits; other countries use the plain geo.
            up_city = None
            if country == "IN" and up_schedule[i - 1]:
                up_city = random.choice(UP_CITIES)
            is_bounce = bounce_schedule[i - 1]
            try:
                ok = await run_one_visit(i, url, country, headless, log,
                                         up_city=up_city, bounce=is_bounce,
                                         view_mode=view_mode)
                if ok:
                    counter["success"] += 1
            except Exception as e:
                log(f"   [x] Unexpected error on visit #{i}: {str(e)[:200]}")

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
        log("\nStopped by user.")
    failed = done - success
    log(f"\nFinished. Total: {done} | Success: {success} | Failed: {failed}")
    log(f"Detailed log: {TEXT_LOG_FILE}  |  JSON: {LOG_FILE}")


# ================= GUI =================
class AndroidBotGUI:
    def __init__(self, root):
        self.root = root
        root.title("Android Traffic Bot (Geonode)")
        root.geometry("790x650")

        self.log_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.worker = None

        pad = {"padx": 8, "pady": 4}

        frm = ttk.Frame(root)
        frm.pack(fill="x", padx=10, pady=8)

        # URL
        ttk.Label(frm, text="Target URL:").grid(row=0, column=0, sticky="w", **pad)
        self.url_var = tk.StringVar(value=DEFAULT_URL)
        ttk.Entry(frm, textvariable=self.url_var, width=70).grid(
            row=0, column=1, columnspan=3, sticky="we", **pad)
        ttk.Label(frm, text="(put {click_id} in the URL for a fresh random id per visit)").grid(
            row=1, column=1, sticky="w", padx=8)

        # Total visits
        ttk.Label(frm, text="Total Visits:").grid(row=2, column=0, sticky="w", **pad)
        self.visits_var = tk.StringVar(value=str(DEFAULT_VISITS))
        ttk.Entry(frm, textvariable=self.visits_var, width=12).grid(row=2, column=1, sticky="w", **pad)

        # Geos
        ttk.Label(frm, text="Geos (e.g. IN  or  IN,US):").grid(row=3, column=0, sticky="w", **pad)
        self.geos_var = tk.StringVar(value=DEFAULT_GEOS)
        ttk.Entry(frm, textvariable=self.geos_var, width=30).grid(
            row=3, column=1, columnspan=2, sticky="w", **pad)

        # Android view mode
        ttk.Label(frm, text="Android view:").grid(row=4, column=0, sticky="w", **pad)
        self.view_var = tk.StringVar(value="mixed")
        ttk.Combobox(frm, textvariable=self.view_var, width=14, state="readonly",
                     values=["mixed", "chrome", "webview"]).grid(row=4, column=1, sticky="w", **pad)
        ttk.Label(frm, text="chrome = Android Chrome | webview = in-app browser | mixed = both").grid(
            row=5, column=1, sticky="w", padx=8)

        # UP percentage
        ttk.Label(frm, text="UP IPs % (rest = other India):").grid(row=6, column=0, sticky="w", **pad)
        self.up_var = tk.StringVar(value=str(DEFAULT_UP_PCT))
        ttk.Entry(frm, textvariable=self.up_var, width=8).grid(row=6, column=1, sticky="w", **pad)

        # Bounce rate %
        ttk.Label(frm, text="Bounce rate % (open + 5-10s + close):").grid(row=7, column=0, sticky="w", **pad)
        self.bounce_var = tk.StringVar(value=str(DEFAULT_BOUNCE_PCT))
        ttk.Entry(frm, textvariable=self.bounce_var, width=8).grid(row=7, column=1, sticky="w", **pad)
        ttk.Label(frm, text="e.g. 30 -> 30% bounce, 70% full flow  (0 = all full flow)").grid(
            row=8, column=1, sticky="w", padx=8)

        # Parallel sessions
        ttk.Label(frm, text="Parallel Sessions:").grid(row=9, column=0, sticky="w", **pad)
        self.par_var = tk.StringVar(value=str(DEFAULT_PARALLEL))
        ttk.Entry(frm, textvariable=self.par_var, width=8).grid(row=9, column=1, sticky="w", **pad)
        ttk.Label(frm, text=f"(1 - {MAX_PARALLEL}: how many run at the same time)").grid(
            row=10, column=1, sticky="w", padx=8)

        # Headless
        self.headless_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frm, text="Headless (no window)", variable=self.headless_var).grid(
            row=11, column=1, sticky="w", **pad)

        frm.columnconfigure(1, weight=1)

        # Buttons
        btns = ttk.Frame(root)
        btns.pack(fill="x", padx=10)
        self.start_btn = ttk.Button(btns, text="Start", command=self.start)
        self.start_btn.pack(side="left", padx=5)
        self.stop_btn = ttk.Button(btns, text="Stop", command=self.stop, state="disabled")
        self.stop_btn.pack(side="left", padx=5)

        # Progress
        self.progress_var = tk.StringVar(value="Idle")
        ttk.Label(root, textvariable=self.progress_var).pack(anchor="w", padx=12, pady=(6, 0))
        self.progress = ttk.Progressbar(root, mode="determinate")
        self.progress.pack(fill="x", padx=10, pady=4)

        # Log box
        self.log_box = scrolledtext.ScrolledText(root, height=20, wrap="word", state="disabled")
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
        if not url.lower().startswith(("http://", "https://")):
            messagebox.showerror("Error", "URL must start with http:// or https://")
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
        view_mode = self.view_var.get()

        self.stop_event.clear()
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.log(f"=== Starting: {total} visits | Geos: {', '.join(geos)} | UP: {up_pct}% "
                 f"| Bounce: {bounce_pct}% | Parallel: {parallel} | View: {view_mode} "
                 f"| Headless: {headless} ===")

        self.worker = threading.Thread(
            target=self._run_thread,
            args=(url, total, geos, headless, up_pct, bounce_pct, parallel, view_mode),
            daemon=True,
        )
        self.worker.start()

    def _run_thread(self, url, total, geos, headless, up_pct, bounce_pct, parallel, view_mode):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(
                run_all(url, total, geos, headless, self.log, self.stop_event,
                        self.set_progress, up_pct, bounce_pct, parallel, view_mode)
            )
        except Exception as e:
            self.log(f"Fatal: {str(e)[:300]}")
        finally:
            loop.close()
            self.root.after(0, self._on_done)

    def _on_done(self):
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.progress_var.set(self.progress_var.get() + "  |  DONE")

    def stop(self):
        self.stop_event.set()
        self.log("Stop requested... finishing current visit.")
        self.stop_btn.configure(state="disabled")


def _cli():
    """Console runner (no GUI):
        python android_traffic.py --url https://site.com --visits 20 --geo IN \
            --view webview --parallel 2 --bounce 30 --headless
    """
    import argparse
    ap = argparse.ArgumentParser(description="Android Traffic Bot (Geonode)")
    ap.add_argument("--url", required=True)
    ap.add_argument("--visits", type=int, default=1)
    ap.add_argument("--geo", default="IN", help="comma separated, e.g. IN,US")
    ap.add_argument("--view", default="mixed", choices=["mixed", "chrome", "webview"])
    ap.add_argument("--up", type=int, default=DEFAULT_UP_PCT)
    ap.add_argument("--bounce", type=int, default=DEFAULT_BOUNCE_PCT)
    ap.add_argument("--parallel", type=int, default=1)
    ap.add_argument("--headless", action="store_true")
    ap.add_argument("--seconds", type=int, default=0,
                    help="override engaged time per visit (seconds)")
    a = ap.parse_args()

    if a.seconds:
        global VISIT_SECONDS
        VISIT_SECONDS = (a.seconds, a.seconds)

    # A windowed .exe has no console, so print() silently goes nowhere. Tee every
    # line to a file next to the exe as well, so CLI runs are still readable.
    logf = open("android_bot_console.log", "a", encoding="utf-8")
    logf.write(f"\n===== run started {datetime.now():%Y-%m-%d %H:%M:%S} =====\n")

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

    geos = [g.strip().upper() for g in a.geo.split(",") if g.strip()]
    stop = threading.Event()
    try:
        asyncio.run(run_all(a.url, a.visits, geos, a.headless, log, stop,
                            lambda d, t, s: None, a.up, a.bounce, a.parallel, a.view))
    finally:
        logf.close()


def _selftest():
    """Non-GUI smoke test: 2 short Android visits -> selftest_android.log."""
    logf = open("selftest_android.log", "w", encoding="utf-8")

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

    global VISIT_SECONDS
    VISIT_SECONDS = (20, 25)

    stop = threading.Event()
    asyncio.run(run_all(DEFAULT_URL, 2, ["IN"], False, log, stop, lambda d, t, s: None,
                        up_pct=50, bounce_pct=50, parallel=1, view_mode="mixed"))
    logf.close()
    sys.exit(0)


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        _selftest()
    elif "--url" in sys.argv:
        _cli()
    else:
        root = tk.Tk()
        app = AndroidBotGUI(root)
        root.mainloop()
