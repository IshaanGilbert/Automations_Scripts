"""
Skyscanner flight-search traffic bot  (standalone, production-grade).

What one visit does (like a real user):
  * fresh Geonode India residential IP + a randomly chosen browser fingerprint
    (user-agent, platform, viewport, locale, client-hints, WebGL/plugins stealth)
  * open the affiliate link -> Skyscanner homepage
  * clear ANY popup/consent wall that shows up (on every page, even inside iframes)
  * if the PerimeterX "PRESS & HOLD" wall appears, hold it until we're inside
  * pick a RANDOM route (from-city, to-city) and a RANDOM future depart date
  * one-way, uncheck "add a place to stay", Search -> flight results
  * pick a random flight card:
        - "Select"       -> same-tab offer ("Book your ticket") page
        - "View details" -> new-tab offer page
  * on the offer page click a random "Go to site" -> provider/airline site (new tab)
  * on the provider site: clear popups, scroll, do a few random clicks

Robustness:
  * inputs are filled by focusing via JS + typing (works even behind an overlay),
    so slow/quirky page loads don't abort the visit
  * long timeouts everywhere for slow networks
  * if a visit can't complete on one IP, it rotates to a fresh IP and retries
  * every visit is logged step-by-step to sky_visits.json + sky_visits.txt,
    for both success and failure

Requires:  pip install playwright   &&   playwright install chrome
Uses real Chrome (channel="chrome"); the bundled Chromium is always blocked by
PerimeterX, real Chrome passes the PRESS & HOLD.

Run:       python skyscanner_final.py            (1 visit)
           python skyscanner_final.py 25          (25 visits)
"""

import asyncio
import json
import os
import sys
import socket
import random
import queue
import threading
import contextvars
from datetime import datetime
from urllib.parse import urlparse

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox


# When frozen into an .exe, skip Playwright's host-requirement validation. We use
# the system's real Google Chrome (channel="chrome"), so no browser is bundled —
# the target machine just needs Google Chrome installed (almost every PC has it).
def _configure_frozen():
    if getattr(sys, "frozen", False):
        os.environ.setdefault("PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS", "1")


_configure_frozen()

from playwright.async_api import async_playwright

# Current visit number for the running task — lets parallel sessions tag their
# log lines (e.g. "[V3] ...") so interleaved output stays readable.
_visit_ctx = contextvars.ContextVar("visit_no", default=None)

# Optional GUI log sink: when the GUI is running, log() also pushes each line here.
_LOG_SINK = None

# ================= GEONODE CONFIG =================
GEONODE_USER_BASE = "geonode_xvmYN44Bvz-type-residential-country-{}"
GEONODE_PASS      = "CHANGE_ME_SECRET"
GEONODE_HOST      = "sg.proxy.geonode.io"
GEONODE_PORT      = "11000"
COUNTRY           = "in"

# ================= RUN CONFIG =================
AFFILIATE_URL     = "https://partners.marcadeo.com/click?oid=441&uid=1&lid=508"
DEFAULT_VISITS    = 1
DEFAULT_PARALLEL  = 1         # how many visits run at the same time (parallel sessions)
MAX_PARALLEL      = 8         # safety cap on concurrent browser sessions
MAX_IP_RETRIES    = 10        # rotate to a fresh IP up to this many times per visit
NAV_TIMEOUT       = 100000    # slow-network safe timeout for loads/clicks (ms)
LOG_FILE          = "sky_visits.json"
TEXT_LOG_FILE     = "sky_visits.txt"

# Well-connected Indian airports (code -> city). Each visit picks a random FROM
# and a different random TO from this pool, so the search always uses a real,
# well-served city that the autosuggest reliably resolves.
AIRPORT_CODES = {
    "BLR": "Bengaluru",
    "BOM": "Mumbai",
    "DEL": "Delhi",
    "CCU": "Kolkata",
    "MAA": "Chennai",
    "HYD": "Hyderabad",
    "AMD": "Ahmedabad",
    "PNQ": "Pune",
    "GOI": "Goa",
    "COK": "Kochi",
    "IXC": "Chandigarh",
    "IXJ": "Jammu",
    "SXV": "Srinagar",
    "GAU": "Guwahati",
    "PAT": "Patna",
    "NAG": "Nagpur",
    "BBI": "Bhubaneswar",
    "TRV": "Thiruvananthapuram",
    "VNS": "Varanasi",
    "ATQ": "Amritsar",
}
CITIES = list(AIRPORT_CODES.values())

# Rotating desktop browser fingerprints. UA is paired with a matching platform,
# client-hints, viewport and locale so the signals are internally consistent.
PROFILES = [
    {
        "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "platform": "Win32", "ch_platform": '"Windows"',
        "ch_ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        "viewport": {"width": 1920, "height": 1080}, "cores": 8, "mem": 8,
        "locale": "en-GB", "accept_language": "en-GB,en;q=0.9",
        "languages": ["en-GB", "en"],
    },
    {
        "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
        "platform": "Win32", "ch_platform": '"Windows"',
        "ch_ua": '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        "viewport": {"width": 1366, "height": 768}, "cores": 4, "mem": 8,
        "locale": "en-IN", "accept_language": "en-IN,en;q=0.9",
        "languages": ["en-IN", "en"],
    },
    {
        "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "platform": "MacIntel", "ch_platform": '"macOS"',
        "ch_ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        "viewport": {"width": 1440, "height": 900}, "cores": 8, "mem": 16,
        "locale": "en-GB", "accept_language": "en-GB,en;q=0.9",
        "languages": ["en-GB", "en"],
    },
    {
        "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        "platform": "Win32", "ch_platform": '"Windows"',
        "ch_ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        "viewport": {"width": 1536, "height": 864}, "cores": 8, "mem": 8,
        "locale": "en-IN", "accept_language": "en-IN,en;q=0.9",
        "languages": ["en-IN", "en"],
    },
    {
        "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "platform": "Win32", "ch_platform": '"Windows"',
        "ch_ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        "viewport": {"width": 1600, "height": 900}, "cores": 12, "mem": 16,
        "locale": "en-GB", "accept_language": "en-GB,en;q=0.9",
        "languages": ["en-GB", "en"],
    },
]


def log(m):
    v = _visit_ctx.get()
    prefix = f"[V{v}] " if v is not None else ""
    line = prefix + str(m)
    print(line, flush=True)
    if _LOG_SINK is not None:
        try:
            _LOG_SINK(line)
        except Exception:
            pass


# ---------------- Proxy bridge (in-process, no dependencies) ----------------
# Chromium cannot authenticate SOCKS5 (username/password) proxies. So we run a
# tiny in-process HTTP proxy on 127.0.0.1 (no auth) that tunnels every connection
# through the authenticated Geonode SOCKS5 upstream. Pure asyncio.
def _free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


async def _socks5_connect(dst_host, dst_port, user, pw):
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
    await reader.readexactly(2)
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
    local_port = _free_port()
    tasks = set()
    server = await asyncio.start_server(_make_bridge_handler(username, tasks), "127.0.0.1", local_port)
    server._bridge_tasks = tasks
    return server, local_port


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


async def get_proxy_ip(context):
    """Fetch the proxy exit IP through the browser (goes via the bridge)."""
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


# ---------------- fingerprint / stealth ----------------
def build_stealth(profile):
    """An init script that harmonises the JS-visible fingerprint with the chosen
    profile and hides the usual automation tells."""
    langs = json.dumps(profile["languages"])
    return f"""
    Object.defineProperty(navigator, 'webdriver', {{get: () => undefined}});
    Object.defineProperty(navigator, 'languages', {{get: () => {langs}}});
    Object.defineProperty(navigator, 'plugins', {{get: () => [1,2,3,4,5]}});
    Object.defineProperty(navigator, 'platform', {{get: () => {json.dumps(profile['platform'])}}});
    Object.defineProperty(navigator, 'hardwareConcurrency', {{get: () => {profile['cores']}}});
    Object.defineProperty(navigator, 'deviceMemory', {{get: () => {profile['mem']}}});
    window.chrome = window.chrome || {{ runtime: {{}} }};
    try {{
      const _q = window.navigator.permissions && window.navigator.permissions.query;
      if (_q) window.navigator.permissions.query = (p) =>
        (p && p.name === 'notifications')
          ? Promise.resolve({{ state: Notification.permission }})
          : _q(p);
    }} catch (e) {{}}
    try {{
      const gp = WebGLRenderingContext.prototype.getParameter;
      WebGLRenderingContext.prototype.getParameter = function(p) {{
        if (p === 37445) return 'Intel Inc.';
        if (p === 37446) return 'Intel Iris OpenGL Engine';
        return gp.call(this, p);
      }};
    }} catch (e) {{}}
    """


# ---------------- popups / captcha ----------------
def is_captcha(u):
    return "captcha" in u.lower() or "/px/" in u.lower()


async def close_popups(page):
    """Dismiss cookie/consent/promo popups anywhere in the page, including inside
    iframes (provider & airline sites put their consent wall in an iframe)."""
    # Distinctive phrases use substring match; short/ambiguous words use EXACT
    # match (":text-is") so "OK" never matches "Booking", "Allow" never matches
    # "Allowance", etc. One popup is closed per call to avoid mis-click floods.
    sels = [
        '#onetrust-accept-btn-handler',
        'button:has-text("Allow all")', 'button:has-text("Allow All")',
        'button:has-text("Accept all")', 'button:has-text("Accept All")',
        'button:has-text("I agree")', 'button:has-text("I accept")',
        'button:has-text("Got it")', 'button:has-text("No thanks")',
        'button:text-is("Accept")', 'button:text-is("Allow")', 'button:text-is("Agree")',
        'button:text-is("OK")', 'button:text-is("Ok")',
        'button[aria-label="Close"]', 'button[title="Close"]',
        'button[aria-label*="dismiss" i]',
        'a:has-text("Allow all")', 'a:has-text("Accept all")', 'a:has-text("I agree")',
    ]
    try:
        frames = list(page.frames)
    except Exception:
        frames = []
    for fr in frames:
        for sel in sels:
            try:
                loc = fr.locator(sel).first
                if await loc.count() > 0 and await loc.is_visible():
                    await loc.click(timeout=2500)
                    log(f"      popup closed: {sel}")
                    await page.wait_for_timeout(400)
                    return True   # one popup per call — prevents click floods
            except Exception:
                pass

    # Modal dialogs with only an X icon (e.g. Skyscanner "Read before booking").
    # These have no text/aria we can match, so dismiss via the X or Escape.
    try:
        dlg = page.locator('[role="dialog"], [aria-modal="true"]').first
        if await dlg.count() > 0 and await dlg.is_visible():
            x = dlg.locator(
                'button[aria-label*="close" i], button[title*="close" i], '
                'button:has(svg), [class*="close" i]'
            ).first
            closed = False
            if await x.count() > 0 and await x.is_visible():
                try:
                    await x.click(timeout=2500)
                    closed = True
                    log("      dialog closed via X")
                except Exception:
                    closed = False
            if not closed:
                await page.keyboard.press("Escape")
                log("      dialog dismissed via Escape")
            await page.wait_for_timeout(500)
            return True
    except Exception:
        pass
    return False


async def _find_hold_button(page):
    """Return the bounding box of a visible PRESS & HOLD button, or None."""
    for fr in page.frames:
        for sel in ['text=/press.*hold/i', '[id*="px-captcha"]', 'div[role="button"]', 'button']:
            try:
                loc = fr.locator(sel).first
                if await loc.count() > 0 and await loc.is_visible():
                    box = await loc.bounding_box()
                    if box and box["width"] > 40:
                        return box
            except Exception:
                pass
    return None


async def _do_hold(page, box):
    cx, cy = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
    await page.mouse.move(cx, cy, steps=10)
    await page.mouse.down()
    t = 0
    target = random.uniform(9, 12)
    while t < target:
        await page.wait_for_timeout(250)
        await page.mouse.move(cx + random.uniform(-2, 2), cy + random.uniform(-2, 2))
        t += 0.25
    await page.mouse.up()
    await page.wait_for_timeout(4000)


async def hold_captcha(page, tries=5):
    """Best-effort clear of a captcha wall mid-flow (does not abort the visit)."""
    if not is_captcha(page.url):
        return True
    for i in range(tries):
        box = await _find_hold_button(page)
        if box:
            await _do_hold(page, box)
            if not is_captcha(page.url):
                log(f"      captcha cleared (hold {i+1})")
                return True
        else:
            await page.wait_for_timeout(2000)
        if not is_captcha(page.url):
            return True
    return not is_captcha(page.url)


async def solve_captcha(page, appear_secs=20, max_holds=5):
    """Entry-gate captcha handling. Wait up to appear_secs for the PRESS & HOLD
    button to show; if it never appears (blank / hard bot page), give up so the
    caller can abort this IP and retry fresh. If it appears, hold until cleared.
    Returns True if we're past the wall, False if we should rotate IP."""
    if not is_captcha(page.url):
        return True
    log("      bot page -> looking for PRESS & HOLD...")
    box = None
    waited = 0
    while waited < appear_secs:
        if not is_captcha(page.url):
            return True
        box = await _find_hold_button(page)
        if box:
            break
        await page.wait_for_timeout(2000)
        waited += 2
    if not box:
        log(f"      no PRESS & HOLD within {appear_secs}s -> abort, retry fresh IP")
        return False
    for i in range(max_holds):
        box = await _find_hold_button(page) or box
        await _do_hold(page, box)
        if not is_captcha(page.url):
            log(f"      captcha cleared (hold {i+1})")
            return True
        b2 = await _find_hold_button(page)
        if b2 is None and not is_captcha(page.url):
            return True
    ok = not is_captcha(page.url)
    if not ok:
        log("      captcha not cleared after holds -> abort, retry fresh IP")
    return ok


async def clear_walls(page, rounds=2):
    """Clear captcha + popups on a page (call generously)."""
    for _ in range(rounds):
        if is_captcha(page.url):
            await hold_captcha(page)
        await close_popups(page)
        await page.wait_for_timeout(400)


# ---------------- form filling ----------------
async def fill_city(page, input_id, city):
    """Fill an autosuggest field by FOCUSING via JS and typing (works even when
    an overlay would block a normal click), then pick the matching suggestion."""
    inp = page.locator(f"#{input_id}")
    for attempt in range(4):
        await clear_walls(page, rounds=1)
        try:
            await inp.wait_for(state="visible", timeout=15000)
        except Exception:
            log(f"      {input_id}: field not visible (att{attempt+1})")
            await page.wait_for_timeout(1200)
            continue
        try:
            await inp.scroll_into_view_if_needed(timeout=10000)
        except Exception:
            pass
        # focus + clear via JS (no click needed, works behind overlays), then type
        try:
            await inp.evaluate("e => { e.focus(); e.value=''; e.dispatchEvent(new Event('input',{bubbles:true})); }")
        except Exception:
            try:
                await inp.click(timeout=12000, force=True)
            except Exception:
                pass
        await page.wait_for_timeout(300)
        await page.keyboard.type(city, delay=random.randint(110, 200))
        await page.wait_for_timeout(700)
        try:
            val = await inp.input_value()
        except Exception:
            val = ""
        if city.lower()[:4] not in (val or "").lower():
            log(f"      {input_id}: text not registered (got '{val}'), retry")
            await page.keyboard.press("Escape")
            await page.wait_for_timeout(800)
            continue
        opts = page.locator('[role="option"]')
        appeared = False
        for _ in range(30):   # up to ~15s for the autosuggest API on slow nets
            await page.wait_for_timeout(500)
            if await opts.count() > 0:
                appeared = True
                break
        if not appeared:
            log(f"      {input_id}: no suggestions (att{attempt+1}), retry")
            await page.keyboard.press("Escape")
            await page.wait_for_timeout(1000)
            continue
        await page.wait_for_timeout(500)
        # STRICT match: only accept a real city option — never the default
        # "Explore everywhere" / "Nearby" entries (they break the search).
        n = await opts.count()
        chosen = None
        chosen_txt = ""
        for i in range(n):
            t = (await opts.nth(i).text_content() or "").strip()
            tl = t.lower()
            if "explore everywhere" in tl or "nearby" in tl or "add nearby" in tl:
                continue
            if city.lower() in tl:
                chosen = opts.nth(i)
                chosen_txt = t
                break
        if chosen is None:
            log(f"      {input_id}: no matching option for '{city}' (att{attempt+1}), retry")
            await page.keyboard.press("Escape")
            await page.wait_for_timeout(900)
            continue
        await chosen.click()
        log(f"      {input_id}: picked '{chosen_txt[:40]}'")
        await page.wait_for_timeout(900)
        return True
    return False


async def set_one_way(page):
    try:
        btn = page.locator('button:has-text("Return")').first
        if await btn.count() > 0:
            await btn.click(timeout=15000)
            await page.wait_for_timeout(800)
            for sel in ['text="One way"', 'text=/one\\s*way/i', '[role="option"]:has-text("One way")']:
                o = page.locator(sel).first
                if await o.count() > 0 and await o.is_visible():
                    await o.click(timeout=8000)
                    await page.wait_for_timeout(800)
                    return True
    except Exception as e:
        log("      one-way err " + str(e)[:50])
    return False


async def pick_depart_date(page):
    """Open the depart calendar and click a RANDOM future day, then Apply.
    Returns the chosen date string (for logging) or None."""
    await page.locator('[data-testid="depart-btn"]').click(timeout=NAV_TIMEOUT)
    await page.wait_for_timeout(1500)
    handles = await page.evaluate_handle("""() => {
        const res=[];
        document.querySelectorAll('[data-testid="dates-container"] button').forEach(b=>{
            const t=(b.textContent||'').trim();
            if(!/^\\d{1,2}$/.test(t)) return;
            if(b.getAttribute('aria-hidden')==='true') return;
            const cls=b.className||'';
            if(cls.includes('NonMonthDate')||cls.includes('BeforeToday')) return;
            if(b.disabled) return;
            res.push(b);
        });
        return res;
    }""")
    props = await handles.get_properties()
    btns = [v.as_element() for v in props.values() if v.as_element()]
    if not btns:
        return None
    # random future day (skip the first couple so it's not always "today")
    lo = min(2, len(btns) - 1)
    idx = random.randint(lo, len(btns) - 1)
    daytxt = (await btns[idx].text_content() or "").strip()
    await btns[idx].click()
    await page.wait_for_timeout(700)
    for sel in ['button:has-text("Apply")', '[data-testid*="apply" i]', 'button:has-text("Done")']:
        a = page.locator(sel).first
        try:
            if await a.count() > 0 and await a.is_visible():
                await a.click(timeout=8000)
                break
        except Exception:
            pass
    await page.wait_for_timeout(1200)
    try:
        dep = (await page.locator('[data-testid="depart-btn"]').inner_text()).replace("\n", " ").strip()
        return dep[:40]
    except Exception:
        return f"day {daytxt}"


# ---------------- engagement helpers ----------------
async def scroll_page(page, rounds=6):
    for _ in range(rounds):
        if is_captcha(page.url):
            await hold_captcha(page)
        await page.mouse.wheel(0, random.randint(600, 1200))
        await page.wait_for_timeout(random.randint(700, 1400))
    await page.mouse.wheel(0, -random.randint(400, 800))
    await page.wait_for_timeout(700)


async def _wait_navigation(fpage, ctx, pages_before, url_before, secs=45):
    """Wait for a real next page after a click: a NEW TAB, or a same-tab URL
    change. Returns that page or None."""
    for _ in range(secs):
        await fpage.wait_for_timeout(1000)
        new_pages = [p for p in ctx.pages if p not in pages_before]
        if new_pages:
            return new_pages[-1]
        if fpage.url != url_before:
            return fpage
    return None


async def _load_page(pg, ctx):
    try:
        await pg.bring_to_front()
        await pg.wait_for_load_state("domcontentloaded", timeout=NAV_TIMEOUT)
    except Exception:
        pass
    try:
        await pg.wait_for_load_state("load", timeout=NAV_TIMEOUT)
    except Exception:
        pass
    await pg.wait_for_timeout(3500)
    await clear_walls(pg, rounds=2)


async def open_offer_page(fpage):
    """Pick a random flight card (Select or View details) and open its offer
    page. Returns the offer page or None."""
    ctx = fpage.context
    await fpage.wait_for_timeout(3500)
    await clear_walls(fpage, rounds=2)
    for _ in range(5):
        if is_captcha(fpage.url):
            await hold_captcha(fpage)
        await fpage.mouse.wheel(0, 1400)
        await fpage.wait_for_timeout(1500)
    await fpage.evaluate("window.scrollTo(0, 0)")
    await fpage.wait_for_timeout(1200)
    await clear_walls(fpage, rounds=1)

    # Poll for card CTAs — flight results stream in, so the Select / View
    # details buttons can take a while to render on slow networks.
    sel = vd = None
    sc = vc = 0
    for _ in range(20):   # up to ~40s
        sel = fpage.get_by_role("link", name="Select")
        if await sel.count() == 0:
            sel = fpage.get_by_role("button", name="Select")
        vd = fpage.get_by_role("link", name="View details")
        if await vd.count() == 0:
            vd = fpage.get_by_role("button", name="View details")
        sc = await sel.count()
        vc = await vd.count()
        if sc > 0 or vc > 0:
            break
        if is_captcha(fpage.url):
            await hold_captcha(fpage)
        await clear_walls(fpage, rounds=1)
        await fpage.mouse.wheel(0, 800)
        await fpage.wait_for_timeout(2000)
    log(f"      card CTAs -> Select={sc}  View details={vc}")

    pool = [("select", i) for i in range(min(sc, 15))] + [("view", i) for i in range(min(vc, 15))]
    if not pool:
        sel = fpage.locator('a:has-text("Select"), button:has-text("Select")')
        sc = await sel.count()
        pool = [("select", i) for i in range(min(sc, 15))]
    if not pool:
        return None
    random.shuffle(pool)

    for kind, idx in pool[:8]:
        loc = sel if kind == "select" else vd
        el = loc.nth(idx)
        pages_before = set(ctx.pages)
        url_before = fpage.url
        try:
            await el.scroll_into_view_if_needed(timeout=NAV_TIMEOUT)
            await fpage.wait_for_timeout(800)
            await el.click(timeout=NAV_TIMEOUT)
            log(f"      clicked '{kind}' card #{idx}")
        except Exception as e:
            log(f"      {kind} #{idx} click failed ({str(e)[:45]}), trying another")
            await clear_walls(fpage, rounds=1)
            continue
        offer = await _wait_navigation(fpage, ctx, pages_before, url_before, secs=45)
        if offer is not None:
            log("      offer page opened" + (" (new tab)" if offer is not fpage else " (same tab)"))
            await _load_page(offer, ctx)
            return offer
        log(f"      {kind} #{idx}: no navigation, trying another")
        await clear_walls(fpage, rounds=1)
    return None


async def click_go_to_site(offer, ctx):
    """Click a random 'Go to site' on the offer page -> provider site (new tab)."""
    await offer.wait_for_timeout(2000)
    await clear_walls(offer, rounds=2)
    gts = None
    cnt = 0
    for _ in range(20):   # poll ~40s; provider list can load lazily / be covered
        await clear_walls(offer, rounds=1)
        for finder in (
            offer.get_by_role("link", name="Go to site"),
            offer.get_by_role("button", name="Go to site"),
            offer.locator('a:has-text("Go to site"), button:has-text("Go to site")'),
        ):
            try:
                c = await finder.count()
            except Exception:
                c = 0
            if c > 0:
                gts = finder
                cnt = c
                break
        if gts is not None:
            break
        await offer.mouse.wheel(0, 900)
        await offer.wait_for_timeout(2000)
    log(f"      Go to site buttons: {cnt}")
    if gts is None:
        return None
    await offer.evaluate("window.scrollTo(0, 0)")
    await offer.wait_for_timeout(800)

    order = list(range(min(cnt, 12)))
    random.shuffle(order)
    for idx in order[:6]:
        el = gts.nth(idx)
        pages_before = set(ctx.pages)
        url_before = offer.url
        try:
            await el.scroll_into_view_if_needed(timeout=NAV_TIMEOUT)
            await offer.wait_for_timeout(700)
            await el.click(timeout=NAV_TIMEOUT)
            log(f"      clicked 'Go to site' #{idx}")
        except Exception as e:
            log(f"      Go to site #{idx} failed ({str(e)[:45]}), trying another")
            await clear_walls(offer, rounds=1)
            continue
        site = await _wait_navigation(offer, ctx, pages_before, url_before, secs=60)
        if site is not None:
            log("      provider site opened" + (" (new tab)" if site is not offer else " (same tab)"))
            return site
        log(f"      Go to site #{idx}: nothing opened, trying another")
        await clear_walls(offer, rounds=1)
    return None


async def _random_click(page):
    """Click one random visible element on the page (scrolls it into view first)."""
    try:
        handle = await page.evaluate_handle("""() => {
            const els=[...document.querySelectorAll('a[href], button, [role="button"], [class*="card" i], [class*="result" i], [class*="offer" i], [class*="btn" i], img')].filter(e=>{
                const r=e.getBoundingClientRect();
                const t=(e.textContent||'').toLowerCase();
                if(r.width<45||r.height<22) return false;
                const st=getComputedStyle(e);
                if(st.visibility==='hidden'||st.display==='none'||parseFloat(st.opacity||'1')<0.1) return false;
                if(/logout|sign out|log out|delete|remove account/.test(t)) return false;
                return true;
            });
            if(!els.length) return null;
            return els[Math.floor(Math.random()*els.length)];
        }""")
        el = handle.as_element()
        if not el:
            return False
        try:
            await el.scroll_into_view_if_needed(timeout=8000)
        except Exception:
            pass
        await page.wait_for_timeout(500)
        try:
            await el.click(timeout=8000)
        except Exception:
            await el.click(timeout=8000, force=True)
        return True
    except Exception:
        return False


async def engage_site(site, ctx):
    """On the provider/airline site: clear walls, scroll, do a few random clicks."""
    await _load_page(site, ctx)
    log(f"      provider site: {site.url[:90]}")
    for _ in range(3):
        await close_popups(site)
        await site.wait_for_timeout(1200)
    await scroll_page(site, rounds=5)
    n = random.randint(3, 5)
    clicks = 0
    for i in range(n):
        await close_popups(site)
        ok = await _random_click(site)
        if not ok:
            await close_popups(site)
            ok = await _random_click(site)
        clicks += 1 if ok else 0
        log(f"      provider random click {i+1}/{n}: {'ok' if ok else 'skip'}")
        await site.wait_for_timeout(random.randint(1500, 2800))
        await close_popups(site)
        try:
            await site.bring_to_front()
        except Exception:
            pass
    await scroll_page(site, rounds=3)
    return clicks


# ---------------- visit logging ----------------
def new_visit_log(n):
    return {
        "visit": n, "started": datetime.now().isoformat(timespec="seconds"),
        "ip": None, "ua": None, "viewport": None, "locale": None,
        "route": None, "date": None, "attempts": 0,
        "steps": [], "status": "pending", "error": None,
        "finished": None,
    }


def step(vlog, name, ok, detail=""):
    vlog["steps"].append({"step": name, "ok": bool(ok), "detail": str(detail)[:120]})
    log(f"   [{'OK' if ok else '--'}] {name}" + (f" : {detail}" if detail else ""))


def save_visit(vlog):
    # JSON array
    logs = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except Exception:
            logs = []
    logs.append(vlog)
    try:
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
    except Exception:
        pass
    # human-readable one-liner with a compact step summary
    done = ",".join(s["step"] for s in vlog["steps"] if s["ok"])
    line = (
        f"[{vlog['finished'] or datetime.now().isoformat(timespec='seconds')}] "
        f"Visit #{vlog['visit']:<4} | {vlog['status'].upper():<7} "
        f"| IP {str(vlog['ip']):<15} | {str(vlog['route']):<22} | {str(vlog['date']):<22} "
        f"| tries:{vlog['attempts']} | UA:{(vlog['ua'] or '')[:35]} "
        f"| ok_steps: {done}"
    )
    if vlog.get("error"):
        line += f" | ERROR: {vlog['error']}"
    try:
        with open(TEXT_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


# ---------------- one attempt (one IP) ----------------
async def run_one_attempt(profile, frm, to, vlog):
    """Run the whole flow once on a fresh IP. Records steps into vlog. Returns
    True only if it reached results and engaged the offer flow."""
    username = GEONODE_USER_BASE.format(COUNTRY)
    server, port = await start_proxy_bridge(username)
    browser = None
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                channel="chrome", headless=False,
                proxy={"server": f"http://127.0.0.1:{port}"},
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox",
                      "--disable-dev-shm-usage"],
            )
            ctx = await browser.new_context(
                user_agent=profile["ua"],
                viewport=profile["viewport"],
                locale=profile["locale"],
                timezone_id="Asia/Kolkata",
                ignore_https_errors=True,
                extra_http_headers={
                    "accept-language": profile["accept_language"],
                    "sec-ch-ua": profile["ch_ua"],
                    "sec-ch-ua-mobile": "9999999999",
                    "sec-ch-ua-platform": profile["ch_platform"],
                },
            )
            ctx.set_default_timeout(NAV_TIMEOUT)
            ctx.set_default_navigation_timeout(NAV_TIMEOUT)
            await ctx.add_init_script(build_stealth(profile))
            page = await ctx.new_page()

            ip = await get_proxy_ip(ctx)
            vlog["ip"] = ip
            step(vlog, "ip", True, ip)

            # open affiliate link (with retry)
            opened = False
            for a in range(3):
                try:
                    await page.goto(AFFILIATE_URL, timeout=NAV_TIMEOUT, wait_until="domcontentloaded")
                    opened = True
                    break
                except Exception as e:
                    log(f"      goto {a+1} fail: {str(e)[:50]}")
                    await page.wait_for_timeout(2500)
            if not opened:
                step(vlog, "open", False, "could not load affiliate url")
                return False
            step(vlog, "open", True)

            # wait for the search form to be ready. Handle the bot page here: if
            # no PRESS & HOLD shows within ~20s, abort this IP and retry fresh.
            ready = False
            for _ in range(30):
                if is_captcha(page.url):
                    if not await solve_captcha(page, appear_secs=20):
                        step(vlog, "captcha", False, "no/unsolved PRESS & HOLD")
                        return False
                    continue
                await close_popups(page)
                try:
                    oi = page.locator("#originInput-input").first
                    if await oi.count() > 0 and await oi.is_visible():
                        ready = True
                        break
                except Exception:
                    pass
                await page.wait_for_timeout(2000)
            if not ready:
                step(vlog, "form_ready", False, page.url[:70])
                return False
            step(vlog, "form_ready", True, page.url[:60])

            await set_one_way(page)
            step(vlog, "one_way", True)

            if not await fill_city(page, "originInput-input", frm):
                step(vlog, "origin", False, frm)
                return False
            step(vlog, "origin", True, frm)

            if not await fill_city(page, "destinationInput-input", to):
                step(vlog, "destination", False, to)
                return False
            step(vlog, "destination", True, to)

            try:
                d = await pick_depart_date(page)
                vlog["date"] = d
                step(vlog, "date", bool(d), d or "")
            except Exception as e:
                step(vlog, "date", False, str(e)[:50])

            await clear_walls(page, rounds=1)
            # uncheck "Add a place to stay" so we get FLIGHT results
            try:
                cb = page.locator('input[name="parallel-search-option"]')
                if await cb.count() > 0 and await cb.is_checked():
                    lbl = page.locator('label:has(input[name="parallel-search-option"])').first
                    if await lbl.count() > 0:
                        await lbl.click(force=True)
                    else:
                        await cb.click(force=True)
                    await page.wait_for_timeout(500)
            except Exception:
                pass

            # search
            try:
                await page.locator('[data-testid="desktop-cta"]').click(timeout=NAV_TIMEOUT)
                step(vlog, "search", True)
            except Exception as e:
                step(vlog, "search", False, str(e)[:50])
                return False

            # wait for flight results in any tab
            reached = False
            for _ in range(30):
                await page.wait_for_timeout(1500)
                for pg in ctx.pages:
                    if is_captcha(pg.url):
                        await hold_captcha(pg)
                if any("/transport/flights/" in u for u in [pg.url for pg in ctx.pages]):
                    reached = True
                    break
            if not reached:
                step(vlog, "results", False)
                return False
            step(vlog, "results", True)

            fpage = None
            for pg in ctx.pages:
                if "/transport/flights/" in pg.url:
                    fpage = pg
                    break
            if fpage is None:
                step(vlog, "results_tab", False)
                return False
            await fpage.bring_to_front()
            await fpage.wait_for_timeout(5000)
            await clear_walls(fpage, rounds=1)

            offer = await open_offer_page(fpage)
            if offer is None:
                step(vlog, "offer_page", False)
                return False
            step(vlog, "offer_page", True, offer.url[:60])

            site = await click_go_to_site(offer, ctx)
            if site is None:
                # still engage the offer page so the visit is meaningful
                await scroll_page(offer, rounds=5)
                step(vlog, "go_to_site", False, "no provider site; engaged offer page")
                return True
            step(vlog, "go_to_site", True, site.url[:60])

            clicks = await engage_site(site, ctx)
            step(vlog, "engage_site", True, f"{clicks} random clicks + scroll")
            return True
    except Exception as e:
        vlog["error"] = str(e)[:200]
        step(vlog, "exception", False, str(e)[:80])
        return False
    finally:
        try:
            if browser is not None:
                await browser.close()
        except Exception:
            pass
        await stop_proxy_bridge(server)


# ---------------- one visit (rotates IP until complete) ----------------
async def run_visit(visit_no):
    _visit_ctx.set(visit_no)   # tag this task's log lines with the visit number
    vlog = new_visit_log(visit_no)
    profile = random.choice(PROFILES)
    frm = random.choice(CITIES)
    to = random.choice([c for c in CITIES if c != frm])
    vlog["ua"] = profile["ua"]
    vlog["viewport"] = f"{profile['viewport']['width']}x{profile['viewport']['height']}"
    vlog["locale"] = profile["locale"]
    vlog["route"] = f"{frm} -> {to}"

    log(f"\n================ VISIT #{visit_no} ================")
    log(f"   route {frm} -> {to} | {vlog['viewport']} | {profile['locale']} | UA {profile['ua'][:40]}")

    ok = False
    for attempt in range(1, MAX_IP_RETRIES + 1):
        vlog["attempts"] = attempt
        log(f"\n   --- attempt {attempt}/{MAX_IP_RETRIES} (fresh IP) ---")
        try:
            ok = await run_one_attempt(profile, frm, to, vlog)
        except Exception as e:
            vlog["error"] = str(e)[:200]
            log(f"   attempt crashed: {str(e)[:80]}")
            ok = False
        if ok:
            break
        # trim per-attempt failed steps history? keep only the last attempt's trail
        vlog["steps"] = []   # reset so the log reflects the final (successful/last) attempt
        log("   attempt did not complete, rotating IP...")
        await asyncio.sleep(2)

    vlog["status"] = "success" if ok else "failed"
    vlog["finished"] = datetime.now().isoformat(timespec="seconds")
    if not ok and not vlog.get("error"):
        vlog["error"] = f"could not complete after {MAX_IP_RETRIES} IPs"
    save_visit(vlog)
    log(f"\n   >>> VISIT #{visit_no}: {vlog['status'].upper()} "
        f"(IP {vlog['ip']}, {vlog['attempts']} tries)")
    return ok


async def run_all(total, parallel=DEFAULT_PARALLEL, stop_event=None, on_progress=None):
    """Run `total` visits, up to `parallel` of them at the same time. Each visit
    is fully independent (own proxy IP, own browser window, own fingerprint), so
    running several in parallel finishes the batch in much less wall-clock time.
    stop_event (optional): when set, workers stop picking up new visits.
    on_progress (optional): called (done, total, ok) after each visit.
    """
    install_quiet_loop()
    parallel = max(1, min(parallel, MAX_PARALLEL))
    log(f"================ START: {total} visits, {parallel} in parallel ================")

    counter = {"next": 1, "ok": 0, "done": 0}

    async def worker(wid):
        while True:
            if stop_event is not None and stop_event.is_set():
                return
            n = counter["next"]
            if n > total:
                return
            counter["next"] += 1
            try:
                ok = await run_visit(n)
            except Exception as e:
                log(f"\n   >>> VISIT #{n}: CRASHED ({str(e)[:80]})")
                ok = False
            counter["done"] += 1
            if ok:
                counter["ok"] += 1
            if on_progress is not None:
                try:
                    on_progress(counter["done"], total, counter["ok"])
                except Exception:
                    pass
            log(f"   [progress] {counter['done']}/{total} done, {counter['ok']} ok")

    workers = [asyncio.create_task(worker(w)) for w in range(parallel)]
    await asyncio.gather(*workers)

    log(f"\n================ DONE: {counter['ok']}/{total} visits succeeded ================")
    log(f"   logs -> {LOG_FILE} , {TEXT_LOG_FILE}")


# ================= GUI =================
class SkyscannerGUI:
    def __init__(self, root):
        self.root = root
        root.title("Skyscanner Traffic Bot")
        root.geometry("800x620")

        self.log_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.worker = None

        pad = {"padx": 8, "pady": 4}
        frm = ttk.Frame(root)
        frm.pack(fill="x", padx=10, pady=8)

        # Affiliate URL (default, editable)
        ttk.Label(frm, text="Affiliate URL:").grid(row=0, column=0, sticky="w", **pad)
        self.url_var = tk.StringVar(value=AFFILIATE_URL)
        ttk.Entry(frm, textvariable=self.url_var, width=72).grid(
            row=0, column=1, columnspan=3, sticky="we", **pad)

        # Total visits
        ttk.Label(frm, text="Total Visits:").grid(row=1, column=0, sticky="w", **pad)
        self.visits_var = tk.StringVar(value="10")
        ttk.Entry(frm, textvariable=self.visits_var, width=12).grid(row=1, column=1, sticky="w", **pad)

        # Parallel sessions
        ttk.Label(frm, text="Parallel Sessions:").grid(row=2, column=0, sticky="w", **pad)
        self.par_var = tk.StringVar(value="1")
        ttk.Entry(frm, textvariable=self.par_var, width=12).grid(row=2, column=1, sticky="w", **pad)
        ttk.Label(frm, text=f"(1 - {MAX_PARALLEL}: how many run at the same time)").grid(
            row=2, column=2, columnspan=2, sticky="w", **pad)

        # Geo (fixed)
        ttk.Label(frm, text="Geo:").grid(row=3, column=0, sticky="w", **pad)
        ttk.Label(frm, text="India (fixed) — residential IPs").grid(row=3, column=1, columnspan=2, sticky="w", **pad)

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

    def gui_log(self, line):
        self.log_queue.put(line)

    def drain_log(self):
        while not self.log_queue.empty():
            msg = self.log_queue.get_nowait()
            self.log_box.configure(state="normal")
            self.log_box.insert("end", msg + "\n")
            self.log_box.see("end")
            self.log_box.configure(state="disabled")
        self.root.after(100, self.drain_log)

    def set_progress(self, done, total, ok):
        def _update():
            self.progress["maximum"] = total
            self.progress["value"] = done
            self.progress_var.set(f"Progress: {done}/{total}  |  Success: {ok}")
        self.root.after(0, _update)

    def start(self):
        global AFFILIATE_URL, _LOG_SINK
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Affiliate URL cannot be empty")
            return
        try:
            total = int(self.visits_var.get().strip())
            if total <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Total Visits must be a positive number")
            return
        try:
            par = int(self.par_var.get().strip())
            if not (1 <= par <= MAX_PARALLEL):
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", f"Parallel Sessions must be between 1 and {MAX_PARALLEL}")
            return

        AFFILIATE_URL = url            # use the URL from the box
        _LOG_SINK = self.gui_log       # route all log() lines into the GUI

        self.stop_event.clear()
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.gui_log(f"=== Starting: {total} visits | {par} parallel sessions | Geo: India ===")

        self.worker = threading.Thread(target=self._run_thread, args=(total, par), daemon=True)
        self.worker.start()

    def _run_thread(self, total, par):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(
                run_all(total, par, self.stop_event, self.set_progress)
            )
        except Exception as e:
            self.gui_log(f"❌ Fatal: {str(e)[:250]}")
        finally:
            loop.close()
            self.root.after(0, self._on_done)

    def _on_done(self):
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.progress_var.set(self.progress_var.get() + "  |  DONE")

    def stop(self):
        self.stop_event.set()
        self.gui_log("⏹️  Stop requested... finishing the visits already running.")
        self.stop_btn.configure(state="disabled")


def launch_gui():
    root = tk.Tk()
    SkyscannerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    # No args -> open the GUI. Numeric args -> CLI:
    #   python skyscanner_final.py            (GUI)
    #   python skyscanner_final.py 10 2       (CLI: 10 visits, 2 parallel)
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        n = int(sys.argv[1])
        par = DEFAULT_PARALLEL
        if len(sys.argv) > 2 and sys.argv[2].isdigit():
            par = int(sys.argv[2])
        asyncio.run(run_all(n, par))
    else:
        launch_gui()
