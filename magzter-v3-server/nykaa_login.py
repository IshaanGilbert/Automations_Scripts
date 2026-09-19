
import os
import sys
import time
import socket
import subprocess
import asyncio
from urllib.parse import urlparse
from playwright.async_api import async_playwright

# ================= CONFIG =================
MOBILE = "9999999999"
NAME = "Pradeep test"
EMAIL = "test@example.com"

# Address details (account setup)
POSTAL_CODE = "208014"
ADDRESS_LINE = "yogendra vihar"

NYKAA_URL = "https://www.nykaa.com/"
PROFILE_URL = "https://www.nykaa.com/myProfile"
# Per-instance, not a constant: one box runs many slots, and a fixed 9222 means the
# second slot finds the port already open, decides Chrome is "already running", and
# quietly drives the FIRST slot's browser. Every slot needs its own port and its own
# profile dir. node_agent/systemd sets NYKAA_INSTANCE per slot.
INSTANCE = int(os.environ.get("NYKAA_INSTANCE", "0") or 0)
DEBUG_PORT = int(os.environ.get("NYKAA_DEBUG_PORT", 0) or (9222 + INSTANCE))

# HEADLESS mode — default OFF (real visible Chrome). True karne par Chrome background me
# (headless=new) chalta hai. Nykaa OTP headless me aata hai ya nahi ye test karne ke liye.
HEADLESS = str(os.environ.get("NYKAA_HEADLESS", "")).strip().lower() in ("1", "true", "yes", "on")


IS_WINDOWS = os.name == "nt"

# ---------------- Timeouts: ONE place, deliberately generous ----------------
# Every Playwright wait in this bot used to carry its own hardcoded number (15s, 20s,
# 30s, 90s). Behind a residential proxy those are short enough that a slow-but-working
# IP failed the account outright — the account was fine, only the clock ran out. A slow
# page should cost seconds of waiting, never a spent queue row.
#
# These are the DEFAULT for every action and navigation (set on the context in
# launch_browser), so a call site that passes nothing gets the generous value.
# Override per-server via the agent env if a box needs different numbers.
PW_TIMEOUT  = int(os.environ.get("NYKAA_PW_TIMEOUT",  120_000))   # clicks, selectors
NAV_TIMEOUT = int(os.environ.get("NYKAA_NAV_TIMEOUT", 240_000))   # page loads

# Mobile OTP submit hone ke BAAD wala intezaar. Us bindu par number ka paisa lag chuka
# hai aur account ban chuka hai, to jaldi haar maanne ka koi faayda nahi — rukna sasta
# hai, haarna mehnga. Isliye ye baaki sab se kaafi bada hai.
POST_OTP_TIMEOUT = int(os.environ.get("NYKAA_POST_OTP_TIMEOUT", 600_000))   # 10 min


def _find_chrome():
    """Kisi bhi system pe Chrome dhoondo (common locations).

    Server pe Linux paths bhi dekhne padte hain — pehle sirf C:\\... candidates the, to
    Linux pe koi na milne par ye Windows path hi return kar deta tha aur Popen
    FileNotFoundError deta tha. CHROME_PATH env var sab pe bhaari hai.
    """
    override = os.environ.get("CHROME_PATH", "").strip()
    if override:
        return override

    env = os.environ
    if IS_WINDOWS:
        cands = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.join(env.get("LOCALAPPDATA", ""), r"Google\Chrome\Application\chrome.exe"),
            # Edge (Chromium) fallback — CDP same tarah kaam karta hai
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        ]
    else:
        cands = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser",
            "/snap/bin/chromium",
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",   # macOS
        ]
    for c in cands:
        if c and os.path.exists(c):
            return c

    # Nothing system-wide — but this fleet installs Playwright's own Chromium
    # (`playwright install chromium`, see DEPLOY_V3.md 1.5/2.2), and that binary drives
    # CDP exactly the same. Bots run under sudo, so the cache is usually root's.
    import glob
    pw_roots = [os.environ.get("PLAYWRIGHT_BROWSERS_PATH", ""),
                "/root/.cache/ms-playwright",
                os.path.expanduser("~/.cache/ms-playwright"),
                os.path.expanduser("~/Library/Caches/ms-playwright")]
    pats = ["chromium-*/chrome-linux64/chrome",      # newer builds
            "chromium-*/chrome-linux/chrome",        # older builds
            "chromium-*/chrome-mac*/Chromium.app/Contents/MacOS/Chromium"]
    found = []
    for root in filter(None, pw_roots):
        for pat in pats:
            found += glob.glob(os.path.join(root, pat))
    if found:
        # highest build number wins — `playwright install` leaves old ones behind
        found.sort()
        return found[-1]

    return cands[0]   # default (agar na mile to error saaf aayega)


# ROOT = jis folder me exe/script hai (frozen .exe -> exe ka folder).
if getattr(sys, "frozen", False):
    _BASE = os.path.dirname(sys.executable)
else:
    _BASE = os.path.dirname(os.path.abspath(__file__))

CHROME_PATH = _find_chrome()
# Per-instance too: Chrome refuses to open the same user-data-dir twice, so slots
# sharing one profile dir would fight over it (and over each other's cookies/session).
PROFILE_DIR = os.path.join(_BASE, f"nykaa_chrome_profile_{INSTANCE}"
                                  if INSTANCE else "nykaa_chrome_profile")

# ================= SELECTORS =================
SIGN_IN_BTN = 'button[aria-label="Sign in"]'
MOBILE_INPUT = '9999999999"Mobile Number"]'
SEND_OTP_BTN = 'button:has-text("Send OTP")'
OTP_DIGIT = lambda i: f'input[aria-label="Digit {i} of 6"]'

# Naya account form (Name input ke kai selectors try karenge)
NAME_INPUTS = [
    'input[label="Enter Name"]',
    'input[placeholder="Test Holder"]',
    'input[aria-label="Enter Name"]',
]
EMAIL_INPUTS = [
    'input[aria-label="Email Id"]',
    'input[label="Email Id"]',
    'input[placeholder="Test Holder"]',
]
# Name/Email bharne ke baad submit karne wala button
YES_PROCEED_BTN = 'button:has-text("Yes, Proceed")'

# ---- Profile / Address setup ----
PROFILE_ICON_BTN = 'button[aria-label="Profile"]'
PROFILE_LINK = 'a[href="/myProfile"]'
ADD_ADDRESS_BTN = 'text="ADD NEW ADDRESS"'
ADDR_NAME_INPUT = 'input[aria-label="Name"]'
ADDR_MOBILE_INPUT = '9999999999"Mobile Number"]'
ADDR_POSTAL_INPUT = 'input[aria-label="Postal Code"]'
ADDR_TEXTAREA = 'textarea[placeholder="Test Holder"]'
ADD_ADDRESS_SUBMIT = 'button:has-text("Add Address")'


async def ask_terminal(prompt):
    return await asyncio.get_event_loop().run_in_executor(None, input, prompt)


async def get_otp(label):
    """Terminal se 6-digit OTP lo."""
    print("\n" + "=" * 55)
    print(f"🔐 {label}")
    while True:
        otp = (await ask_terminal("👉 6-digit OTP enter karo: ")).strip()
        if otp.isdigit() and len(otp) == 6:
            print("=" * 55)
            return otp
        print("⚠️ Sirf 6 digit ka number daalo.")


async def fill_otp(page, otp):
    """6 alag boxes me OTP daalo."""
    print("⌨️  OTP fill kar rahe hain...")
    for i, digit in enumerate(otp, start=1):
        box = page.locator(OTP_DIGIT(i))
        await box.click()
        await box.type(digit, delay=100)
        await page.wait_for_timeout(200)
    await page.wait_for_timeout(1500)
    try:
        await page.keyboard.press("Enter")
    except Exception:
        pass


async def find_present(page, selectors):
    """List me se jo pehla selector page pe mile, wo return karo."""
    for sel in selectors:
        if await page.query_selector(sel):
            return sel
    return None


async def click_if_present(page, selector, label="", timeout_sec=8):
    """Agar element aa jaye to click karo (poll)."""
    for _ in range(timeout_sec):
        el = await page.query_selector(selector)
        if el:
            try:
                await el.click()
                if label:
                    print(f"   ✅ Clicked: {label}")
                return True
            except Exception:
                pass
        await page.wait_for_timeout(1000)
    return False


async def robust_click(page, selector, text=None, label="", timeout=None):
    """
    Ek element ko strategies se click karo (SAHI element pe, overlay ignore karke):
      1. Normal Playwright click (overlay ho to ye fail hoga, galat click nahi karega)
      2. JS DOM click -> EXACT text wale element ko dhoondh ke seedha .click()
                         (chat widget "how may we help" jaise overlay ko skip karta hai)
      3. Force click (last resort)
    """
    label = label or (text or selector)
    loc = page.locator(selector).first
    try:
        await loc.wait_for(state="visible", timeout=timeout)
    except Exception:
        pass

    # 1. Normal click (intercept-safe: overlay ho to galat jagah click nahi karega)
    try:
        await loc.scroll_into_view_if_needed(timeout=4000)
        await loc.click(timeout=5000)
        print(f"   ✅ {label} clicked (normal)")
        return True
    except Exception:
        pass

    # 2. JS DOM click -> exact text match, chat/overlay ko skip
    if text:
        ok = await page.evaluate(
            """(t) => {
                const norm = s => (s || '').replace(/\\s+/g, ' ').trim();
                const bad = ['how may we help', 'chat', 'need help'];
                const isBad = s => bad.some(b => s.toLowerCase().includes(b));
                const cand = [...document.querySelectorAll('button, [role=button], a, div, span')]
                    .filter(x => !isBad(norm(x.textContent)));
                let el = cand.find(x => norm(x.textContent) === t)
                      || cand.find(x => norm(x.textContent).startsWith(t))
                      || cand.find(x => norm(x.textContent).includes(t));
                if (el) {
                    el.scrollIntoView({block: 'center'});
                    el.click();
                    return true;
                }
                return false;
            }""",
            text,
        )
        if ok:
            print(f"   ✅ {label} clicked (JS DOM - exact)")
            return True

    # 3. Force click (last resort)
    try:
        await loc.click(force=True, timeout=5000)
        print(f"   ✅ {label} clicked (force)")
        return True
    except Exception:
        pass

    print(f"   ❌ {label} click FAIL (saari strategies)")
    return False


async def wait_for_signup_form(page, timeout_sec=20):
    """Mobile OTP ke baad signup form (Name/Email) aane ka poll karo."""
    print("⏳ Checking: naya account form aaya ya login ho gaya...")
    for _ in range(timeout_sec):
        sel = await find_present(page, NAME_INPUTS + EMAIL_INPUTS)
        if sel:
            return True
        await page.wait_for_timeout(1000)
    return False


def _port_open(port):
    s = socket.socket()
    s.settimeout(0.5)
    try:
        s.connect(("127.0.0.1", port))
        return True
    except Exception:
        return False
    finally:
        s.close()


def launch_real_chrome():
    if _port_open(DEBUG_PORT):
        print(f"🟢 Chrome pehle se port {DEBUG_PORT} pe chal raha hai")
        return None
    os.makedirs(PROFILE_DIR, exist_ok=True)
    args = [
        CHROME_PATH,
        f"--remote-debugging-port={DEBUG_PORT}",
        f"--user-data-dir={PROFILE_DIR}",
        "--no-first-run",
        "--no-default-browser-check",
    ]
    if not IS_WINDOWS:
        # Chrome refuses to start as root without this, and on a server the bots run
        # as root. /dev/shm is tiny in most VMs/containers, which crashes tabs.
        #
        # --disable-gpu belongs here, NOT only in the headless branch: a headed Chrome
        # on Xvfb still tries to bring up GPU acceleration, fails
        # ("Failed to send GpuControl.CreateCommandBuffer"), and takes the X connection
        # down with it — the browser dies mid-signin and the account is lost.
        # NOT --disable-software-rasterizer: together with --disable-gpu it leaves
        # Chromium no way to draw at all and the process exits at startup. See the
        # longer note in launch_browser().
        args += ["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage",
                 "--disable-gpu",
                 "--memory-pressure-off", "--disable-background-timer-throttling"]
    if HEADLESS:
        # headless=new + anti-detection (Nykaa ko normal browser lage taaki OTP jaaye)
        #  --disable-http2  : Nykaa CDN headless pe HTTP2 connection reset kar deta
        #                     (ERR_HTTP2_PROTOCOL_ERROR) -> HTTP/1.1 force
        #  --user-agent     : "HeadlessChrome" token hata ke normal Chrome UA
        args += [
            "--headless=new",
            "--window-size=1920,1080",
            "--disable-gpu",
            "--disable-blink-features=AutomationControlled",
            "--disable-dev-shm-usage",
            "--disable-http2",
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        ]
    else:
        # Explicit window size that FITS the slot's Xvfb, exactly like buyer.py and
        # read.py do. Not --start-maximized: read.py:391 warns it stacks windows so only
        # one shows, and with no window manager it means nothing anyway. A window bigger
        # than the screen (the earlier 1920x1080 on a 1440x900 Xvfb) hangs off the edge —
        # over VNC only its titlebar is reachable, so every click lands on minimise.
        args += [f"--window-size={WIN_W},{WIN_H}", "--window-position=0,0",
                 "--disable-infobars"]
    args.append(NYKAA_URL)
    print(f"🚀 {'Headless' if HEADLESS else 'Real'} Chrome launch kar rahe hain...")
    proc = subprocess.Popen(args)
    for _ in range(40):
        if _port_open(DEBUG_PORT):
            print("✅ Chrome debugging port ready")
            time.sleep(2)
            return proc
        time.sleep(0.5)
    raise RuntimeError("Chrome debugging port ready nahi hua")


# Window/viewport size. Must FIT node_agent's Xvfb (1440x900) or the window hangs off
# the screen and cannot be driven over VNC. Same numbers are used for the Playwright
# viewport so the page fills the window exactly — read.py:423 does the same.
WIN_W = int(os.environ.get("NYKAA_WIN_W", 1440))
WIN_H = int(os.environ.get("NYKAA_WIN_H", 900))


# ================= GEONODE PROXY =================
# Nykaa sits behind Akamai, which blocks datacenter IPs outright ("Access Denied",
# errors.edgesuite.net). A residential exit is the only way the page loads at all.
# Country is fixed to India: the site is India-only and the OTP goes to an Indian
# mobile, so any other exit is a mismatch waiting to be flagged.
GEONODE_USER_BASE = os.environ.get(
    "GEONODE_USER_BASE", "geonode_xvmYN44Bvz-type-residential-country-{}")
GEONODE_PASS = os.environ.get("GEONODE_PASS", "a8a841f4-46ad-4059-bf25-c9d8170908ff")
GEONODE_HOST = os.environ.get("GEONODE_HOST", "sg.proxy.geonode.io")
GEONODE_PORT = os.environ.get("GEONODE_PORT", "11000")
# CASE MATTERS. buyer.py (jo mahino se chal raha hai) config.json se
# "...-type-residential-country-IN" bhejta hai. Yahan .lower() lagta tha, to nykaa
# "country-in" bhejta tha — Geonode use apne India pool par nahi bhejta, aur tunnel ke
# andar "HTTP/1.1 400 Bad Request / Target website error" laut aata tha, jise Chrome
# ERR_SSL_PROTOCOL_ERROR bolta hai. Naapa gaya: country-in par example.com/google.com
# dono fail, country-IN par dono 200.
GEONODE_COUNTRY = os.environ.get("GEONODE_COUNTRY", "IN")


def proxy_enabled():
    """settings.json -> nykaa.proxy, re-read every call so the dashboard toggle applies
    without a restart (same as the reader/source bots)."""
    v = os.environ.get("NYKAA_PROXY")
    if v is None:
        try:
            from settings_util import load_settings
            v = (load_settings("nykaa") or {}).get("proxy")
        except Exception:
            v = None
    if isinstance(v, bool):
        return v
    return str(v or "").strip().lower() in ("1", "true", "yes", "on")


# Bridges started by launch_browser. One account = one browser = one bridge; the next
# launch tears down the previous one, so a long-running slot never accumulates them.
_BRIDGES = []


async def _stop_bridges():
    while _BRIDGES:
        await stop_proxy_bridge(_BRIDGES.pop())



# ---------------- Geonode SOCKS5 -> local HTTP bridge ----------------
# Geonode's :11000 speaks SOCKS5 ONLY — verified with curl: the http:// form returns
# nothing, socks5h:// returns an Indian residential IP. Playwright's proxy option can
# only do HTTP, so we run a tiny in-process HTTP proxy on 127.0.0.1 that CONNECT-tunnels
# out through Geonode's SOCKS5. Same approach source.py uses, same code.

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
    dbytes = dst_host.encode()
    writer.write(b"\x05\x01\x00\x03" + bytes([len(dbytes)]) + dbytes + int(dst_port).to_bytes(2, "big")); await writer.drain()
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

class InfraError(Exception):
    """The BOX is broken (no browser binary, no display, out of memory) — not the
    account. Lives here so every flow and the fleet runner agree on one type: the
    runner puts the queue row BACK on this, instead of spending it on a box that was
    never going to work."""


async def dump_page(page, tag="fail"):
    """Failure ke waqt screen ko file me save karo — screenshot + URL + page ka text.

    Ek account fail hone ka matlab ek khareeda hua number chala gaya. Log sirf itna
    batata hai ki kaunsa element nahi mila; ye batata hai ki screen par tha kya —
    error message, captcha, ya "email already registered". Bina iske har baar VNC pe
    baithna padta hai, jo 100 slots pe mumkin nahi."""
    import time as _t
    stamp = _t.strftime("%H%M%S")
    base = os.path.join(_BASE, "instance_logs", f"fail_{INSTANCE}_{tag}_{stamp}")
    try:
        os.makedirs(os.path.dirname(base), exist_ok=True)
    except Exception:
        pass
    try:
        await page.screenshot(path=base + ".png", full_page=False)
    except Exception as e:
        print(f"[DUMP] screenshot nahi bana: {str(e)[:80]}")
    try:
        txt = await page.inner_text("body")
    except Exception:
        txt = ""
    try:
        with open(base + ".txt", "w", encoding="utf-8") as f:
            f.write(f"url: {page.url}\n\n{txt[:4000]}")
    except Exception:
        pass
    # pehli kuch lines seedha log me bhi — aksar wajah wahin likhi hoti hai
    head = " | ".join([l.strip() for l in txt.splitlines() if l.strip()][:6])
    print(f"[DUMP] {base}.png")
    print(f"[DUMP] url: {page.url}")
    if head:
        print(f"[DUMP] screen: {head[:220]}")


def live_page(context, page):
    """Return a page that is actually usable. Nykaa's verify step can replace the tab we
    are holding; the handle we kept then raises "Target page ... has been closed" even
    though the browser is perfectly alive. Prefer the page we were given, else the newest
    open one in the context. Costs nothing when nothing was replaced."""
    try:
        if page is not None and not page.is_closed():
            return page
    except Exception:
        pass
    try:
        for other in reversed(context.pages):
            if not other.is_closed():
                print("[NK] ⚠️  page badal gaya tha — naye tab pe switch")
                return other
    except Exception:
        pass
    return page


def close_state(browser=None, context=None, page=None):
    """Playwright says "Target page, context or browser has been closed" for THREE very
    different failures — a dead page, a dead context, or a dead browser process — and
    the message never says which. Reading it as "the browser died" sent this hunt after
    OOM killers, cron jobs and signal senders that were never there. Print the three
    facts separately so the next failure names itself."""
    try:
        conn = browser.is_connected() if browser else "?"
    except Exception:
        conn = "?"
    try:
        closed = page.is_closed() if page else "?"
    except Exception:
        closed = "?"
    try:
        npages = len(context.pages) if context else "?"
    except Exception:
        npages = "?"
    return f"browser_connected={conn} page_closed={closed} context_pages={npages}"


async def launch_browser(p):
    """Launch a browser the way every other bot in this fleet does — p.chromium.launch()
    instead of spawning Chrome on a fixed --remote-debugging-port and connecting over
    CDP. Returns (browser, context, page).

    The CDP approach needed a unique port and profile dir per slot, and a stray port
    left open from a crashed run made the NEXT slot silently drive the OLD browser.
    Playwright owns the process here, so there is no port to collide on and the browser
    is torn down properly when the context manager exits.

    patchright (a stealth Playwright drop-in) is preferred by the caller's import; this
    just uses whatever `p` it was handed.
    """
    args = ["--disable-blink-features=AutomationControlled", "--disable-infobars",
            f"--window-size={WIN_W},{WIN_H}",
            "--no-first-run", "--no-default-browser-check"]
    if not IS_WINDOWS:
        # These are buyer.py's flags, verbatim (buyer.py:1126). buyer and read have run
        # headed Chrome on these exact Xvfb boxes for months without a browser dying, so
        # this bot uses their set instead of one invented for it.
        #
        # Two flags that USED to be here are deliberately gone:
        #   --disable-software-rasterizer : with --disable-gpu also set, Chromium has NO
        #       rendering path left (no GPU, and SwiftShader forbidden) and exits within
        #       seconds of launch. This is what killed the browser before the first
        #       page.goto() even ran. Documented: ember-cli/ember-cli#8778, crbug 737678.
        #   --disable-features=VizDisplayCompositor : obsolete (Viz is not optional in
        #       modern Chromium), and it OVERRODE Playwright's own --disable-features
        #       list, since Chrome takes only the last one given.
        args += ["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage",
                 "--disable-gpu",
                 # NO --disable-features here. Chrome honours only the LAST one given,
                 # and Playwright already passes its own list; ours replaced it wholesale.
                 # Measured through the proxy: with "site-per-process" in it every site
                 # failed, without it example.com/google.com returned 200.
                 #
                 # the OTP wait leaves the page untouched for ~7 minutes; without these
                 # Chrome throttles/discards a backgrounded tab in exactly that window.
                 "--memory-pressure-off", "--disable-background-timer-throttling"]
    if HEADLESS:
        # Nykaa's CDN resets HTTP/2 for headless, and the UA still says HeadlessChrome.
        args += ["--disable-http2",
                 "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                 "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"]

    # Chrome ka APNA log. Until now, when the browser process died there was no record
    # anywhere of why — Playwright only reports "Target ... has been closed", which is
    # the symptom, and Chrome's stderr went nowhere. This makes Chrome write its own
    # fatal/error lines to a file that survives the run.
    try:
        _logdir = os.path.join(_BASE, "instance_logs")
        os.makedirs(_logdir, exist_ok=True)
        _chrome_log = os.path.join(_logdir, f"chrome_{INSTANCE}.log")
        args += ["--enable-logging", f"--log-file={_chrome_log}"]
        print(f"[NK] chrome log: {_chrome_log}")
    except Exception:
        pass

    kw = {"headless": HEADLESS, "args": args}

    # Geonode's :11000 is SOCKS5-only (curl proves it: http:// returns nothing,
    # socks5h:// returns an Indian residential IP). Playwright can only be told about an
    # HTTP proxy, so point it at a local bridge that CONNECT-tunnels out over SOCKS5.
    await _stop_bridges()
    if proxy_enabled():
        user = GEONODE_USER_BASE.format(GEONODE_COUNTRY)
        server, local_port = await start_proxy_bridge(user)
        _BRIDGES.append(server)
        kw["proxy"] = {"server": f"http://127.0.0.1:{local_port}"}
        print(f"[PROXY] Geonode residential ({GEONODE_COUNTRY.upper()}) "
              f"via SOCKS5 bridge on 127.0.0.1:{local_port}")
    else:
        print("[PROXY] OFF — Nykaa Akamai ke peeche hai, datacenter IP block ho jaayega")
    # NO executable_path by default — buyer.py and read.py never set one, and neither
    # should this. The engine is patchright, whose stealth build is its OWN patched
    # chromium; pointing it at playwright's chromium instead is a mismatch, and that
    # browser kept dying mid-account. Set CHROME_PATH explicitly only to override.
    if os.environ.get("CHROME_PATH", "").strip():
        kw["executable_path"] = os.environ["CHROME_PATH"].strip()

    # Retry the launch like buyer.py:1201 does — a transient failure should cost a few
    # seconds, not the whole account.
    browser = None
    last = None
    for attempt in range(1, 4):
        try:
            browser = await p.chromium.launch(**kw)
            break
        except Exception as e:
            last = str(e).split("\n")[0][:200]
            print(f"   ⚠️ browser launch fail ({attempt}/3): {last} — 5s me retry")
            await asyncio.sleep(5)
    if browser is None:
        raise InfraError(last or "browser launch failed")
    context = await browser.new_context(
        viewport={"width": WIN_W, "height": WIN_H},
        ignore_https_errors=True,
    )
    # Every action and navigation inherits these, so a call site that passes no timeout
    # gets the generous value instead of Playwright's 30s default. Behind a residential
    # proxy 30s is routinely too short, and a slow IP must not cost a whole account.
    context.set_default_timeout(PW_TIMEOUT)
    context.set_default_navigation_timeout(NAV_TIMEOUT)
    page = await context.new_page()
    return browser, context, page


async def wait_for_otp_screen(page, timeout=None):
    """OTP boxes aane ka wait karo."""
    await page.wait_for_selector(OTP_DIGIT(1), timeout=timeout)
    await page.wait_for_timeout(1500)
    body = (await page.inner_text("body")).lower()
    if "resend otp in" in body:
        print("✅ OTP SEND HO GAYA (timer dikh raha hai)!")
    else:
        print("⚠️  Timer nahi dikha — OTP shayad na gaya ho. Browser dekho.")


async def setup_address(page):
    """Profile page pe jaake naya address add karo."""
    print("\n" + "=" * 55)
    print("🏠 ADDRESS SETUP START")
    print("=" * 55)

    # --- Profile page pe jao (direct) ---
    print(f"🌐 Profile page open: {PROFILE_URL}")
    await page.goto(PROFILE_URL, timeout=NAV_TIMEOUT, wait_until="domcontentloaded")
    await page.wait_for_timeout(4000)

    # --- ADD NEW ADDRESS click ---
    print("➕ 'ADD NEW ADDRESS' dhoond rahe hain...")
    if not await robust_click(page, ADD_ADDRESS_BTN, text="ADD NEW ADDRESS", label="ADD NEW ADDRESS"):
        print("⚠️ 'ADD NEW ADDRESS' button nahi mila. Browser dekho.")
        return
    await page.wait_for_timeout(3000)

    # --- Address form fill ---
    print("📝 Address form fill kar rahe hain...")

    # Name
    await page.wait_for_selector(ADDR_NAME_INPUT, timeout=PW_TIMEOUT)
    await page.click(ADDR_NAME_INPUT)
    await page.type(ADDR_NAME_INPUT, NAME, delay=60)
    print(f"   👤 Name: {NAME}")
    await page.wait_for_timeout(600)

    # Mobile
    await page.click(ADDR_MOBILE_INPUT)
    await page.type(ADDR_MOBILE_INPUT, MOBILE, delay=60)
    print(f"   📱 Mobile: {MOBILE}")
    await page.wait_for_timeout(600)

    # Postal Code
    await page.click(ADDR_POSTAL_INPUT)
    await page.type(ADDR_POSTAL_INPUT, POSTAL_CODE, delay=80)
    print(f"   📮 Postal: {POSTAL_CODE}")
    await page.wait_for_timeout(2000)  # postal se city/state autofill ho sakta hai

    # Address line (textarea)
    await page.click(ADDR_TEXTAREA)
    await page.type(ADDR_TEXTAREA, ADDRESS_LINE, delay=40)
    print(f"   🏘️  Address: {ADDRESS_LINE}")
    await page.wait_for_timeout(1500)

    # Address ke baad blur -> button enable ho
    await page.keyboard.press("Tab")
    await page.wait_for_timeout(1000)

    # --- Add Address button (disabled tab tak jab tak form valid na ho) ---
    print("💾 'Add Address' button click...")
    btn = page.locator(ADD_ADDRESS_SUBMIT).first
    # button enable hone ka thoda wait
    for _ in range(12):
        try:
            if await btn.is_enabled():
                break
        except Exception:
            pass
        await page.wait_for_timeout(1000)
    if await robust_click(page, ADD_ADDRESS_SUBMIT, text="Add Address", label="Add Address"):
        print("✅ Address ADD ho gaya!")
    else:
        print("⚠️ Add Address click fail — form check karo, koi field missing ho sakti hai.")
    await page.wait_for_timeout(4000)


async def run():
    launch_real_chrome()
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(f"http://127.0.0.1:{DEBUG_PORT}")
        context = browser.contexts[0] if browser.contexts else await browser.new_context()

        page = None
        for pg in context.pages:
            if "nykaa" in pg.url:
                page = pg
                break
        if page is None:
            page = context.pages[0] if context.pages else await context.new_page()

        try:
            if "nykaa" not in page.url:
                print(f"🌐 Opening Nykaa: {NYKAA_URL}")
                await page.goto(NYKAA_URL, timeout=NAV_TIMEOUT, wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)

            # Already logged in?
            if await page.query_selector(SIGN_IN_BTN) is None:
                print("✅ Aap pehle se logged in ho (session saved)!")
                await ask_terminal("👉 Band karne ke liye Enter dabao...")
                return

            # --- Sign in ---
            print("🔑 'Sign in' button click...")
            await page.click(SIGN_IN_BTN, timeout=PW_TIMEOUT)
            await page.wait_for_timeout(2500)

            # --- Mobile number ---
            print(f"📱 Mobile number type: {MOBILE}")
            await page.wait_for_selector(MOBILE_INPUT, timeout=PW_TIMEOUT)
            await page.click(MOBILE_INPUT)
            await page.type(MOBILE_INPUT, MOBILE, delay=120)
            await page.wait_for_timeout(1500)

            # --- Send OTP ---
            print("📨 'Send OTP' button click...")
            await page.click(SEND_OTP_BTN, timeout=PW_TIMEOUT)

            # --- Mobile OTP ---
            print("⏳ Mobile OTP page load ho raha hai...")
            await wait_for_otp_screen(page)
            mobile_otp = await get_otp(f"OTP number {MOBILE} pe aaya hoga.")
            await fill_otp(page, mobile_otp)
            await page.wait_for_timeout(4000)

            # --- Ab decide: naya account form aaya ya login ho gaya? ---
            if await wait_for_signup_form(page):
                print("\n🆕 Naya account form aaya — Name + Email bhar rahe hain...")

                # Name
                name_sel = await find_present(page, NAME_INPUTS)
                print(f"👤 Name: {NAME}  (selector: {name_sel})")
                await page.click(name_sel)
                await page.type(name_sel, NAME, delay=80)
                await page.wait_for_timeout(1000)

                # Email
                email_sel = await find_present(page, EMAIL_INPUTS)
                if not email_sel:
                    await page.wait_for_selector(EMAIL_INPUTS[0], timeout=PW_TIMEOUT)
                    email_sel = EMAIL_INPUTS[0]
                print(f"📧 Email: {EMAIL}  (selector: {email_sel})")
                await page.click(email_sel)
                await page.type(email_sel, EMAIL, delay=80)
                await page.wait_for_timeout(800)
                # Blur -> validation trigger ho (button enable hone ke liye)
                await page.keyboard.press("Tab")
                await page.wait_for_timeout(1500)

                # --- 'Yes, Proceed' button (name+email submit) ---
                print("➡️  'Yes, Proceed' button click...")
                await robust_click(page, YES_PROCEED_BTN, text="Yes, Proceed", label="Yes, Proceed")
                await page.wait_for_timeout(2500)

                # --- Email OTP ---
                print("⏳ Email OTP page load ho raha hai...")
                await wait_for_otp_screen(page)
                email_otp = await get_otp(f"OTP email {EMAIL} pe aaya hoga (inbox check karo).")
                await fill_otp(page, email_otp)
                await page.wait_for_timeout(4000)

            # --- Login verify ---
            await page.wait_for_timeout(2000)
            print(f"\n📍 Current page: {page.url}")
            if await page.query_selector(SIGN_IN_BTN) is not None:
                print("⚠️  Login confirm nahi hua (Sign-in button abhi bhi dikh raha).")
                print("   Address setup skip kar rahe hain.")
            else:
                print("✅ ACCOUNT CREATE / LOGIN SUCCESSFUL! Session save ho gaya.")
                # --- Address setup ---
                await setup_address(page)

            print("\n🎉 SAB STEPS COMPLETE!")
            await ask_terminal("\n👉 Browser band karne ke liye Enter dabao...")

        except Exception as e:
            print(f"❌ Error: {e}")
            await ask_terminal("👉 Band karne ke liye Enter dabao...")
        finally:
            try:
                await browser.close()
            except Exception:
                pass
            print("👋 Done. (Chrome window aap khud band kar sakte ho)")


if __name__ == "__main__":
    asyncio.run(run())