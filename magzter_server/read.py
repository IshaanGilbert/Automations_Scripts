"""
read.py — Magzter reader (Postgres-backed). NO proxy. Proven simple login logic.

Per claimed account:
  1. Login (email -> 2nd screen). 2nd screen is a plain password screen OR a
     "Create Account" set-password form (Full Name + Country + Password). We just
     FILL whatever is present — name (#inp_box), Country=India (if shown), password —
     and submit. One unified flow, exactly like the version that worked well.
  2. my_orders -> read Transaction ID + Date.
  3. Gold publications -> actually read 2-5 magazines (count real page turns).
  4. Write result to Postgres ONCE:
       done   -> at least one magazine actually read
       failed -> nothing read (login/orders/magazines didn't work) — reason in `error`

Tasks come from Postgres (read_tasks); the promoter fills them from completed
'readfile' sheet <-> DB, so the reader never touches Google Sheets (quota-safe).
Run:  ./venv/bin/python3 read.py --instance 1 --sessions 3
"""

import asyncio
import random
import logging
import argparse
import sys
import time
import re
import os
import socket
import struct
import threading
import traceback
from datetime import datetime

os.environ["TZ"] = "Asia/Calcutta"
try:
    time.tzset()
except Exception:
    pass

from playwright.async_api import async_playwright
import db  # Postgres task store
from fingerprint import Fingerprint   # GoLogin-style per-account fingerprint spoofing

# ====================== ARGUMENTS ======================
parser = argparse.ArgumentParser()
parser.add_argument('--instance', type=int, default=1)
parser.add_argument('--total-instances', type=int, default=1)
# Parallel browser sessions on THIS instance (max 4). Fallback only — settings.json
# reader.sessions overrides it live (re-read every batch).
parser.add_argument('--sessions', type=int, default=4)
args = parser.parse_args()

INSTANCE_ID = args.instance
TOTAL_INSTANCES = args.total_instances
DEFAULT_SESSIONS = max(1, args.sessions)

# ====================== PROXY (India residential, via config.json) ======================
# Magzter's store/login depends on the client IP, so we route through the SAME India
# proxy the buyer (script.py) uses. Playwright can't do SOCKS5 auth, so Socks5Tunnel
# exposes a local auth-less HTTP proxy that forwards to the upstream SOCKS5 (geonode).
try:
    from settings_util import load_json as _load_json
    _cfg = _load_json("config.json", {}) or {}
except Exception:
    _cfg = {}

PROXY_HOST = (_cfg.get("PROXY_HOST") or "").strip()
PROXY_PORT = int(_cfg.get("PROXY_PORT") or 0)
PROXY_USER = (_cfg.get("PROXY_USERNAME") or "").strip()
PROXY_PASS = (_cfg.get("PROXY_PASSWORD") or "").strip()

# Magzter's /login/email uses INVISIBLE reCAPTCHA v3 (api.js?render=<sitekey> + grecaptcha
# .execute). Headless bots score low -> server rejects the email step with "Sorry, We could
# not process your request now" (status=-3) -> login never reaches the password form. We
# solve the v3 token via 2captcha and inject it so login succeeds headless. Reuses the
# buyer's 2captcha key; both key + sitekey are overridable in config.json.
CAPTCHA_API_KEY = (str(_cfg.get("CAPTCHA_API_KEY") or "a0e3a745ea0f1d30cf95d98ec4402c07")).strip()
LOGIN_RECAPTCHA_SITEKEY = (str(_cfg.get("LOGIN_RECAPTCHA_SITEKEY")
                              or "6LePk50UAAAAAAMVdVXntpM-xrLezBXtD7jc_BEt")).strip()
LOGIN_RECAPTCHA_ACTION = (str(_cfg.get("LOGIN_RECAPTCHA_ACTION") or "login")).strip()

# GoLogin (Orbita anti-detect browser) — OPT-IN. Set GOLOGIN_TOKEN in config.json to route
# the reader through a REAL anti-detect browser (much higher reCAPTCHA v3 score => login
# passes without solving a captcha). GOLOGIN_PROFILE_ID (optional) reuses ONE profile; else
# a fresh random-fingerprint profile is created per browser (carrying the India proxy) and
# deleted afterwards. EMPTY token => reader uses the normal Chromium + fingerprint.py
# (completely unchanged — this is purely additive/opt-in).
GOLOGIN_TOKEN = (str(_cfg.get("GOLOGIN_TOKEN") or "")).strip()
GOLOGIN_PROFILE_ID = (str(_cfg.get("GOLOGIN_PROFILE_ID") or "")).strip()


def _proxy_setting_on():
    """Proxy is OFF by default (it was too slow). Turn it back on per-box with
    settings.json reader.proxy = true."""
    try:
        from settings_util import load_settings
        v = (load_settings("reader") or {}).get("proxy")
        return str(v).strip().lower() in ("1", "true", "yes", "on") if v is not None else False
    except Exception:
        return False


PROXY_ENABLED = bool(PROXY_HOST and PROXY_PORT and PROXY_USER) and _proxy_setting_on()

_LOCAL_PROXY_PORT = None          # set in main() once the tunnel is up


class Socks5Tunnel:
    """Local auth-less HTTP proxy on 127.0.0.1 that tunnels (CONNECT) to an upstream
    authenticated SOCKS5 proxy. One tunnel serves all parallel sessions."""
    def __init__(self, host, port, user, pwd):
        self.host, self.port, self.user, self.pwd = host, port, user, pwd
        self.local_port, self.running = None, False

    def find_port(self):
        base = 11000 + (INSTANCE_ID * 100)
        for p in range(base, base + 100):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                s.bind(('127.0.0.1', p)); s.close(); return p
            except Exception:
                s.close()
        return None

    def connect_socks5(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(120)
        s.connect((self.host, self.port))
        s.send(b'\x05\x01\x02'); s.recv(2)
        auth = b'\x01' + bytes([len(self.user)]) + self.user.encode() + bytes([len(self.pwd)]) + self.pwd.encode()
        s.send(auth)
        if s.recv(2) != b'\x01\x00':
            raise Exception("SOCKS5 auth failed")
        return s

    def handle(self, client):
        try:
            remote = self.connect_socks5()
            data = b""
            while b"\r\n\r\n" not in data:
                d = client.recv(4096)
                if not d:
                    return
                data += d
            req = data.decode('utf-8', errors='ignore')
            host, port = None, 80
            if req.startswith('CONNECT'):
                host, port = req.split(' ')[1].split(':'); port = int(port)
            else:
                for line in req.split('\r\n'):
                    if line.lower().startswith('host:'):
                        host = line.split(':')[1].strip(); break
                if not host:
                    return
            remote.send(b'\x05\x01\x00\x03' + bytes([len(host)]) + host.encode() + struct.pack('!H', port))
            remote.recv(10)
            client.send(b'HTTP/1.1 200 Connection Established\r\n\r\n')

            def forward(src, dst):
                try:
                    while True:
                        d = src.recv(8192)
                        if not d:
                            break
                        dst.send(d)
                except Exception:
                    pass
                finally:
                    try: dst.close()
                    except Exception: pass

            t1 = threading.Thread(target=forward, args=(client, remote), daemon=True)
            t2 = threading.Thread(target=forward, args=(remote, client), daemon=True)
            t1.start(); t2.start()
            t1.join(300); t2.join(300)
        except Exception:
            pass
        finally:
            try: client.close()
            except Exception: pass

    def start(self):
        self.local_port = self.find_port()
        if not self.local_port:
            raise Exception("No free local port for proxy tunnel")
        self.running = True
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('127.0.0.1', self.local_port))
        s.listen(128); s.settimeout(1)

        def accept():
            while self.running:
                try:
                    c, _ = s.accept()
                    threading.Thread(target=self.handle, args=(c,), daemon=True).start()
                except socket.timeout:
                    continue
                except Exception:
                    break
            s.close()

        threading.Thread(target=accept, daemon=True).start()
        return self.local_port

    def stop(self):
        self.running = False

# ====================== LOGGING ======================
# Logs go into read_logs/instance<ID>/ (next to read.py, not the CWD root) so each
# instance's logs sit in their own subfolder instead of cluttering the project root.
_LOG_BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "read_logs",
                         f"instance{INSTANCE_ID}")
os.makedirs(_LOG_BASE, exist_ok=True)
log_filename = os.path.join(_LOG_BASE,
                            f"read_i{INSTANCE_ID}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [I%(instance)s] %(message)s",
    handlers=[logging.FileHandler(log_filename, encoding="utf-8"), logging.StreamHandler()]
)
_base_logger = logging.getLogger(__name__)
logger = logging.LoggerAdapter(_base_logger, {"instance": INSTANCE_ID})

# Captcha screenshots go into screenshots/instance<ID>/ (next to read.py) so a blocked
# login leaves visual evidence of exactly what challenge appeared.
_SHOT_BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots",
                          f"instance{INSTANCE_ID}")
os.makedirs(_SHOT_BASE, exist_ok=True)


# ====================== LIVE SETTINGS (re-read every batch) ======================
MAX_SESSIONS = 4          # hard cap — 2x2 visible grid per instance


def current_sessions():
    try:
        from settings_util import load_settings
        v = (load_settings("reader") or {}).get("sessions")
        if v:
            return max(1, min(MAX_SESSIONS, int(v)))
    except Exception:
        pass
    return max(1, min(MAX_SESSIONS, DEFAULT_SESSIONS))


def headless_mode():
    """Default FALSE (headed, inside Xvfb) — the proven setup. Override per-box with
    settings.json reader.headless = true."""
    try:
        from settings_util import load_settings
        v = (load_settings("reader") or {}).get("headless")
        if v is not None:
            return bool(v) if isinstance(v, bool) else str(v).strip().lower() in ("1", "true", "yes", "on")
    except Exception:
        pass
    return False


# How many times to re-attempt a WHOLE account (fresh browser each time) before we
# write 'failed'. Most failures are transient — a slow/dead browser launch ("Target
# page, context or browser has been closed") or a half-loaded page that turns 0 pages.
# A clean second attempt usually succeeds, so this is the single biggest lever on the
# failure ratio. Default 3, override per-box with settings.json reader.retries.
MAX_ACCOUNT_ATTEMPTS = 3


def account_attempts():
    try:
        from settings_util import load_settings
        v = (load_settings("reader") or {}).get("retries")
        if v is not None:
            return max(1, min(6, int(v)))
    except Exception:
        pass
    return MAX_ACCOUNT_ATTEMPTS


# Random name fallback for the create-account form when Name_Used is blank.
_FIRST = ["Amit", "Rahul", "Priya", "Sneha", "Vikas", "Neha", "Rohan", "Pooja", "Arjun", "Kiran"]
_LAST  = ["Sharma", "Singh", "Kumar", "Verma", "Gupta", "Yadav", "Patel", "Jain", "Rao", "Nair"]


def _ensure_name(name):
    name = (name or "").strip()
    return name if name else f"{random.choice(_FIRST)} {random.choice(_LAST)}"


# ====================== POPUP HANDLING ======================
POPUP_KILL_JS = """
(function(){
  try {
    Object.defineProperty(window, 'clevertap', {
      configurable:true,
      get:function(){ return this.__ct; },
      set:function(nv){
        try { if (nv) { nv.notifications = nv.notifications || {}; nv.notifications.push = function(){}; } } catch(e){}
        this.__ct = nv;
      }
    });
  } catch(e){}
  try { if (window.Notification) { Notification.requestPermission = function(cb){ if(cb) cb('denied'); return Promise.resolve('denied'); }; } } catch(e){}
  function rm(){
    try { document.querySelectorAll('.wzrk-alert,.wzrk-overlay,.wzrk-backdrop,[id^="wzrk"],[class*="wzrk"]').forEach(function(el){ el.remove(); }); } catch(e){}
  }
  try { new MutationObserver(rm).observe(document.documentElement||document,{childList:true,subtree:true}); } catch(e){}
  document.addEventListener('DOMContentLoaded', rm);
  setInterval(rm, 800);
})();
"""


async def dismiss_popups(page):
    for selector in ('#tooltipOkBtnD', 'button.tooltip-ok',
                     'button.jsx-a5473e9fc229b582.close-btn', 'button:has-text("Okay")'):
        try:
            btn = page.locator(selector).first
            if await btn.is_visible():
                await btn.click()
                await page.wait_for_timeout(300)
        except Exception:
            pass


async def auto_dismiss_loop(page, stop_event):
    while not stop_event.is_set():
        try:
            await dismiss_popups(page)
        except Exception:
            pass
        await asyncio.sleep(1)


# ====================== BROWSER FACTORY ======================
async def _create_gologin_browser(playwright, session_idx, seed):
    """OPT-IN GoLogin/Orbita anti-detect browser (when GOLOGIN_TOKEN set). Creates/starts a
    profile (carrying the India proxy), connects Playwright over CDP. Returns (browser,
    context); the GoLogin handle is stashed on browser._gl for cleanup."""
    from gologin import GoLogin
    def _start():
        gl = GoLogin({"token": GOLOGIN_TOKEN,
                      "extra_params": ["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"]})
        own = None
        if GOLOGIN_PROFILE_ID:
            gl.setProfileId(GOLOGIN_PROFILE_ID)
        else:
            prof = gl.createProfileRandomFingerprint({"os": "win", "name": f"reader-{seed or session_idx}"})
            pid = prof["id"] if isinstance(prof, dict) else prof
            if PROXY_HOST and PROXY_PORT and PROXY_USER:
                try:
                    gl.changeProfileProxy(pid, {"mode": "socks5", "host": PROXY_HOST,
                        "port": int(PROXY_PORT), "username": PROXY_USER, "password": PROXY_PASS})
                except Exception:
                    pass
            gl.setProfileId(pid); own = pid
        return gl, own, gl.start()          # gl.start() => "127.0.0.1:<port>"
    gl, own_profile, dbg = await asyncio.to_thread(_start)
    browser = await playwright.chromium.connect_over_cdp(f"http://{dbg}")
    ctxs = browser.contexts
    context = ctxs[0] if ctxs else await browser.new_context()
    try: await context.add_init_script(POPUP_KILL_JS)
    except Exception: pass
    browser._gl = gl                        # stashed for _gologin_cleanup
    browser._gl_own_profile = own_profile
    logger.info(f"[browser] GoLogin/Orbita connected ({dbg}, profile={own_profile or GOLOGIN_PROFILE_ID})")
    return browser, context


async def _gologin_cleanup(browser):
    """Stop Orbita + delete the per-account profile. Safe no-op if not a GoLogin browser."""
    gl = getattr(browser, "_gl", None)
    if not gl:
        return
    own = getattr(browser, "_gl_own_profile", None)
    def _stop():
        try: gl.stop()
        except Exception: pass
        if own:
            try: gl.delete(own)
            except Exception: pass
    try: await asyncio.to_thread(_stop)
    except Exception: pass


async def create_browser(playwright, session_idx=0, seed=None):
    # OPT-IN: GoLogin anti-detect browser (higher reCAPTCHA score). Empty token => normal path.
    if GOLOGIN_TOKEN:
        return await _create_gologin_browser(playwright, session_idx, seed)
    headless = headless_mode()
    # Headed: TILE windows in a 2x2 grid so all 4 sessions are visible at once
    # (NOT '--start-maximized', which stacks them so only one shows). Each window is
    # also the viewport size. Headless: lean memory flags.
    win_w, win_h = 720, 450
    if headless:
        launch_args = ['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu',
                       '--disable-extensions', '--disable-blink-features=AutomationControlled',
                       f'--window-size={win_w},{win_h}']
    else:
        col, row = session_idx % 2, session_idx // 2          # 2 across, then wrap
        pos_x, pos_y = col * (win_w + 8), row * (win_h + 40)
        launch_args = ['--disable-blink-features=AutomationControlled',
                       f'--window-size={win_w},{win_h}',
                       f'--window-position={pos_x},{pos_y}']
    # Launch with retry — under concurrency the (headless) chrome shell sometimes dies
    # mid-launch ("Target page/context/browser has been closed"). Retry with backoff.
    browser = None
    for attempt in range(1, 4):
        try:
            browser = await playwright.chromium.launch(headless=headless, args=launch_args)
            break
        except Exception as e:
            logger.warning(f"[browser] launch failed (attempt {attempt}/3): {str(e)[:120]}")
            await asyncio.sleep(3 * attempt)
    if browser is None:
        raise Exception("Browser launch failed after 3 attempts")
    # GoLogin-style fingerprint — one CONSISTENT spoofed device per account (seeded by
    # the email; same account => same machine across retries). Spoofs UA + client-hints +
    # navigator + screen + WebGL/canvas/audio + WebRTC. We KEEP the small grid viewport so
    # the visible 2x2 layout stays intact (a small window on a large screen is normal).
    fp = Fingerprint(seed=(seed or f"reader-sess{session_idx}"),
                     locale="en-IN", timezone_id="Asia/Kolkata")
    ctx_kwargs = fp.context_kwargs()
    ctx_kwargs["viewport"] = {"width": win_w, "height": win_h}     # keep the grid size
    ctx_kwargs["geolocation"] = {"latitude": 28.6139, "longitude": 77.2090}  # New Delhi
    ctx_kwargs["permissions"] = ["geolocation"]
    # Route through the local India proxy tunnel (auth-less HTTP -> geonode SOCKS5).
    if _LOCAL_PROXY_PORT:
        ctx_kwargs["proxy"] = {"server": f"http://127.0.0.1:{_LOCAL_PROXY_PORT}"}
        ctx_kwargs["ignore_https_errors"] = True
    context = await browser.new_context(**ctx_kwargs)
    await context.add_init_script(fp.init_script())
    await context.add_init_script(POPUP_KILL_JS)
    return browser, context


async def create_browser_with_retry(playwright, session_idx, task_id, attempts=3, seed=None):
    """Chromium launch itself can fail under parallel load ("Target page, context or
    browser has been closed" — a half-spawned process the OS killed). Don't let that
    burn the whole account: retry the launch a few times with a small backoff. Any
    partially-created browser is closed before the next try so we don't leak processes."""
    last_err = None
    for i in range(1, attempts + 1):
        browser = None
        try:
            browser, context = await create_browser(playwright, session_idx, seed=seed)
            return browser, context
        except Exception as e:
            last_err = e
            logger.warning(f"[Task {task_id}] browser launch failed "
                           f"(try {i}/{attempts}): {str(e)[:120]}")
            try:
                if browser:
                    await browser.close()
            except Exception:
                pass
            await asyncio.sleep(random.uniform(2, 5) * i)
    raise last_err if last_err else Exception("browser launch failed")


# ====================== LOGIN ======================
async def _fill_first(page, selectors, value, label):
    for sel in selectors:
        try:
            loc = page.locator(sel).first
            if await loc.count() and await loc.is_visible():
                await loc.fill(value)
                return True
        except Exception:
            pass
    return False


async def _click_first(page, selectors, label):
    for sel in selectors:
        try:
            loc = page.locator(sel).first
            if await loc.count() and await loc.is_visible() and await loc.is_enabled():
                await loc.click()
                return True
        except Exception:
            pass
    return False


async def _any_visible(page, selectors):
    for sel in selectors:
        try:
            loc = page.locator(sel).first
            if await loc.count() and await loc.is_visible():
                return True
        except Exception:
            pass
    return False


# "Continue" (login) AND "Create Account" (set-password) both submit the 2nd screen.
SUBMIT_BTNS = ['#continue_btn', 'button:has-text("Continue")',
               'button:has-text("Create Account")', 'button[type="submit"].max-width',
               'button[type="submit"]']
EMAIL_SELECTORS = ['#user-email-inp', 'input[name="mail"]', '#user-email', 'input[type="email"]']
PASS_SELECTORS  = ['#user-pass', '#pass', 'input[name="pass"]', 'input[name="password"]',
                   'input[type="password"]']


async def _set_country_india(page, task_id):
    """Create-account form has a searchable country box (#filterCountry) + dropdown
    (#myDropdown .sel__ctry). Force India."""
    try:
        ctry = page.locator('#filterCountry').first
        if not (await ctry.count() and await ctry.is_visible()):
            return
        await ctry.click()
        await ctry.fill("India")
        await page.wait_for_timeout(700)
        opt = page.locator('#myDropdown div.sel__ctry').filter(
            has_text=re.compile(r'^\s*India\s*$')).first
        if await opt.count():
            await opt.click()
            logger.info(f"[Task {task_id}] Country set to India")
        else:
            await ctry.fill("India")
    except Exception as e:
        logger.warning(f"[Task {task_id}] country set failed: {e}")


# Step-2 can be EITHER the password-login form OR the create-account form.
STEP2_SELECTOR = ('#user-pass, #pass, input[name="pass"], input[name="password"], '
                  'input[type="password"], #create-account-form, #filterCountry')


def _solve_recaptcha_v3(pageurl, sitekey, action, timeout=140):
    """Get a reCAPTCHA v3 token from 2captcha for the invisible login captcha.
    Returns the token string or None. Blocking (run via asyncio.to_thread)."""
    import requests
    try:
        r = requests.post("https://2captcha.com/in.php", data={
            "key": CAPTCHA_API_KEY, "method": "userrecaptcha", "googlekey": sitekey,
            "pageurl": pageurl, "version": "v3", "action": action, "min_score": 0.3,
            "json": 1}, timeout=30).json()
    except Exception as e:
        logger.warning(f"[recaptcha] 2captcha submit failed: {str(e)[:100]}")
        return None
    if str(r.get("status")) != "1":
        logger.warning(f"[recaptcha] 2captcha rejected: {r.get('request')}")
        return None
    cid = r["request"]
    for _ in range(max(1, timeout // 5)):
        time.sleep(5)
        try:
            res = requests.get("https://2captcha.com/res.php", params={
                "key": CAPTCHA_API_KEY, "action": "get", "id": cid, "json": 1}, timeout=30).json()
        except Exception:
            continue
        if str(res.get("status")) == "1":
            return res["request"]
        if res.get("request") != "CAPCHA_NOT_READY":
            logger.warning(f"[recaptcha] 2captcha error: {res.get('request')}")
            return None
    logger.warning("[recaptcha] not solved in time")
    return None


async def _inject_recaptcha_token(page, task_id):
    """Solve the invisible login reCAPTCHA v3 via 2captcha and inject the token so the
    email-continue step passes on headless bots (otherwise 'could not process your request')."""
    try:
        token = await asyncio.to_thread(_solve_recaptcha_v3,
                                        "https://www.magzter.com/login/email",
                                        LOGIN_RECAPTCHA_SITEKEY, LOGIN_RECAPTCHA_ACTION)
        if not token:
            logger.warning(f"[Task {task_id}] reCAPTCHA v3 not solved — login may fail")
            return False
        await page.evaluate("""(tk)=>{
            try{ var ci=document.getElementById('captchaInput'); if(ci) ci.value=tk; }catch(e){}
            try{ document.querySelectorAll('textarea#g-recaptcha-response,[name=\\"g-recaptcha-response\\"]').forEach(function(g){g.value=tk;}); }catch(e){}
            try{ if(window.grecaptcha){ window.grecaptcha.execute=function(){return Promise.resolve(tk);}; window.grecaptcha.ready=function(cb){try{cb&&cb();}catch(e){}}; } }catch(e){}
        }""", token)
        logger.info(f"[Task {task_id}] ✅ reCAPTCHA v3 token injected")
        return True
    except Exception as e:
        logger.warning(f"[Task {task_id}] reCAPTCHA solve error: {str(e)[:120]}")
        return False


# A VISIBLE captcha challenge that actually blocks login — NOT the always-present
# invisible reCAPTCHA v3 (that has no visible iframe, so it won't match these).
_CAPTCHA_SELECTORS = ['iframe[src*="hcaptcha.com"]', 'div.h-captcha', '[class*="hcaptcha"]',
                      'iframe[title*="recaptcha challenge" i]']
_CAPTCHA_TEXTS = ("verify you are human", "select all images", "press and hold",
                  "are you a robot", "unusual traffic", "i am not a robot")


async def _capture_captcha(page, task_id, tag="login"):
    """If a VISIBLE captcha challenge (hCaptcha or a reCAPTCHA image/checkbox popup) is
    on screen, save a screenshot to screenshots/instance<ID>/ and return its path.
    Purely diagnostic — never raises, never affects the login flow. Skips the invisible
    reCAPTCHA v3 that's always on the page."""
    try:
        hit = False
        for sel in _CAPTCHA_SELECTORS:
            try:
                loc = page.locator(sel).first
                if await loc.count() and await loc.is_visible():
                    hit = True
                    break
            except Exception:
                pass
        if not hit:
            try:
                body = (await page.locator('body').inner_text(timeout=3000)).lower()
                hit = any(t in body for t in _CAPTCHA_TEXTS)
            except Exception:
                pass
        if not hit:
            return None
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        path = os.path.join(_SHOT_BASE, f"captcha_t{task_id}_{tag}_{ts}.png")
        await page.screenshot(path=path, full_page=True)
        logger.warning(f"[Task {task_id}] 🧩 CAPTCHA detected ({tag}) — screenshot saved: {path}")
        return path
    except Exception as e:
        logger.warning(f"[Task {task_id}] captcha screenshot failed: {str(e)[:100]}")
        return None


async def do_login(page, email, password, name, task_id):
    """Two-step Magzter login:
      STEP 1: enter email -> Continue
      STEP 2: a form appears (email pre-filled) — ONE of:
              • login:          #user-pass  + #continue_btn
              • create-account: #inp_box(name) + #filterCountry(India) + #pass + "Create Account"
    We detect which one and fill it. No hard verification — my_orders is the real test."""
    logger.info(f"[Task {task_id}] Opening login page...")
    await page.goto("https://www.magzter.com/login/email", wait_until="domcontentloaded", timeout=90000)
    # Wait for the email field to actually render (proxy makes first paint slow) — don't
    # rush ahead on a half-loaded page.
    try:
        await page.wait_for_selector(", ".join(EMAIL_SELECTORS), state="visible", timeout=30000)
    except Exception:
        logger.warning(f"[Task {task_id}] email field slow to appear")
    await page.wait_for_timeout(1000)
    await dismiss_popups(page)

    # ---- STEP 1: email -> Continue ----
    await _fill_first(page, EMAIL_SELECTORS, email, "email")
    await page.wait_for_timeout(800)

    # Solve + inject the invisible reCAPTCHA v3 token BEFORE clicking Continue, else the
    # email step is rejected ("could not process your request") on headless bots.
    await _inject_recaptcha_token(page, task_id)

    # ---- STEP 2: reveal + WAIT for the password/create-account form. Proxy + 4 parallel
    #      sessions make this slow, so give it a long window AND up to 2 Continue tries
    #      before giving up — this is what was being rushed (the "did not appear" rows).
    have_step2 = await _any_visible(page, PASS_SELECTORS + ['#create-account-form', '#filterCountry'])
    for attempt in range(1, 3):
        if have_step2:
            break
        await _click_first(page, ['#continue_btn', 'button:has-text("Continue")',
                                  'button[type="submit"]'], "email-continue")
        try:
            await page.wait_for_selector(STEP2_SELECTOR, state="visible", timeout=30000)
            have_step2 = True
        except Exception:
            logger.warning(f"[Task {task_id}] step-2 form not visible (try {attempt}/2)")
            # step-2 often fails to appear because a captcha challenge blocked the
            # email-continue step — grab a screenshot of whatever's on screen.
            await _capture_captcha(page, task_id, "email-continue")
        await dismiss_popups(page)

    # ---- which form? ----
    is_signup = False
    try:
        is_signup = await page.locator('#create-account-form, #filterCountry').first.is_visible()
    except Exception:
        pass

    if is_signup:
        logger.info(f"[Task {task_id}] step-2 = Create-Account (name + India + password)")
        await _fill_first(page, ['#inp_box', 'input[name="name"]'], _ensure_name(name), "name")
        await _set_country_india(page, task_id)
    else:
        logger.info(f"[Task {task_id}] step-2 = password login")

    # Fill password — verify it actually landed; the page can still be settling, so
    # wait + retry a couple of times instead of submitting an empty form.
    filled = False
    for _ in range(3):
        if await _fill_first(page, PASS_SELECTORS, password, "password"):
            # confirm a password box now holds a value
            for sel in PASS_SELECTORS:
                try:
                    el = page.locator(sel).first
                    if await el.count() and (await el.input_value()):
                        filled = True
                        break
                except Exception:
                    pass
        if filled:
            break
        await page.wait_for_timeout(2000)
    if not filled:
        logger.warning(f"[Task {task_id}] password not fillable (step-2 never stabilised)")

    await page.wait_for_timeout(500)
    await _click_first(page, SUBMIT_BTNS, "submit")
    logger.info(f"[Task {task_id}] Login submitted")
    await page.wait_for_timeout(5000)

    # ---- CAPTCHA detection -------------------------------------------------------
    # If a visible captcha challenge popped up on submit, save a screenshot for review.
    await _capture_captcha(page, task_id, "after-login")

    # ---- INVALID PASSWORD detection ----------------------------------------------
    # A wrong password otherwise falls through silently to my_orders and looks like a
    # false NOT_FOUND. Magzter shows an error and stays on the login screen — surface it
    # clearly as "Password invalid" so the dashboard/error column says exactly that.
    try:
        _body = (await page.locator('body').inner_text(timeout=5000)).lower()
    except Exception:
        _body = ""
    _PW_ERR = ("incorrect password", "invalid password", "wrong password",
               "password is incorrect", "password you entered is incorrect",
               "incorrect email or password", "invalid email or password",
               "invalid credentials", "enter a valid password", "please enter valid password")
    if any(k in _body for k in _PW_ERR):
        logger.warning(f"[Task {task_id}] ❌ Password invalid")
        raise Exception("Password invalid")


# ====================== PROCESS ONE ACCOUNT ======================
async def _run_account_once(playwright, row_data, session_idx, attempt):
    """ONE full attempt at an account: fresh browser -> login -> orders -> read.
    Owns its own browser + reader-task lifecycle and always cleans them up. Returns a
    result dict; process_account decides whether to retry based on it. Raising is fine
    too — process_account catches it and retries."""
    task_id  = row_data["task_id"]
    email    = row_data["email"]
    password = row_data["password"]
    name     = row_data["name"]

    transaction_id, transaction_date = "NOT_FOUND", ""
    books_read, pages_read = 0, 0
    success, err_msg = False, ""
    proof_shot = ""
    browser = None
    reader_tasks = []

    try:
        browser, context = await create_browser_with_retry(playwright, session_idx, task_id, seed=email)
        page = await context.new_page()
        await do_login(page, email, password, name, task_id)

        # ===== Orders page: Transaction ID + Date =====
        # The order CAN exist but my_orders renders the table slowly (esp. under load /
        # headed Chromium). A too-short wait => false NOT_FOUND. So: wait longer, and if
        # still not seen, RELOAD my_orders once and re-check before giving up.
        orders_page = await context.new_page()
        for _oa in range(2):
            await orders_page.goto("https://www.magzter.com/dashboard/my_orders",
                                    wait_until="domcontentloaded", timeout=60000)
            await orders_page.wait_for_timeout(3000)
            try:
                await orders_page.wait_for_selector('td[data-title="Transaction ID"]', timeout=25000)
                transaction_id = (await orders_page.inner_text('td[data-title="Transaction ID"]')).strip() or "NOT_FOUND"
                logger.info(f"[Task {task_id}] Transaction ID: {transaction_id}")
                break
            except Exception:
                if _oa == 0:
                    logger.warning(f"[Task {task_id}] Transaction ID not seen — reloading my_orders & retrying")
                    await orders_page.wait_for_timeout(4000)
                    continue
                logger.warning(f"[Task {task_id}] Transaction ID not found (after reload retry)")
        try:
            transaction_date = (await orders_page.inner_text('td[data-title="Date"]')).strip()
        except Exception:
            pass

        # PROOF: no order id on my_orders -> save a full-page screenshot as evidence and
        # remember its path, so the operator can SEE why this row has no transaction id
        # right on the read row (attached in the dashboard). Best-effort; never breaks the run.
        if transaction_id == "NOT_FOUND":
            try:
                os.makedirs(_SHOT_BASE, exist_ok=True)
                _pfn = f"NOORDER_t{task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                await orders_page.screenshot(path=os.path.join(_SHOT_BASE, _pfn), full_page=True)
                proof_shot = f"instance{INSTANCE_ID}/{_pfn}"
                logger.info(f"[Task {task_id}] 📸 no order id — saved proof {proof_shot}")
            except Exception as _pe:
                logger.warning(f"[Task {task_id}] proof screenshot failed: {str(_pe)[:100]}")

        # Did my_orders say "you did not purchase anything"? If so, we still open just
        # ONE magazine (open + close) instead of reading 2-5 — light activity only.
        no_orders = False
        try:
            body = (await orders_page.inner_text('body')).lower()
            if any(k in body for k in ("did not purchase", "have not purchased", "haven't purchased",
                                       "no orders", "no purchase", "no transactions")):
                no_orders = True
                logger.info(f"[Task {task_id}] my_orders empty (no purchase) — will just open 1 magazine")
        except Exception:
            pass

        # ===== Gold publications -> Explore =====
        await orders_page.goto("https://www.magzter.com/dashboard/purchase/gold",
                                wait_until="domcontentloaded", timeout=60000)
        await orders_page.wait_for_timeout(3000)
        await orders_page.evaluate("window.scrollBy(0, 400)")
        await orders_page.wait_for_timeout(1000)
        try:
            explore = await orders_page.locator(
                'a[href="/magztergold/publications"] button.blue_transparent_btn').all()
            if explore:
                await random.choice(explore).click()
            else:
                await orders_page.click('a[href="/magztergold/publications"] button.blue_transparent_btn')
            logger.info(f"[Task {task_id}] Explore Now clicked")
        except Exception as e:
            logger.warning(f"[Task {task_id}] Explore Now error: {e}")
        await orders_page.wait_for_timeout(4000)

        # ===== Read magazines =====  no orders -> just 1 (open + close); else 2-5
        num_books = 1 if no_orders else random.randint(2, 5)
        logger.info(f"[Task {task_id}] Will open {num_books} book(s)"
                    + (" (no-purchase: open+close only)" if no_orders else ""))

        for book_num in range(1, num_books + 1):
            reader_page = orders_page
            try:
                if book_num > 1 and random.random() < 0.65:
                    try:
                        nxt = orders_page.locator(
                            'a.pagination-previous.svelte-1rpew09[aria-label="Next"], a[aria-label="Next"]')
                        if await nxt.count() > 0 and await nxt.first.is_visible():
                            await nxt.click()
                            await orders_page.wait_for_timeout(5000)
                    except Exception:
                        pass

                await orders_page.wait_for_selector('li.magazines-list a.magazines-anchor', timeout=12000)
                magazines = await orders_page.locator('li.magazines-list a.magazines-anchor').all()
                if not magazines:
                    logger.warning(f"[Task {task_id}] Book {book_num}: no magazines, skipping")
                    continue

                mag = random.choice(magazines)
                await mag.scroll_into_view_if_needed()
                await orders_page.wait_for_timeout(800)
                await mag.click()
                await orders_page.wait_for_timeout(4000)

                await orders_page.wait_for_selector('#reader', timeout=10000)
                await orders_page.click('#reader')
                await orders_page.wait_for_timeout(4000)

                reader_page = None
                for p_obj in context.pages:
                    if "reader.magzter.com" in p_obj.url:
                        reader_page = p_obj
                        break
                if not reader_page:
                    reader_page = orders_page

                stop_event = asyncio.Event()
                rt = asyncio.create_task(auto_dismiss_loop(reader_page, stop_event))
                reader_tasks.append((rt, stop_event))

                try:
                    okay = reader_page.locator('button:has-text("Okay"), .tooltip-ok, #tooltipOkBtnD').first
                    if await okay.count() and await okay.is_visible():
                        await okay.click()
                except Exception:
                    pass

                next_selector = None
                for sel in ('div.pagination-previous-icon.svelte-1rpew09',
                            'div.right img[alt="next page"]', '.right img[alt="next page"]',
                            'img[alt="next page"]'):
                    try:
                        await reader_page.wait_for_selector(sel, timeout=5000)
                        next_selector = sel
                        break
                    except Exception:
                        continue

                book_pages = 0
                # no-purchase accounts: just open + close (1 page); else read 3-4.
                pages_to_read = 1 if no_orders else random.randint(3, 4)
                if next_selector:
                    fails = 0
                    for i in range(pages_to_read):
                        await dismiss_popups(reader_page)
                        try:
                            await reader_page.click(next_selector, timeout=8000)
                            book_pages += 1
                            pages_read += 1
                            fails = 0
                            wait_sec = random.randint(5, 15)
                            logger.info(f"[Task {task_id}] Book {book_num}: page {i+1}/{pages_to_read} | wait {wait_sec}s")
                            await reader_page.wait_for_timeout(wait_sec * 1000)
                        except Exception:
                            fails += 1
                            if fails >= 3:
                                break
                            await reader_page.wait_for_timeout(5000)
                else:
                    logger.warning(f"[Task {task_id}] Book {book_num}: next button not found")

                if book_pages > 0:
                    books_read += 1
                    logger.info(f"[Task {task_id}] Book {book_num}: read {book_pages} page(s) (total {books_read})")

                stop_event.set()
                try:
                    await asyncio.wait_for(rt, timeout=5)
                except Exception:
                    pass

            except Exception as e:
                logger.warning(f"[Task {task_id}] Book {book_num} failed: {e}")
                continue

            if book_num < num_books:
                try:
                    await reader_page.goto("https://www.magzter.com/magztergold/publications",
                                            wait_until="domcontentloaded", timeout=60000)
                    await reader_page.wait_for_timeout(4000)
                except Exception:
                    pass

        # "Read complete" = at least one magazine actually got pages turned.
        success = books_read > 0
        if not success and not err_msg:
            err_msg = f"0 books read ({pages_read} pages turned)"

    except Exception as e:
        err_msg = str(e)[:300]
        logger.error(f"[Task {task_id}] attempt {attempt} error: {e}")
        traceback.print_exc()

    finally:
        # clean up reader auto-dismiss tasks
        for rt, stop_event in reader_tasks:
            stop_event.set()
            if not rt.done():
                try:
                    await asyncio.wait_for(rt, timeout=3)
                except Exception:
                    pass
        # always close this attempt's browser — a retry uses a brand-new one.
        try:
            if browser:
                try: await browser.close()
                except Exception: pass
                await _gologin_cleanup(browser)   # stop Orbita + delete profile (no-op if not GoLogin)
        except Exception:
            pass

    return {
        "success": success,
        "books_read": books_read,
        "pages_read": pages_read,
        "transaction_id": transaction_id,
        "transaction_date": transaction_date,
        "err_msg": err_msg,
        "proof_shot": proof_shot,
    }


async def process_account(playwright, row_data, session_idx=0):
    """Run an account with FAILED AUTO-RETRY (mirrors the buyer's retry behaviour):
    re-attempt the whole flow with a fresh browser up to `account_attempts()` times,
    then write the result to the DB exactly ONCE. The common failures —
    "Target page, context or browser has been closed" and "0 books read" — are almost
    always transient, so a clean retry recovers most of them."""
    task_id   = row_data["task_id"]
    email     = row_data["email"]
    row_index = row_data.get("row_index")

    logger.info(f"[Task {task_id}][Row {row_index}] Start: {email}")
    t_start = time.time()

    max_attempts = account_attempts()
    result = {"success": False, "books_read": 0, "pages_read": 0,
              "transaction_id": "NOT_FOUND", "transaction_date": "", "err_msg": "", "proof_shot": ""}

    for attempt in range(1, max_attempts + 1):
        # Stagger session starts so N logins don't fire in the same instant; on a
        # retry, back off a bit longer so a transient overload has time to clear.
        if attempt == 1:
            await asyncio.sleep(random.uniform(0.5, 2.5))
        else:
            backoff = random.uniform(4, 9) * attempt
            logger.info(f"[Task {task_id}] retry {attempt}/{max_attempts} "
                        f"(prev: {result['err_msg'] or 'no books'}) — waiting {backoff:.0f}s")
            await asyncio.sleep(backoff)

        try:
            result = await _run_account_once(playwright, row_data, session_idx, attempt)
        except Exception as e:
            # _run_account_once already cleans up; treat a raise as a failed attempt.
            result = {"success": False, "books_read": 0, "pages_read": 0,
                      "transaction_id": "NOT_FOUND", "transaction_date": "",
                      "err_msg": str(e)[:300], "proof_shot": ""}
            logger.error(f"[Task {task_id}] attempt {attempt} raised: {e}")

        if result["success"]:
            break
        # A wrong password will NEVER recover on retry — record it and stop early.
        if "password invalid" in (result.get("err_msg") or "").lower():
            logger.info(f"[Task {task_id}] password invalid — skipping retries")
            break

    success          = result["success"]
    books_read       = result["books_read"]
    pages_read       = result["pages_read"]
    transaction_id   = result["transaction_id"]
    transaction_date = result["transaction_date"]
    err_msg          = result["err_msg"]
    # Wrong password is a PERMANENT account error — it can never succeed on retry, so it
    # must not go back to 'retry' (that loops forever). Save the error and mark it 'failed'
    # so claim_read_rows never re-runs it.
    bad_password = "CHANGE_ME_PASSWORD" in (err_msg or "").lower()
    if not success and not err_msg:
        err_msg = f"0 books read ({pages_read} pages turned)"
    if not success and not bad_password:
        err_msg = f"{err_msg} (after {max_attempts} attempts)"

    duration = round(time.time() - t_start, 1)
    # ZERO-FAILED policy: a non-success row is NEVER marked 'failed' — it goes back to
    # 'retry' so claim_read_rows re-runs it later, again and again, until it reads at
    # least one magazine. (Requires headless=false so content actually loads; otherwise
    # every account "0 books" and loops forever doing nothing.)
    # EXCEPTION: invalid password is terminal — mark 'failed' (not 'retry') so it stops.
    if success:
        db_status = db.ST_DONE
    elif bad_password:
        db_status = db.ST_FAILED
    else:
        db_status = db.ST_RETRY
    saved_txn = transaction_id if transaction_id != "NOT_FOUND" else "NOT_FOUND"
    # Attach the proof screenshot ONLY when no order id was found; on a real txn we pass
    # none, and update_read_task clears any old proof (the buy is confirmed now).
    proof_shot = result.get("proof_shot") or ""
    proof_node = (os.environ.get("NODE_NAME") or "local") if (proof_shot and saved_txn == "NOT_FOUND") else None
    try:
        ok = await asyncio.to_thread(
            db.update_read_task,
            task_id=task_id,
            status=db_status,
            transaction_id=saved_txn,
            transaction_date=transaction_date,
            duration_sec=duration,
            error=err_msg,
            books_read=books_read,
            proof_shot=(proof_shot if saved_txn == "NOT_FOUND" else None),
            proof_node=proof_node,
        )
        if not ok:
            logger.error(f"[Task {task_id}] DB update returned False")
    except Exception as db_error:
        logger.error(f"[Task {task_id}] DB update failed: {db_error}")

    logger.info(f"[Task {task_id}][Row {row_index}] Done in {duration}s | "
                f"status={db_status} | books={books_read} | txn={saved_txn}")


# ====================== MAIN ======================
def _verify_proxy_ip(local_port):
    """Best-effort: print the exit IP the proxy gives, so you can confirm it's India."""
    try:
        import requests
        p = {"http": f"http://127.0.0.1:{local_port}", "https": f"http://127.0.0.1:{local_port}"}
        ip = requests.get("https://api.ipify.org?format=json", proxies=p, timeout=30).json().get("ip")
        logger.info(f"[Proxy] exit IP = {ip}")
    except Exception as e:
        logger.warning(f"[Proxy] IP check failed (tunnel may still work): {str(e)[:80]}")


async def main():
    global _LOCAL_PROXY_PORT
    logger.info(f"[Start] Reader instance {INSTANCE_ID}")
    try:
        db.assert_db_ready()
    except Exception as e:
        logger.error(f"[DB] not reachable: {e}")
        # Exit NON-ZERO so node_agent treats this as a crash (auto-restart), not a
        # clean "done" — matching the buyers' sys.exit(1). A bare return would exit 0.
        sys.exit(1)

    # Bring up ONE India proxy tunnel for all sessions on this instance.
    tunnel = None
    if PROXY_ENABLED:
        try:
            tunnel = Socks5Tunnel(PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)
            _LOCAL_PROXY_PORT = tunnel.start()
            logger.info(f"[Proxy] India tunnel up on 127.0.0.1:{_LOCAL_PROXY_PORT} "
                        f"(upstream {PROXY_HOST}:{PROXY_PORT})")
            await asyncio.to_thread(_verify_proxy_ip, _LOCAL_PROXY_PORT)
        except Exception as e:
            logger.error(f"[Proxy] tunnel failed to start — running DIRECT: {e}")
            _LOCAL_PROXY_PORT = None
    else:
        logger.warning("[Proxy] no PROXY_* in config.json — running DIRECT (server IP).")

    try:
        async with async_playwright() as playwright:
            _paused_logged = False
            while True:
                # GLOBAL PAUSE — operator kill-switch. Wait & re-poll while paused; never
                # exit, so the reader resumes the moment pause is lifted.
                if await asyncio.to_thread(db.is_paused):
                    if not _paused_logged:
                        logger.info("⏸️  PAUSED by operator — waiting (no new rows claimed)…")
                        _paused_logged = True
                    await asyncio.sleep(15)
                    continue
                if _paused_logged:
                    logger.info("▶️  Resumed — claiming rows again.")
                    _paused_logged = False
                n_sessions = current_sessions()
                claimed = await asyncio.to_thread(db.claim_read_rows, INSTANCE_ID, n_sessions)
                if not claimed:
                    logger.info("No pending rows left.")
                    break

                logger.info(f"Claimed {len(claimed)} row(s), concurrency={n_sessions}, "
                            f"headless={headless_mode()}, proxy={'on' if _LOCAL_PROXY_PORT else 'off'}")
                semaphore = asyncio.Semaphore(n_sessions)

                async def run_one(row_data, idx):
                    async with semaphore:
                        await process_account(playwright, row_data, idx)

                await asyncio.gather(
                    *[run_one(rd, idx) for idx, rd in enumerate(claimed)],
                    return_exceptions=True
                )
                await asyncio.sleep(2)
    finally:
        if tunnel:
            tunnel.stop()

    logger.info(f"[Complete] Instance {INSTANCE_ID} finished. Log: {log_filename}")


if __name__ == "__main__":
    asyncio.run(main())
