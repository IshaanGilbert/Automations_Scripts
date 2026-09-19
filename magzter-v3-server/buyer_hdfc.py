#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Magzter "best-of-both" buyer bot.

Base infrastructure is the DB-backed buyer (script.py); the more-robust browser
flow is ported from magzter-aws/magzter_final.py. Merged here:

KEPT FROM script.py (DB infra):
  - argparse (--instance / --total-instances), config loading, settings_util.
  - Socks5Tunnel (India proxy), LocalLogger, stuck-task watchdog (MAX_TASK_SECONDS).
  - OTP API consume-on-fetch logic: 200=fresh/return, 404=wait, 401/503=give up,
    429=backoff; X-OTP-Token + Authorization: Bearer headers.
  - 2captcha hCaptcha solver (solve_hcaptcha / _find_hcaptcha_sitekey).
  - DECLINE_MSGS / ELIGIBILITY_MSGS detection, CleverTap popup-kill init script.
  - DB claim loop (db.claim_next_group work-stealing) + db.update_task writeback.

PORTED FROM magzter_final.py (robust flow):
  1. /login/verify interstitial handling (Continue/Skip, retry 3x, then raise).
  2. Stripe FLOWS A/B/C detection (hosted checkout / name form / summary page),
     including Stripe opening in a NEW TAB / popup.
  3. fill_in_frames payment fill: scan page + all iframes with many selector
     variants for card number / expiry / cvc / cardholder name (#cardNumber path
     kept as one variant).
  4. Stripe hosted-checkout niceties: billing country -> India, UNCHECK "Save my
     information", cardholder name via cc-name / Full name, wait up to ~90s for the
     card form, reload embedded Stripe at ~45s.
  5. Fuzzy CORPORATE selectors (CORP_ID_SELS / EMP_ID_SELS) + JS-click-first for
     ICICI <a> submit anchors (_find_corp_ctx), keeping the 3x-reload retry.
  6. OTP card_last_four matching (card_no[-4:]) merged with script.py's
     consume-on-fetch HTTP-code handling: prefer a 200 whose card_last_four
     matches, else keep polling.

NEW db.py helpers used:
  - db.otp_lock(emp_id)        — serialize corp-submit -> OTP -> confirm per emp.
  - db.retry_or_fail(...)      — transient-failure requeue (RETRYABLE_ERRORS).
  - db.record_otp_failure/success(emp_id) — drives the dashboard alert banner.
"""

import time, random, string, json, os, sys, requests
import threading, socket, struct, re, argparse
from datetime import datetime
os.environ["TZ"] = "Asia/Calcutta"          # IST timestamps/logs
try: time.tzset()
except Exception: pass


import db   # local Postgres task store (runs from magzter-pro/)
from settings_util import load_json, load_settings
from fingerprint import Fingerprint   # GoLogin-style per-account fingerprint spoofing
# Prefer patchright (stealth fork) when installed — its anti-detection makes hCaptcha far
# more likely to PASS on the "I am human" checkbox with no solver. Falls back to vanilla
# playwright if patchright isn't installed. Same API, drop-in.
try:
    from patchright.sync_api import sync_playwright
    from patchright.sync_api import TimeoutError as PlaywrightTimeout
    _STEALTH = True
except ImportError:
    from playwright.sync_api import sync_playwright
    from playwright.sync_api import TimeoutError as PlaywrightTimeout
    _STEALTH = False

# ================= ARGUMENTS =================
parser = argparse.ArgumentParser()
parser.add_argument('--instance', type=int, default=1)
parser.add_argument('--total-instances', type=int, default=3)
args = parser.parse_args()

INSTANCE_ID = args.instance
TOTAL_INSTANCES = args.total_instances

print(f"🤖 Instance {INSTANCE_ID}/{TOTAL_INSTANCES}")

# ================= CONFIG =================
CONFIG_FILE = "config.json"
LOG_DIR = "logs"
SCREENSHOT_DIR = "screenshots"

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


# Use the shared loader (settings_util) so a missing/partial file never crashes.
config = load_json(CONFIG_FILE, {}) or {}


TARGET_URL = config.get("TARGET_URL", "https://app.adstracking.io/click?pid=3030&offer_id=20655")
OTP_API_URL = config.get("OTP_API_URL", "")
# Static token for the OTP API (sent as X-OTP-Token / Authorization: Bearer).
OTP_FETCH_TOKEN = config.get("OTP_FETCH_TOKEN") or ""
# Password used to LOG IN / create-account when verifying a purchase via my_orders.
# A freshly-bought email has no account yet → Magzter shows a "Create Account" form where
# we SET this password; an existing one → password login. Empty => skip login-verify.
VERIFY_LOGIN_PASSWORD = config.get("VERIFY_LOGIN_PASSWORD") or ""
# HDFC 3D-Secure "Static Password" PIN (buyer_hdfc build only). Set ONCE in config.json
# as  "HDFC_3DS_PIN": "000000".  The bank page hashes it client-side on submit
# (getHashedPWD: SHA-256+salt), so we fill the RAW PIN and click Submit — page does the hash.
HDFC_3DS_PIN = str(config.get("HDFC_3DS_PIN") or "").strip()
# EMAIL MUTATION: when an email is "not eligible" (account already exists), retry with a
# mutated address (dots/+tag/domain-swap) instead of giving up. Original stays in `email`,
# mutated in `updated_email`. Set EMAIL_MUTATION=false in config to disable.
EMAIL_MUTATION = str(config.get("EMAIL_MUTATION", True)).lower() not in ("0","false","no","off")
# Cap captcha-solve time so a flagged IP doesn't lock an instance for many minutes (the
# corp step calls the solver a few times; 180s each was wasting 9-15 min). Fail-fast.
CAPTCHA_TIMEOUT = int(config.get("CAPTCHA_TIMEOUT", 90))
# Hard cap on the whole corporate-form + captcha phase. If it can't get past captcha in
# this long, STOP wasting time — bail to RETRY (re-queued; a fresh proxy IP often skips
# the captcha). Default 5 min.
CAPTCHA_MAX_TOTAL = int(config.get("CAPTCHA_MAX_TOTAL", 300))
MAX_EMAIL_MUTATIONS = int(config.get("MAX_EMAIL_MUTATIONS", 4))
# 2captcha API key — used to solve an hCaptcha if one appears at the corporate step.
CAPTCHA_API_KEY = config.get("CAPTCHA_API_KEY") or "CHANGE_ME_SECRET"
# hCaptcha solver provider: "2captcha" (default) or "capsolver". CapSolver is often more
# reliable on hard hCaptcha challenges. Set CAPTCHA_PROVIDER + CAPSOLVER_API_KEY in
# config.json to switch. CapSolver falls back to the 2captcha key if no separate key set.
CAPTCHA_PROVIDER = (str(config.get("CAPTCHA_PROVIDER") or "2captcha")).strip().lower()
CAPSOLVER_API_KEY = config.get("CAPSOLVER_API_KEY") or CAPTCHA_API_KEY
# No paid solver (default): just CLICK the hCaptcha "I am human" checkbox. With patchright
# stealth + a clean residential proxy it often passes with no image challenge. If it does
# challenge, fail fast (re-queue) — we don't pay to solve. Set false to use the paid solver.
CAPTCHA_CLICK_ONLY = str(config.get("CAPTCHA_CLICK_ONLY", True)).lower() not in ("0","false","no","off")
# Optional FALLBACK hCaptcha sitekey. Normally the sitekey is auto-extracted from the
# live page; set HCAPTCHA_SITEKEY in config.json only as a backup for when extraction
# fails (used ONLY when an hCaptcha widget is actually present, so no wasted credits).
HCAPTCHA_SITEKEY = (str(config.get("HCAPTCHA_SITEKEY") or "")).strip()
WAIT_TASKS = config.get("WAIT_BETWEEN_TASKS", 30)
HEADLESS = bool(config.get("HEADLESS", True))      # default True for server
# How many instances may work the SAME employee in parallel (aws INSTANCES_PER_EMP).
# 1 = whole emp -> one instance (default). 2+ = split an emp across N instances so no
# slot sits idle when employees ≈ slots. OTP stays correct (db.otp_lock + card_last_four).
INSTANCES_PER_EMP = max(0, int(config.get("INSTANCES_PER_EMP", 1)))   # 0 = unlimited (1 emp -> all instances)


def current_instances_per_emp():
    """Re-read INSTANCES_PER_EMP LIVE from config.json before every group claim, so a
    dashboard change applies on the NEXT claim — no restart, no killing a bot that's
    mid-payment/OTP. Falls back to the startup value if the file can't be read."""
    try:
        cfg = load_json(CONFIG_FILE, {}) or {}
        return max(0, int(cfg.get("INSTANCES_PER_EMP", INSTANCES_PER_EMP)))
    except Exception:
        return INSTANCES_PER_EMP
PROXY_HOST = config.get("PROXY_HOST", "sg.proxy.geonode.io")
PROXY_PORT = config.get("PROXY_PORT", 11000)
PROXY_USERNAME = config.get("PROXY_USERNAME", "")
PROXY_PASSWORD = config.get("PROXY_PASSWORD", "")

# Timeouts in ms (bound how long a WRONG selector / dead page waits before failing).
GLOBAL_TIMEOUT     = int(config.get("GLOBAL_TIMEOUT", 60000))
NAVIGATION_TIMEOUT = int(config.get("NAVIGATION_TIMEOUT", 90000))
ELEMENT_WAIT       = int(config.get("ELEMENT_WAIT", 45000))
RETRY_COUNT        = int(config.get("RETRY_COUNT", 4))


# ================= RETRYABLE ERRORS (aws model) =================
# Transient failures that should be re-queued (db.retry_or_fail) instead of marked
# FAILED. Anything else is a terminal outcome (declined/ineligible/success/unconfirmed).
RETRYABLE_ERRORS = [
    "Corporate form not found",
    "Stripe payment form not loaded",
    "Corporate form did not submit",
    "Could not navigate to payment",
    "OTP screen not reached",
    "Claim button not found",
    "Captcha appeared",           # captcha fast-fail -> retry (fresh attempt lands clean)
]
MAX_TASK_RETRIES = 3

# ================= EMAIL → FILENAME =================

PROVIDER_MAP = {
    "gmail.com": "Gmail",
    "rediffmail.com": "Rediff",
    "yahoo.com": "Yahoo",
    "outlook.com": "Outlook",
    "hotmail.com": "Hotmail",
}

def email_to_filename(email):
    """Build '<CleanUsername><ProviderName>.png' from an email address."""
    email = str(email).strip()
    username, _, domain = email.partition("@")
    clean_user = re.sub(r"[^A-Za-z0-9_]", "", username)
    provider = PROVIDER_MAP.get(domain.lower())
    if not provider:
        base = domain.split(".")[0] if domain else "Unknown"
        provider = base.capitalize() if base else "Unknown"
    return f"{clean_user}{provider}.png"

# ================= STUCK WATCHDOG =================
# If a single task runs longer than MAX_TASK_SECONDS it is considered hung. The
# instance then exits itself so the monitor can restart JUST this instance with a
# fresh browser/page. The interrupted row (left 'running') is reclaimed on restart.
MAX_TASK_SECONDS = int(config.get("MAX_TASK_SECONDS", 600))   # hard cap per task (s); was 900
_task_deadline = None           # set while a task is running, None when idle

def _watchdog():
    while True:
        time.sleep(10)
        dl = _task_deadline
        if dl and time.time() > dl:
            print(f"⛔ Instance {INSTANCE_ID}: task exceeded {MAX_TASK_SECONDS}s (stuck) — "
                  f"exiting for auto-restart", flush=True)
            os._exit(2)

# ================= LOCAL LOGGER =================

class LocalLogger:
    def __init__(self, card, email, corp, emp, task_id=None):
        self.card,self.email,self.corp,self.emp=card,email,corp,emp
        self.task_id=task_id
        self.start=datetime.now()
        self.steps=[]
        self.name_used=""
        self.file=os.path.join(LOG_DIR,f"task_{card[-4:]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    def set_name(self,name): self.name_used=name
    def mark(self, step):
        """Record the CURRENT step (+ time) to the DB so the dashboard shows which
        instance is on which step and for how long. Best-effort — never breaks the bot."""
        if self.task_id:
            try: db.update_task_step(self.task_id, step)
            except Exception: pass
    def log(self,step,status,dur,details="",error=""):
        self.steps.append({"step":step,"status":status,"duration":round(dur,2),"details":details,"error":error})
        icon="✅" if status=="success" else "❌"
        print(f"   {icon} {step} ({dur:.1f}s) {details[:80]}")
        self.mark(step)   # also push the just-finished step to the DB (live progress)
    def save(self,status,ip,error=""):
        dur=(datetime.now()-self.start).total_seconds()
        with open(self.file,'w') as f:
            json.dump({"instance":INSTANCE_ID,"time":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                       "card":f"{self.card[:4]}...{self.card[-4:]}","email":self.email,"name":self.name_used,
                       "corp":self.corp,"emp":self.emp,"duration":round(dur,2),
                       "status":status,"proxy_ip":ip,"error":error,"steps":self.steps},f,indent=2)

# ================= SOCKS5 TUNNEL =================

class Socks5Tunnel:
    def __init__(self,host,port,user,pwd):
        self.host,self.port,self.user,self.pwd=host,port,user,pwd
        self.local_port,self.running=None,False
    def find_port(self):
        base=11000+(INSTANCE_ID*100)
        for p in range(base,base+100):
            s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            try: s.bind(('127.0.0.1',p));s.close();return p
            except: s.close()
        return None
    def connect_socks5(self):
        s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.settimeout(120)
        s.connect((self.host,self.port))
        s.send(b'\x05\x01\x02');s.recv(2)
        auth=b'\x01'+bytes([len(self.user)])+self.user.encode()+bytes([len(self.pwd)])+self.pwd.encode()
        s.send(auth)
        if s.recv(2)!=b'\x01\x00': raise Exception("Auth Failed")
        return s
    def handle(self,client):
        try:
            remote=self.connect_socks5()
            data=b""
            while b"\r\n\r\n" not in data:
                d=client.recv(4096)
                if not d: return
                data+=d
            req=data.decode('utf-8',errors='ignore')
            host,port=None,80
            if req.startswith('CONNECT'): host,port=req.split(' ')[1].split(':');port=int(port)
            else:
                for line in req.split('\r\n'):
                    if line.lower().startswith('host:'): host=line.split(':')[1].strip();break
                if not host: return
            remote.send(b'\x05\x01\x00\x03'+bytes([len(host)])+host.encode()+struct.pack('!H',port))
            remote.recv(10)
            client.send(b'HTTP/1.1 200 Connection Established\r\n\r\n')
            def forward(src,dst):
                try:
                    while True:
                        d=src.recv(8192)
                        if not d: break
                        dst.send(d)
                except: pass
                finally:
                    try: dst.close()
                    except: pass
            t1=threading.Thread(target=forward,args=(client,remote),daemon=True)
            t2=threading.Thread(target=forward,args=(remote,client),daemon=True)
            t1.start();t2.start()
            t1.join(300);t2.join(300)
        except: pass
        finally:
            try: client.close()
            except: pass
    def start(self):
        self.local_port=self.find_port()
        if not self.local_port: raise Exception("No free port")
        self.running=True
        s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        s.bind(('127.0.0.1',self.local_port))
        s.listen(5);s.settimeout(1)
        def accept():
            while self.running:
                try:
                    c,_=s.accept()
                    threading.Thread(target=self.handle,args=(c,),daemon=True).start()
                except socket.timeout: continue
                except: break
            s.close()
        threading.Thread(target=accept,daemon=True).start()
        return self.local_port
    def stop(self): self.running=False

# ================= HELPERS =================

def get_ip():
    try: return requests.get("https://api.ipify.org?format=json",timeout=30).json()["ip"]
    except: return "Unknown"

def get_proxy_ip(port):
    try:
        p={'http':f'http://127.0.0.1:{port}','https':f'http://127.0.0.1:{port}'}
        return requests.get("https://api.ipify.org?format=json",proxies=p,timeout=30).json()["ip"]
    except: return "Unknown"

def safe_goto(page,url):
    # First try a full domcontentloaded; on a slow/flaky proxy that can time out, so
    # later attempts fall back to "commit" (fires as soon as navigation commits) — the
    # time.sleep(5) after gives the page time to paint anyway. Cuts false "Navigation
    # failed" from a proxy hiccup.
    for a in range(1, RETRY_COUNT + 1):
        wait = "domcontentloaded" if a == 1 else "commit"
        try:
            page.goto(url, timeout=NAVIGATION_TIMEOUT, wait_until=wait)
            time.sleep(5)
            return True
        except Exception:
            time.sleep(a * 10)
    return False

def click_with_retry(page,selectors,step_name=""):
    if isinstance(selectors,str): selectors=[selectors]
    per = max(5000, ELEMENT_WAIT//RETRY_COUNT)
    for a in range(1,RETRY_COUNT+1):
        for sel in selectors:
            try:
                page.wait_for_selector(sel,timeout=per,state="visible")
                page.click(sel)
                return True
            except: pass
        print(f"   ⏳ [{step_name or 'click'}] round {a}/{RETRY_COUNT} waiting: {selectors}",flush=True)
        time.sleep(3)
    return False

def fill_with_retry(page,selectors,value,timeout=ELEMENT_WAIT//1000):
    if isinstance(selectors,str): selectors=[selectors]
    per = max(5000, (timeout*1000)//RETRY_COUNT)
    for a in range(1,RETRY_COUNT+1):
        for sel in selectors:
            try:
                page.wait_for_selector(sel,timeout=per,state="visible")
                page.fill(sel,value)
                return True
            except: pass
        print(f"   ⏳ [fill] round {a}/{RETRY_COUNT} waiting: {selectors}",flush=True)
        time.sleep(3)
    try:
        page.keyboard.press("Tab");time.sleep(1)
        page.keyboard.type(value,delay=100)
        return True
    except: return False

def type_with_retry(page, selectors, value, timeout=ELEMENT_WAIT // 1000):
    """Like fill_with_retry but TYPES the value with real keystrokes (keydown/keyup/
    input per char) instead of page.fill(). React/Vue forms enable their Continue/Submit
    button on real key events — page.fill() sets the value but often leaves the button
    DISABLED. So for the email/name fields we type, then fire input+change+blur, and
    verify the value actually landed. This is what drives 'Continue button stayed
    disabled' to ~0. Returns True if the value is present in the field afterwards."""
    if isinstance(selectors, str):
        selectors = [selectors]
    # Search the main page AND every iframe (some flows render the email/name input
    # inside an embedded frame, where page.locator() alone never finds it), within a
    # bounded total budget so a missing field can't hang the task. Re-dismiss popups each
    # pass — an overlay sitting on top of the field makes the click/type silently fail.
    deadline = time.time() + max(20, int(timeout))
    while time.time() < deadline:
        for ctx in [page] + list(page.frames):
            for sel in selectors:
                try:
                    loc = ctx.locator(sel).first
                    if not loc.count() or not loc.is_visible():
                        continue
                    try: loc.click(timeout=4000)             # focus (overlay may block it)
                    except Exception: pass
                    try: loc.fill("")                         # clear any partial value
                    except Exception: pass
                    # real keystrokes — press_sequentially (new PW) -> type -> fill fallback
                    try:
                        loc.press_sequentially(value, delay=35)
                    except Exception:
                        try: loc.type(value, delay=35)
                        except Exception: loc.fill(value)
                    # nudge framework validation: input+change+blur
                    try:
                        loc.evaluate("e => { e.dispatchEvent(new Event('input',{bubbles:true}));"
                                     " e.dispatchEvent(new Event('change',{bubbles:true})); e.blur(); }")
                    except Exception:
                        pass
                    if (loc.input_value() or "").strip():
                        return True
                except Exception:
                    pass
        try: dismiss_popups(page)
        except Exception: pass
        time.sleep(2)
    return False


def click_when_enabled(page, selectors, total_wait=30, step_name="click"):
    """Click the first selector that is visible AND ENABLED within total_wait seconds.
    Avoids the long hang on a disabled button (page.click() waits the full default
    timeout for a disabled <button>). Returns True if clicked, else False."""
    if isinstance(selectors, str): selectors = [selectors]
    deadline = time.time() + total_wait
    while time.time() < deadline:
        for sel in selectors:
            try:
                b = page.locator(sel).first
                if b.count() and b.is_visible() and b.is_enabled():
                    b.click(timeout=ELEMENT_WAIT)
                    return True
            except Exception:
                pass
        time.sleep(1)
    print(f"   ⚠️ [{step_name}] button never became enabled in {total_wait}s: {selectors}", flush=True)
    return False

def wait_for_any(page, selectors, timeout=20000):
    """True if any of the selectors becomes visible within timeout (ms)."""
    combined = ", ".join(selectors)
    try:
        page.wait_for_selector(combined, timeout=timeout, state="visible")
        return True
    except Exception:
        return False

# ================= OTP =================

def _extract_otp(data):
    """Find a 4-8 digit OTP anywhere in the API response (dict / list / str)."""
    if isinstance(data, dict):
        for k, v in data.items():
            kl = str(k).lower()
            if ("otp" in kl or "code" in kl) and isinstance(v, (str, int)):
                digits = re.sub(r"\D", "", str(v))
                if 4 <= len(digits) <= 8:
                    return digits
        for v in data.values():
            r = _extract_otp(v)
            if r:
                return r
    elif isinstance(data, list):
        for v in data:
            r = _extract_otp(v)
            if r:
                return r
    return None


def _otp_headers():
    # Callers reach the network only after the OTP_FETCH_TOKEN guard in get_otp,
    # so the token is always present here — send it on every request.
    return {"Accept": "application/json",
            "X-OTP-Token": OTP_FETCH_TOKEN,
            "Authorization": f"Bearer {OTP_FETCH_TOKEN}"}


def fetch_otp_once(emp_id, card_last_four=None):
    """No-op baseline snapshot. The OTP API CONSUMES the OTP on each successful
    fetch, so snapshotting would burn a real code. Kept (returns None) for caller
    compatibility; card_last_four is accepted for signature parity with get_otp."""
    return None


def get_otp(emp_id, prev_otp=None, max_polls=60, delay=4, card_last_four=None):
    """Poll the OTP API for the latest OTP (consume-on-fetch).

    The API CONSUMES the OTP on a 200 fetch — each code is returned only ONCE; a
    repeat call gives 404 until a fresh OTP arrives. So we poll until a 200 (that
    IS the fresh code) and return it.

    HTTP-code handling (script.py): 200=fresh/return, 404=wait, 401/503=give up,
    429=backoff. card_last_four matching (magzter_final): when the API returns a
    'card_last_four', prefer a 200 whose value matches card_no[-4:]; on mismatch,
    keep polling (the 200 belonged to a sibling card on the same employee).
    Returns the OTP string, 'manual' if no URL is set, or None on give-up."""
    emp_id_upper = emp_id.upper().strip()
    if not OTP_API_URL:
        print(f"\n   🔐 Enter OTP manually (Emp: {emp_id_upper})")
        input("   Press Enter...")
        return "manual"

    # SECURITY: the latest-otp API must NEVER be called without a token.
    # No token configured => refuse to fetch rather than hit the endpoint
    # unauthenticated (user requirement: "without token nahi chalegi").
    if not OTP_FETCH_TOKEN:
        print("   ❌ OTP_FETCH_TOKEN not set — refusing to fetch OTP without a token. "
              "Set it in Settings → Buy Subscriptions.", flush=True)
        return None

    url = OTP_API_URL.replace("{API_EMPLOYEE_ID}", emp_id_upper)
    headers = _otp_headers()
    want4 = str(card_last_four).strip() if card_last_four else ""
    print(f"   🔍 OTP for: {emp_id_upper}  →  {url}"
          + (f"  (card ****{want4})" if want4 else ""), flush=True)

    last_err = "Doe"
    for i in range(max_polls):
        try:
            resp = requests.get(url, headers=headers, timeout=20)
            sc = resp.status_code

            if sc == 200:
                try:
                    data = resp.json()
                    otp = _extract_otp(data)
                    if otp:
                        c4 = str(data.get("card_last_four", "")).strip() if isinstance(data, dict) else ""
                        # card_last_four matching: skip a 200 meant for another card.
                        if want4 and c4 and c4 != want4:
                            if i % 5 == 0:
                                print(f"   ⏳ OTP card mismatch (API ****{c4} ≠ task ****{want4}) — waiting…", flush=True)
                            time.sleep(delay); continue
                        print(f"   ✅ OTP: {otp}  (card ****{c4})", flush=True)
                        return otp
                except ValueError:
                    digits = re.sub(r"\D", "", resp.text)
                    if 4 <= len(digits) <= 8:
                        print(f"   ✅ OTP: {digits}", flush=True)
                        return digits
                time.sleep(delay); continue

            if sc == 404:                       # no fresh OTP yet — keep waiting
                if i % 10 == 0:
                    print("   ⏳ No pending OTP yet (404) — waiting…", flush=True)
                time.sleep(delay); continue

            if sc == 401:
                print("   ❌ OTP token invalid/missing (401) — set OTP_FETCH_TOKEN in config", flush=True)
                return None
            if sc == 503:
                print("   ❌ OTP token not configured on the OTP server (503)", flush=True)
                return None
            if sc == 429:                       # rate limited (30/min) — back off
                print("   ⚠️ OTP API rate-limited (429) — backing off", flush=True)
                time.sleep(max(delay, 6)); continue

            if i % 10 == 0:
                print(f"   ⚠️ OTP API HTTP {sc}: {resp.text[:150]}", flush=True)
            time.sleep(delay)
        except Exception as e:
            msg = str(e)[:120]
            if msg != last_err:
                print(f"   ⚠️ OTP fetch error: {msg}", flush=True)
                last_err = msg
            time.sleep(delay)

    print("   ❌ OTP not received (no matching 200 in the poll window)", flush=True)
    return None

# Specific OTP-ish selectors first, then broader. The broad ones (inputmode/tel/
# maxlength) ALSO match payment fields like #cardNumber, so find_otp_field filters
# those out by attribute + skips disabled inputs.
OTP_DETECT = ['input[autocomplete="one-time-code"]','input[name="otp"]','#otp',
              'input[name="otpValue"]','input[name*="otp" i]','input[id*="otp" i]',
              'input[placeholder*="otp" i]','input[aria-label*="otp" i]',
              'input[placeholder*="code" i]','input[aria-label*="code" i]',
              'input[inputmode="numeric"]','input[type="tel"]','input[maxlength="1"]']
SUBMIT_BTN = ['button[type="submit"]','button#submitBtn','button.verify_btn','button.submit']

# How many times to (re)send + re-enter an OTP before giving up on a card.
MAX_OTP_ATTEMPTS = 3

# "Resend OTP" / "Send again" buttons/links on the OTP screen.
RESEND_BTN = [
    'button:has-text("Resend OTP")','a:has-text("Resend OTP")',
    'button:has-text("Resend Code")','a:has-text("Resend Code")',
    'button:has-text("Resend")','a:has-text("Resend")',
    'button:has-text("Send again")','a:has-text("Send again")',
    'button:has-text("Send OTP")','a:has-text("Send OTP")',
    '[id*="resend" i]','[class*="resend" i]','[aria-label*="resend" i]',
]

# OTP-screen errors that ARE fixable by resending a fresh code.
OTP_INVALID_MSGS = [
    "invalid otp","incorrect otp","otp is invalid","wrong otp","otp did not match",
    "otp does not match","otp expired","otp has expired","invalid verification code",
    "incorrect code","invalid code","code is incorrect","code did not match",
    "code has expired","please try again","try again",
]

def click_resend(page):
    """Click a 'Resend OTP' button/link on the page or any iframe. Returns True if clicked."""
    for ctx in [page] + list(page.frames):
        for sel in RESEND_BTN:
            try:
                loc = ctx.locator(sel).first
                if loc.is_visible():
                    loc.click(timeout=5000)
                    print(f"   🔁 Resend clicked ({sel})", flush=True)
                    return True
            except Exception:
                pass
    print("   ⚠️ Resend button not found on page", flush=True)
    return False

# Fields that look numeric but are NOT the OTP (payment / personal).
OTP_EXCLUDE = ("card","cvc","cvv","expiry","exp","zip","postal","email","name","billing","address","phone","mobile")

def find_otp_field(page, selectors=None):
    """Return (ctx, locator) for a real, enabled OTP input. Skips disabled fields
    and payment/personal fields (cardNumber also has inputmode=numeric)."""
    if selectors is None: selectors = OTP_DETECT
    for ctx in [page] + list(page.frames):
        for sel in selectors:
            try:
                loc = ctx.locator(sel)
                cnt = min(loc.count(), 6)
            except Exception:
                continue
            for i in range(cnt):
                el = loc.nth(i)
                try:
                    if not el.is_visible() or not el.is_enabled():
                        continue
                    attrs = ((el.get_attribute("id") or "") + " " +
                             (el.get_attribute("name") or "") + " " +
                             (el.get_attribute("aria-label") or "") + " " +
                             (el.get_attribute("placeholder") or "")).lower()
                    if any(x in attrs for x in OTP_EXCLUDE):
                        continue
                    return ctx, el
                except Exception:
                    continue
    return None, None

# ================= PAGE ERROR DETECTION =================
DECLINE_MSGS = [
    "card has been declined","card was declined","your card was declined","card declined",
    "declined","insufficient funds","do not honor","incorrect card number","invalid card",
    "card number is incorrect","payment failed","transaction declined","incorrect cvc",
    "security code is incorrect","expired card","card does not support","unable to process payment",
]
ELIGIBILITY_MSGS = [
    "not eligible","you are not eligible","ineligible","not valid for this offer",
    "already redeemed","already subscribed","already been used","already claimed",
    "offer has expired","offer expired","limit reached","not available in your",
    "offer is no longer","not qualify","offer not available","existing subscriber",
    # existing-GOLD-user offer block (Billing Details, before Stripe) — was misread as
    # "Stripe payment form not loaded" so email mutation never fired.
    "not applicable for existing","existing gold","gold user","gold member",
    "offer is not applicable","not applicable for this offer",
]

def page_has_error(page, phrases):
    """Return the first matching error phrase found on the page or any iframe, else None."""
    blob = ""
    for ctx in [page] + list(page.frames):
        try:
            blob += " " + ctx.locator('body').inner_text(timeout=5000).lower()
        except Exception:
            pass
    for p in phrases:
        if p in blob:
            return p
    return None

# Close interrupting popups. The CleverTap "Get Updates" popup (wzrk-*) is removed
# in-browser by the init script; keep this list to clickable, non-animating closers.
# Merged with aws's POPUP_CLOSE (wzrk-cancel / Not Now / aria-label Close variants)
# so they can ALSO be registered as add_locator_handler dismissers.
POPUP_CLOSE = [
    '#wzrk-cancel', 'button[aria-label="Not Now"]',
    'button:has-text("Not Now")', 'button.close-btn', 'img[alt="Close"]',
    '[aria-label="Close"]', '[aria-label="close"]', 'button:has-text("No thanks")',
    '.close_icon_id_banner', '#accept-cookie .agree_btn',
]

def dismiss_popups(page):
    for ctx in [page] + list(page.frames):
        for sel in POPUP_CLOSE:
            try:
                loc = ctx.locator(sel).first
                if loc.count() and loc.is_visible():
                    loc.click(timeout=1500, force=True, no_wait_after=True)
            except Exception:
                pass

# ================= CORPORATE FORM SELECTORS (fuzzy, from aws) =================

CORP_ID_SELS = [
    '#corporateId', 'input[name="corporateId"]', 'input[id*="corporate" i]',
    'input[name*="corporate" i]', 'input[placeholder*="corporate" i]',
    'input[placeholder*="company" i]',
]
EMP_ID_SELS = [
    '#employeeId', 'input[name="employeeId"]', 'input[id*="employee" i]',
    'input[name*="employee" i]', 'input[placeholder*="employee" i]',
]

# ================= hCAPTCHA (2captcha) =================

def _find_hcaptcha_sitekey(page):
    """Return the hCaptcha sitekey if a captcha is present on the page/any frame, else None."""
    for ctx in [page] + list(page.frames):
        try:
            sk = ctx.evaluate("""() => {
                const el = document.querySelector('.h-captcha[data-sitekey], [data-hcaptcha-sitekey], [data-sitekey]');
                if (el) return el.getAttribute('data-sitekey') || el.getAttribute('data-hcaptcha-sitekey');
                return null;
            }""")
            if sk:
                return sk
        except Exception:
            pass
    for fr in page.frames:
        try:
            u = fr.url or ""
            if "hcaptcha.com" in u:
                m = re.search(r"sitekey=([0-9a-fA-F\-]+)", u)
                if m:
                    return m.group(1)
        except Exception:
            pass
    return None


def _hcaptcha_present(page):
    """True if an hCaptcha widget/iframe is on the page or any frame — even when its
    sitekey couldn't be parsed. Lets us fall back to a configured sitekey only when a
    captcha really IS there (so we never waste solver credits on a captcha-free page)."""
    for fr in page.frames:
        try:
            if "hcaptcha.com" in (fr.url or ""):
                return True
        except Exception:
            pass
    for ctx in [page] + list(page.frames):
        try:
            if ctx.locator('.h-captcha, iframe[src*="hcaptcha"], [data-hcaptcha-widget-id]').first.count():
                return True
        except Exception:
            pass
    return False


def _solver_proxy():
    """The SAME upstream India proxy our browser uses, as solver-friendly parts (or None).
    Passing this + the browser User-Agent to the solver makes the solved token's IP/UA
    match our submitting browser — hCaptcha rejects tokens solved from a different IP/UA
    (Gemini's points 2 & 3, the 80% cause). geonode is SOCKS5."""
    if PROXY_HOST and PROXY_PORT and PROXY_USERNAME:
        return {"type": "socks5", "host": str(PROXY_HOST), "port": int(PROXY_PORT),
                "user": str(PROXY_USERNAME), "pass": str(PROXY_PASSWORD or "")}
    return None


def _token_2captcha(sitekey, pageurl, api_key, timeout=CAPTCHA_TIMEOUT, user_agent=None, proxy=None):
    """Get an hCaptcha token from 2captcha (in.php/res.php). Returns token or None;
    prints the real reason (e.g. ZERO_BALANCE, WRONG_USER_KEY) on failure. Passes the
    browser User-Agent + our proxy so the token's IP/UA match the submitting browser."""
    data = {"key": api_key, "method": "hcaptcha", "sitekey": sitekey,
            "pageurl": pageurl, "json": 1}
    if user_agent:
        data["userAgent"] = user_agent
    if proxy:
        data["proxy"] = f'{proxy["user"]}:{proxy["pass"]}@{proxy["host"]}:{proxy["port"]}'
        data["proxytype"] = proxy["type"].upper()
    try:
        r = requests.post("https://2captcha.com/in.php", data=data, timeout=30).json()
    except Exception as e:
        print(f"   ⚠️ 2captcha submit failed: {str(e)[:100]}", flush=True)
        return None
    if str(r.get("status")) != "1":
        # Surface the exact reason — ERROR_ZERO_BALANCE / ERROR_WRONG_USER_KEY etc.
        print(f"   ❌ 2captcha rejected: {r.get('request')}", flush=True)
        return None
    cid = r["request"]
    for _ in range(max(1, timeout // 5)):
        time.sleep(5)
        try:
            res = requests.get("https://2captcha.com/res.php", params={
                "key": api_key, "action": "get", "id": cid, "json": 1}, timeout=30).json()
        except Exception:
            continue
        if str(res.get("status")) == "1":
            return res["request"]
        if res.get("request") != "CAPCHA_NOT_READY":
            print(f"   ❌ 2captcha error: {res.get('request')}", flush=True)
            return None
    print("   ❌ 2captcha not solved in time", flush=True)
    return None


def _token_capsolver(sitekey, pageurl, api_key, timeout=CAPTCHA_TIMEOUT, user_agent=None, proxy=None):
    """Get an hCaptcha token from CapSolver (createTask/getTaskResult). Often more
    reliable on hard hCaptcha. Passes browser User-Agent + our proxy (HCaptchaTask) so the
    token's IP/UA match the submitting browser. Returns token or None."""
    task = {"type": "HCaptchaTaskProxyless", "websiteURL": pageurl, "websiteKey": sitekey}
    if user_agent:
        task["userAgent"] = user_agent
    if proxy:
        # Separate proxy fields are more reliable than the single "proxy" string — a bad
        # parse makes CapSolver silently fall back to Proxyless => IP mismatch => token
        # rejected (the loop you saw).
        task["type"] = "HCaptchaTask"
        task["proxyType"] = proxy["type"].lower()      # 'socks5' / 'http'
        task["proxyAddress"] = proxy["host"]
        task["proxyPort"] = int(proxy["port"])
        task["proxyLogin"] = proxy["user"]
        task["proxyPassword"] = proxy["pass"]
    try:
        resp = requests.post("https://api.capsolver.com/createTask", json={
            "clientKey": api_key, "task": task}, timeout=30).json()
    except Exception as e:
        print(f"   ⚠️ capsolver createTask failed: {str(e)[:100]}", flush=True)
        return None
    if resp.get("errorId"):
        print(f"   ❌ capsolver rejected: {resp.get('errorCode')} {resp.get('errorDescription','')}", flush=True)
        return None
    task_id = resp.get("taskId")
    if not task_id:
        print(f"   ❌ capsolver no taskId: {resp}", flush=True)
        return None
    for _ in range(max(1, timeout // 3)):
        time.sleep(3)
        try:
            res = requests.post("https://api.capsolver.com/getTaskResult", json={
                "clientKey": api_key, "taskId": task_id}, timeout=30).json()
        except Exception:
            continue
        if res.get("errorId"):
            print(f"   ❌ capsolver error: {res.get('errorCode')} {res.get('errorDescription','')}", flush=True)
            return None
        if res.get("status") == "ready":
            return (res.get("solution") or {}).get("gRecaptchaResponse")
    print("   ❌ capsolver not solved in time", flush=True)
    return None


# JS that injects the solved token EVERYWHERE hCaptcha/reCAPTCHA reads it, on the page
# and every frame, then fires the widget's success callback so the form actually accepts
# it (a bare value set is often ignored until the callback runs).
_HCAPTCHA_INJECT_JS = r"""(tok) => {
  try {
    document.querySelectorAll(
      '[name="h-captcha-response"],[name="g-recaptcha-response"],'
      + 'textarea#h-captcha-response,textarea#g-recaptcha-response,iframe[data-hcaptcha-response]'
    ).forEach(t => {
      try { t.value = tok; } catch(e){}
      try { t.innerHTML = tok; } catch(e){}
      try { t.dispatchEvent(new Event('input', {bubbles:true})); } catch(e){}
      try { t.dispatchEvent(new Event('change', {bubbles:true})); } catch(e){}
    });
  } catch(e){}
  // Fire any data-callback / hcaptcha onSuccess / common callback names.
  try {
    const names = ['hcaptchaCallback','onHcaptchaSuccess','onSuccessCallback','captchaCallback','onVerify'];
    names.forEach(n => { try { if (typeof window[n] === 'function') window[n](tok); } catch(e){} });
    document.querySelectorAll('[data-callback]').forEach(el => {
      try { const fn = el.getAttribute('data-callback'); if (fn && typeof window[fn] === 'function') window[fn](tok); } catch(e){}
    });
    if (window.hcaptcha && window._hcaptchaCb) window._hcaptchaCb(tok);
  } catch(e){}
}"""


def _solve_hcaptcha_paid(page, api_key, timeout, sitekey):
    """OLD paid-solver path (2captcha/capsolver) — only used if CAPTCHA_CLICK_ONLY is off."""
    if not sitekey:
        if HCAPTCHA_SITEKEY and _hcaptcha_present(page):
            sitekey = HCAPTCHA_SITEKEY
        else:
            return "none"
    provider = CAPTCHA_PROVIDER
    key = api_key or (CAPSOLVER_API_KEY if provider == "capsolver" else CAPTCHA_API_KEY)
    if not key:
        print("   ⚠️ hCaptcha present but no captcha API key set", flush=True)
        return False
    pageurl = page.url
    try: ua = page.evaluate("() => navigator.userAgent")
    except Exception: ua = None
    proxy = _solver_proxy()
    print(f"   🧩 hCaptcha — solving via {provider}", flush=True)
    if provider == "capsolver":
        token = _token_capsolver(sitekey, pageurl, key, timeout, user_agent=ua, proxy=proxy)
    else:
        token = _token_2captcha(sitekey, pageurl, key, timeout, user_agent=ua, proxy=proxy)
    if not token:
        return False
    for ctx in [page] + list(page.frames):
        try: ctx.evaluate(_HCAPTCHA_INJECT_JS, token)
        except Exception: pass
    print("   ✅ hCaptcha solved + token injected", flush=True)
    return True


def solve_hcaptcha(page, api_key=None, timeout=CAPTCHA_TIMEOUT):
    """No paid solver (default): CLICK the hCaptcha "I am human" checkbox. With patchright
    stealth + a clean residential proxy, hCaptcha often passes the checkbox with NO image
    challenge. Returns True if it passes, False if it throws an (unsolvable) image challenge
    or times out, 'none' when there's no captcha. CAPTCHA_CLICK_ONLY=false → paid solver."""
    sitekey = _find_hcaptcha_sitekey(page)
    if not sitekey and not _hcaptcha_present(page):
        return "none"
    if not CAPTCHA_CLICK_ONLY:
        return _solve_hcaptcha_paid(page, api_key, timeout, sitekey)
    # --- checkbox-click path (no solver) -------------------------------------------------
    # If a token is ALREADY present (e.g. the corp-wait loop already passed this hCaptcha),
    # do NOT click again. Re-clicking a passed hCaptcha flips it into challenge mode and
    # invalidates the token — that's exactly what broke the corp SUBMIT (→ no OTP). Reuse it.
    def _token_present():
        for ctx in [page] + list(page.frames):
            try:
                n = ctx.evaluate("() => {const t=document.querySelector('textarea[name=\"h-captcha-response\"],textarea[name=\"g-recaptcha-response\"]'); return t && t.value ? t.value.length : 0;}")
                if n and n > 20:
                    return True
            except Exception:
                pass
        return False
    if _token_present():
        print("   ✅ hCaptcha already passed (token present) — reusing, no re-click", flush=True)
        return True
    # Only act when an hCaptcha checkbox iframe is ACTUALLY VISIBLE (rendered on screen).
    # A present-but-hidden / invisible-passive widget must NOT be clicked — skip it so we
    # don't waste a wait/click when no captcha actually appeared.
    def _hcaptcha_iframe_visible():
        for ctx in [page] + list(page.frames):
            try:
                for sel in ['iframe[src*="hcaptcha.com"]', 'iframe[title*="hCaptcha" i]',
                            'iframe[title*="human" i]']:
                    loc = ctx.locator(sel)
                    for i in range(min(loc.count(), 4)):
                        el = loc.nth(i)
                        try:
                            if "challenge" in (el.get_attribute("src") or ""):
                                continue
                            if el.is_visible():
                                return True
                        except Exception:
                            pass
            except Exception:
                pass
        return False
    if not _hcaptcha_iframe_visible():
        print("   ⏭️ hCaptcha frame not visible — skipping (no captcha to act on)", flush=True)
        return "none"
    print("   🖱️ hCaptcha — clicking 'I am human' (no solver)", flush=True)
    for fr in list(page.frames):
        u = (fr.url or "")
        if "hcaptcha.com" in u and "frame=challenge" not in u:   # the checkbox/anchor frame
            for sel in ['#checkbox', 'div[role="checkbox"]', '#anchor', '.check']:
                try:
                    el = fr.locator(sel).first
                    if el.count() and el.is_visible():
                        el.click(timeout=5000)
                        print("   🖱️ checkbox clicked", flush=True)
                        break
                except Exception:
                    pass
            break
    # wait for PASS (response token populated) OR CHALLENGE (image puzzle → can't solve)
    deadline = time.time() + min(20, max(8, timeout))
    while time.time() < deadline:
        if _token_present():
            print("   ✅ hCaptcha passed via checkbox", flush=True)
            return True
        for fr in list(page.frames):
            if "frame=challenge" in (fr.url or ""):
                print("   ❌ hCaptcha threw an image challenge — no solver, failing fast", flush=True)
                return False
        time.sleep(1)
    print("   ❌ hCaptcha checkbox didn't pass in time — failing", flush=True)
    return False


# ================= LOGIN-BASED PURCHASE VERIFICATION =================

def verify_via_login(context, email, name, password=None):
    """Definitive purchase check: the Magzter Gold success page itself says "Sign in/Sign
    up" — the purchase does NOT log you in — so there's no session to read my_orders from.
    Instead LOG IN with the same email in a fresh tab (a freshly-bought email hits the
    "Create Account" form where we SET the password; an existing one → password login),
    then read the Transaction ID from my_orders. The account's order history is the real
    proof. Returns the Transaction ID string, or None. Used when the thank-you page didn't
    show (it often fails to load after payment)."""
    password = password or VERIFY_LOGIN_PASSWORD
    if not password:
        print("   ⚠️ VERIFY_LOGIN_PASSWORD not set — can't login-verify", flush=True)
        return None
    EMAIL_SELS = ['#email', 'input[type="email"]', 'input[name="email"]', '#login_email']
    PASS_SELS  = ['#user-pass', '#pass', 'input[name="pass"]', 'input[name="password"]', 'input[type="password"]']
    STEP2 = '#user-pass, #pass, input[type="password"], #create-account-form, #filterCountry'
    vp = None
    _vdeadline = time.time() + 70      # hard cap — never let verification hang the instance
    try:
        vp = context.new_page()
        try: vp.set_default_timeout(12000)        # snappy per-action timeout (proxy is slow)
        except Exception: pass
        vp.goto("https://www.magzter.com/login/email", wait_until="domcontentloaded", timeout=35000)
        try: vp.wait_for_selector(", ".join(EMAIL_SELS), state="visible", timeout=15000)
        except Exception: pass
        time.sleep(1)
        try: dismiss_popups(vp)
        except Exception: pass
        # STEP 1 — email
        for s in EMAIL_SELS:
            try:
                el = vp.locator(s).first
                if el.count() and el.is_visible(): el.fill(email); break
            except Exception: pass
        time.sleep(0.8)
        # STEP 2 — reveal the password / create-account form (up to 2 Continue tries)
        for _ in range(2):
            try:
                if vp.locator(STEP2).first.is_visible(): break
            except Exception: pass
            if time.time() > _vdeadline: return None
            for c in ['#continue_btn', 'button:has-text("Continue")', 'button[type="submit"]']:
                try:
                    b = vp.locator(c).first
                    if b.is_visible(timeout=2000): b.click(timeout=5000); break
                except Exception: pass
            try: vp.wait_for_selector(STEP2, state="visible", timeout=12000)
            except Exception: pass
            try: dismiss_popups(vp)
            except Exception: pass
        # Create-Account form? → fill name + India
        try:
            if vp.locator('#create-account-form, #filterCountry').first.is_visible():
                for s in ['#inp_box', 'input[name="name"]']:
                    try:
                        el = vp.locator(s).first
                        if el.count() and el.is_visible(): el.fill((name or "User").strip() or "User"); break
                    except Exception: pass
                try:
                    cc = vp.locator('#filterCountry').first
                    if cc.is_visible(timeout=2000): cc.select_option('India')
                except Exception: pass
        except Exception: pass
        # password
        for s in PASS_SELS:
            try:
                el = vp.locator(s).first
                if el.count() and el.is_visible(): el.fill(password); break
            except Exception: pass
        time.sleep(0.5)
        for c in ['#continue_btn', 'button:has-text("Create Account")', 'button:has-text("Continue")',
                  'button:has-text("Login")', 'button[type="submit"]']:
            try:
                b = vp.locator(c).first
                if b.is_visible(timeout=2000): b.click(timeout=5000); break
            except Exception: pass
        time.sleep(4)
        if time.time() > _vdeadline: return None
        # my_orders → Transaction ID
        op = context.new_page()
        try: op.set_default_timeout(12000)
        except Exception: pass
        try:
            op.goto("https://www.magzter.com/dashboard/my_orders", wait_until="domcontentloaded", timeout=30000)
            op.wait_for_timeout(2500)
            try: dismiss_popups(op)
            except Exception: pass
            txn = None
            try:
                op.wait_for_selector('td[data-title="Transaction ID"]', timeout=15000)
                txn = (op.inner_text('td[data-title="Transaction ID"]') or "").strip()
            except Exception:
                try:
                    _b = (op.locator('body').inner_text(timeout=4000) or "")[:120].replace("\n", " ")
                    print(f"   🔎 my_orders: no txn — url={op.url[:55]} | {_b!r}", flush=True)
                except Exception: pass
            return txn or None
        finally:
            try: op.close()
            except Exception: pass
    except Exception as e:
        print(f"   ⚠️ verify_via_login error: {str(e)[:120]}", flush=True)
        return None
    finally:
        try:
            if vp: vp.close()
        except Exception: pass


# ================= SINGLE TASK =================

def run_task(task, proxy_port, proxy_ip):
    card_no = task['card_no']; expiry = task['month']; cvv = task['cvv']
    # use the mutated email if this row was re-queued by email-mutation, else the original;
    # sanitize so a messy/invalid sheet email is corrected before use (never pass garbage)
    _raw_email = (task.get('updated_email') or task['email'])
    email = db.sanitize_email(_raw_email) or _raw_email; corp_id = task['corp_id']; emp_id = task['emp_id']
    first_name = task['first_name']; last_name = task['last_name']
    row = task['row']; task_id = task['task_id']

    name_used = f"{first_name} {last_name}"
    local = LocalLogger(card_no, email, corp_id, emp_id, task_id=task_id)
    local.set_name(name_used)

    print(f"\n{'='*60}")
    print(f"🎯 Row {row}: {card_no[:4]}...{card_no[-4:]}")
    print(f"   👤 {name_used} | 📧 {email}")
    print(f"   🏢 {corp_id} | 👔 {emp_id}")
    print(f"   🌍 {proxy_ip}")

    # Already 'running' in DB from the claim; record the proxy IP for writeback.
    db.update_task(task_id, db.ST_RUNNING, proxy_ip=proxy_ip)

    pw = browser = context = page = None
    status = "FAILED"; error_msg = ""; _txn_id = None
    start_time = datetime.now()

    try:
        t0 = time.time()
        pw = sync_playwright().start()

        res = random.choice([{'w':1366,'h':768},{'w':1440,'h':900},{'w':1536,'h':864}])

        # Robust launch (from aws): retry up to 5x, restarting playwright between
        # tries, so a transient chromium launch failure doesn't kill the task.
        _launch_args = [
            '--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu',
            f'--window-size={res["w"]},{res["h"]}',
            '--disable-blink-features=AutomationControlled', '--disable-infobars',
            '--disable-setuid-sandbox', '--disable-features=site-per-process',
            '--memory-pressure-off', '--disable-background-timer-throttling',
        ]
        browser = None
        for _bl_try in range(5):
            try:
                browser = pw.chromium.launch(headless=HEADLESS, args=_launch_args)
                break
            except Exception as _bl_e:
                _bl_msg = str(_bl_e)[:120]
                print(f'   ⚠️ Browser launch failed (attempt {_bl_try+1}/5): {_bl_msg} → retrying in 15s', flush=True)
                try:
                    if pw: pw.stop()
                except Exception: pass
                time.sleep(15)
                try:
                    pw = sync_playwright().start()
                except Exception: pass
                if _bl_try == 4:
                    raise
        # GoLogin-style fingerprint — one CONSISTENT spoofed device per account (seeded by
        # the email, so a re-run of the same account looks like the same machine, not a new
        # one). Spoofs UA + client-hints + navigator + screen + WebGL/canvas/audio + WebRTC.
        # Locale/timezone match the India proxy exit.
        fp = Fingerprint(seed=email, locale="en-IN", timezone_id="Asia/Kolkata")
        context = browser.new_context(
            **fp.context_kwargs(proxy_server=f"http://127.0.0.1:{proxy_port}")
        )
        context.add_init_script(fp.init_script())

        # KILL the CleverTap "Get Updates" web-push popup before the site's scripts run.
        context.add_init_script("""
(function(){
  try {
    Object.defineProperty(window, 'clevertap', {
      configurable:true,
      get:function(){ return this.__ct; },
      set:function(nv){
        try {
          if (nv) {
            nv.notifications = nv.notifications || {};
            nv.notifications.push = function(){};   // swallow the "Get Updates" opt-in
          }
        } catch(e){}
        this.__ct = nv;
      }
    });
  } catch(e){}
  try { if (window.Notification) { Notification.requestPermission = function(cb){ if(cb) cb('denied'); return Promise.resolve('denied'); }; } } catch(e){}
  function rm(){
    try {
      var sel='.wzrk-alert,.wzrk-overlay,.wzrk-backdrop,[id^="wzrk"],[class*="wzrk"]';
      document.querySelectorAll(sel).forEach(function(el){ el.remove(); });
    } catch(e){}
  }
  try { new MutationObserver(rm).observe(document.documentElement||document,{childList:true,subtree:true}); } catch(e){}
  document.addEventListener('DOMContentLoaded', rm);
  setInterval(rm, 800);
})();
""")
        page = context.new_page()
        page.set_default_timeout(GLOBAL_TIMEOUT)

        # Auto-dismiss popups (from aws): register a named handler (not a lambda) per
        # POPUP_CLOSE selector with force=True so a detached/unstable element can't
        # crash the handler and block the page. This catches the "Get Updates" popup
        # on ANY page, not just where dismiss_popups() is called manually.
        def _make_popup_handler(s):
            def _h(loc=None):
                try:
                    page.locator(s).first.click(force=True, timeout=3000)
                except Exception:
                    pass
            return _h
        for _sel in POPUP_CLOSE:
            _handler = _make_popup_handler(_sel)
            try:
                page.add_locator_handler(page.locator(_sel), _handler, no_wait_after=True)
            except TypeError:
                try: page.add_locator_handler(page.locator(_sel), _handler)
                except Exception: pass
            except Exception:
                pass

        local.log("INIT","success",time.time()-t0)

        # NAVIGATE
        t0=time.time()
        if not safe_goto(page,TARGET_URL): raise Exception("Navigation failed")
        local.log("NAVIGATE","success",time.time()-t0)
        time.sleep(random.uniform(3,5))
        dismiss_popups(page)

        # CLAIM
        t0=time.time()
        if not click_with_retry(page,['button:has-text("Claim Now")','button.yellow_btn','a.subscribe_a button']):
            raise Exception("Claim button not found")
        local.log("CLAIM","success",time.time()-t0)
        time.sleep(random.uniform(3,5))
        dismiss_popups(page)

        # ── EMAIL + ELIGIBILITY (in-session mutation retry) ──────────────────────
        # navigate+claim done above (ONCE). Enter email -> eligibility. On 'not eligible'
        # (account exists) pick a RANDOM mutated email and re-enter it on the SAME page
        # (no re-navigate) until eligible or mutations run out.
        _orig_email = email
        _tried = {email}
        while True:
            try:
                # EMAIL — type the address, then make Continue ENABLE the way the page itself
                # does it. The "Verify your Email Address" page keeps #continueBtn DISABLED until
                # Google reCAPTCHA v3 runs (generateCaptcha(): grecaptcha.execute() -> fill
                # #captchaInput -> removeAttribute('disabled')). So the button is NOT gated on the
                # email input at all — it's gated on the captcha token. We therefore: type the
                # email, WAIT for reCAPTCHA (slow via proxy) and actively (re)trigger
                # generateCaptcha() in case onReCaptchaLoad never fired, then click. This is the
                # real fix that drives "Continue button stayed disabled" to ~0.
                t0=time.time()
                email_sel = ['#verify_email_input','input[type="email"]','input[name="email"]',
                             '#email','input[placeholder*="mail" i]','input[type="text"]']

                def _email_landed():
                    for s in email_sel:
                        try:
                            el = page.locator(s).first
                            if el.count() and el.is_visible() and (el.input_value() or "").strip():
                                return True
                        except Exception:
                            pass
                    return False

                if not type_with_retry(page, email_sel, email):
                    # Dump WHY it failed: the URL we're on + every input the page exposes (across
                    # frames). Tells "wrong page" (login redirect / eligibility) apart from
                    # "field in an iframe we didn't reach" vs "overlay covering it".
                    try:
                        _inputs = page.eval_on_selector_all('input',
                            "els=>els.map(e=>({name:e.name,id:e.id,type:e.type,ph:e.placeholder,vis:e.offsetParent!==null})).slice(0,20)")
                        print(f"   🔎 Email field not fillable — url={page.url[:90]} | frames={len(page.frames)} | inputs={_inputs}", flush=True)
                    except Exception: pass
                    try: page.screenshot(path=os.path.join(SCREENSHOT_DIR, "EMAILFILL_FAIL_"+email_to_filename(email)))
                    except Exception: pass
                    raise Exception("Email field not fillable")
                for _ in range(4):
                    if _email_landed():
                        break
                    dismiss_popups(page)
                    try: type_with_retry(page, email_sel, email)
                    except Exception: pass
                    time.sleep(1)

                # Wait for reCAPTCHA to enable Continue. Poll up to ~45s (proxy makes the Google
                # reCAPTCHA script load slowly); every few seconds re-trigger generateCaptcha() so
                # a missed onReCaptchaLoad doesn't leave the button disabled forever.
                clicked = False
                # Give reCAPTCHA ~18s to enable Continue normally (keep it SHORT so the
                # server-rendered captcha token below is still fresh if we have to force it).
                for i in range(18):
                    dismiss_popups(page)
                    if i == 2 or (i % 6 == 0 and i > 0):
                        try:
                            page.evaluate("() => { try { if (typeof generateCaptcha === 'function')"
                                          " generateCaptcha(); } catch(e){} }")
                        except Exception:
                            pass
                    for cs in ['#continueBtn','button:has-text("Continue")','button.continue_btn']:
                        try:
                            b = page.locator(cs).first
                            if b.count() and b.is_visible() and b.is_enabled():
                                b.click(timeout=ELEMENT_WAIT); clicked = True; break
                        except Exception:
                            pass
                    if clicked:
                        break
                    time.sleep(1)

                if not clicked:
                    # reCAPTCHA never enabled the button — Google's script is usually blocked/slow
                    # through the India proxy. But the page already carries a SERVER-RENDERED
                    # captcha token (#captchaInput value=...), so we FORCE-enable the button and
                    # submit verify_form ourselves; that token goes through. This is the real fix
                    # for "Continue button stayed disabled" when grecaptcha won't run.
                    try:
                        gre = page.evaluate("() => (typeof grecaptcha !== 'undefined')")
                        print(f"   🔧 Continue disabled — grecaptcha loaded={gre}; force-enabling + submitting form", flush=True)
                    except Exception:
                        pass
                    try:
                        page.evaluate("""() => {
                            try { const b=document.getElementById('continueBtn');
                                  if(b){ b.removeAttribute('disabled'); b.disabled=false; } } catch(e){}
                        }""")
                    except Exception:
                        pass
                    _before = page.url
                    for cs in ['#continueBtn','button:has-text("Continue")','button.continue_btn']:
                        try:
                            b = page.locator(cs).first
                            if b.count() and b.is_visible():
                                b.click(timeout=8000, force=True); break
                        except Exception:
                            pass
                    time.sleep(3)
                    # still on the same page? submit the verify form directly with its token.
                    if page.url == _before:
                        try:
                            page.evaluate("""() => {
                                try {
                                    const f = document.forms['verify_form']
                                           || document.querySelector('form.verify_form, form[action*="verify"], form');
                                    if (f) { f.requestSubmit ? f.requestSubmit() : f.submit(); }
                                } catch(e){}
                            }""")
                            time.sleep(4)
                        except Exception:
                            pass
                    if page.url != _before:
                        clicked = True
                        print("   ✅ Continue forced through (server-rendered captcha token)", flush=True)

                if not clicked:
                    try: page.screenshot(path=os.path.join(SCREENSHOT_DIR, "EMAILDEBUG_"+email_to_filename(email)))
                    except Exception: pass
                    raise Exception("Continue button stayed disabled (email not accepted)")

                local.log("EMAIL","success",time.time()-t0,email)
                time.sleep(random.uniform(4,6))
                dismiss_popups(page)

                # ── LOGIN/VERIFY INTERSTITIAL (ported from aws) ──────────────────────────
                # After the EMAIL continue some accounts land on a /login/verify, /login/email
                # or /signin interstitial. Click Continue/Skip; retry up to 3x; if still stuck
                # on /login/verify, this account needs email-OTP — not eligible.
                try:
                    _is_login_url = any(kw in page.url for kw in ['/login/verify', '/login/email', '/signin'])
                    if _is_login_url and 'checkout/summary' not in page.url:
                        print('   ℹ️ Interstitial detected → clicking Continue/Skip', flush=True)
                        for _ics in ['button:has-text("Continue")', 'button:has-text("CONTINUE")',
                                     '#continueBtn', 'button:has-text("Skip")', 'button[type="submit"]',
                                     'a:has-text("Continue")']:
                            try:
                                _ib = page.locator(_ics).first
                                if _ib.is_visible(timeout=2000):
                                    _ib.click(timeout=5000)
                                    time.sleep(4)
                                    break
                            except Exception:
                                pass
                    for _lv_attempt in range(3):
                        if '/login/verify' not in page.url:
                            break
                        print(f'   ℹ️ On login/verify (attempt {_lv_attempt+1}/3) → clicking CONTINUE', flush=True)
                        for _ics in ['button:has-text("CONTINUE")', 'button:has-text("Continue")',
                                     'button.continue_btn', 'button[type="submit"]']:
                            try:
                                _ib = page.locator(_ics).first
                                if _ib.is_visible(timeout=3000):
                                    _ib.click(timeout=5000)
                                    time.sleep(5)
                                    break
                            except Exception:
                                pass
                    # STILL on /login/verify after the Continue clicks → the account likely
                    # already EXISTS (Magzter wants password/OTP). Mutate the email IN-SESSION
                    # on this SAME form and re-submit until we get past /login/verify (eligible)
                    # or mutations run out (then → not eligible). Same idea as the billingForm.
                    if '/login/verify' in page.url and EMAIL_MUTATION:
                        while '/login/verify' in page.url and len(_tried) <= MAX_EMAIL_MUTATIONS:
                            _nxt = db.mutate_email(_orig_email, _tried)
                            if not _nxt:
                                break
                            _tried.add(_nxt); email = _nxt
                            print(f'   🔁 Stuck on verify — new email on SAME form: {email}', flush=True)
                            try: type_with_retry(page, email_sel, email)
                            except Exception: pass
                            try:
                                page.evaluate("() => { try { const b=document.getElementById('continueBtn'); if(b){ b.removeAttribute('disabled'); b.disabled=false; } } catch(e){} }")
                            except Exception: pass
                            for _cs in ['#continueBtn','button:has-text("Continue")','button.continue_btn']:
                                try:
                                    _bb = page.locator(_cs).first
                                    if _bb.count() and _bb.is_visible():
                                        _bb.click(timeout=6000, force=True); break
                                except Exception: pass
                            time.sleep(2)
                            if '/login/verify' in page.url:
                                try:
                                    page.evaluate("() => { try { const f=document.forms['verify_form']||document.querySelector('form.verify_form, form[action*=\"verify\"], form'); if(f){ f.requestSubmit ? f.requestSubmit() : f.submit(); } } catch(e){} }")
                                except Exception: pass
                            time.sleep(3)
                        if email != _orig_email:
                            try: db.set_updated_email(task_id, email, len(_tried)-1)
                            except Exception: pass
                    if '/login/verify' in page.url:
                        raise Exception('Not eligible: stuck on login/verify')
                except Exception as _lv_ex:
                    if 'login/verify' in str(_lv_ex).lower():
                        raise
                # NAME is filled later in the CHECKOUT FLOW below (FLOW B name form).

                break
            except Exception:
                # Eligibility is decided on the billingForm (below), NOT at the email/reCAPTCHA
                # step — do NOT re-enter email here (that revived 'Continue button disabled').
                raise
        if email != _orig_email:
            try: db.set_updated_email(task_id, email, len(_tried)-1)
            except Exception: pass

        # ── CHECKOUT FLOW A/B/C (ported from aws) ────────────────────────────────
        #   A) Already on Stripe hosted checkout (checkout.stripe.com / payment.magzter.com)
        #   B) Name form visible → submit → detect Stripe (new tab OR same tab)
        #   C) Summary page → click "Credit/Debit Card" → detect Stripe
        t0 = time.time()
        _NAME_SELS_F = ['#firstName','input[name="firstName"]','input[placeholder*="First Name" i]','input[placeholder*="first" i]']
        _NAME_SELS_L = ['#lastName','input[name="lastName"]','input[placeholder*="Last Name" i]','input[placeholder*="last" i]']
        _NAME_SUBMIT = ['#submitBtn','#continueBtn','button:has-text("Continue")','button:has-text("CONTINUE")','button:has-text("Submit")','button[type="submit"]']

        def _on_stripe(p):
            return ('checkout.stripe.com' in p.url or 'payment.magzter.com' in p.url)

        def _switch_to_stripe_tab():
            """If a context page is on Stripe, return it; else None."""
            for _p in context.pages:
                if _on_stripe(_p):
                    return _p
            return None

        def _poll_for_stripe(cur_page, rounds=20):
            """Poll up to `rounds` x1s for Stripe to appear in the same tab or a new
            tab; return the page on Stripe (possibly cur_page) or cur_page if none."""
            for _ in range(rounds):
                if _on_stripe(cur_page):
                    return cur_page
                t = _switch_to_stripe_tab()
                if t is not None:
                    return t
                time.sleep(1)
            t = _switch_to_stripe_tab()
            return t if t is not None else cur_page

        if _on_stripe(page):
            # Flow A
            print('   ℹ️ Already on Stripe hosted checkout', flush=True)
        elif wait_for_any(page, _NAME_SELS_F, timeout=12000):
            # Flow B — name form (TYPE so its submit button reliably enables too)
            print('   ℹ️ Name form detected — filling', flush=True)
            type_with_retry(page, _NAME_SELS_F, first_name)
            type_with_retry(page, _NAME_SELS_L, last_name)
            try: page.keyboard.press("Enter")
            except: pass
            time.sleep(1)
            def _submit_billing():
                for _ns in _NAME_SUBMIT + ["a.btn.primary__btn","a[class*='btn']"]:
                    try:
                        _nb = page.locator(_ns).first
                        if _nb.is_visible(timeout=2000):
                            _nb.click(timeout=10000)
                            print(f'   ✅ Billing form submitted via: {_ns}', flush=True)
                            return True
                    except Exception:
                        pass
                return False
            _submit_billing()
            time.sleep(1.5)
            # IN-SESSION eligibility retry on the SAME billingForm: refill first+last name +
            # new email, re-submit. No re-navigate, no reCAPTCHA email-step.
            while True:
                elig_err = page_has_error(page, ELIGIBILITY_MSGS)
                if not elig_err: break
                if not EMAIL_MUTATION or len(_tried) > MAX_EMAIL_MUTATIONS:
                    raise Exception(f"Not eligible: {elig_err}")
                _nxt = db.mutate_email(_orig_email, _tried)
                if not _nxt:
                    raise Exception(f"Not eligible: mutations exhausted ({str(elig_err)[:40]})")
                _tried.add(_nxt); email = _nxt
                print(f'   🔁 Not eligible — refilling billingForm with new email: {email}', flush=True)
                type_with_retry(page, _NAME_SELS_F, first_name)
                type_with_retry(page, _NAME_SELS_L, last_name)
                if not type_with_retry(page, ['#email','input[name="email"]','input[type="email"]'], email):
                    raise Exception(f"Not eligible: could not re-enter email ({str(elig_err)[:30]})")
                time.sleep(0.5)
                _submit_billing()
                time.sleep(2.5)
            if email != _orig_email:
                try: db.set_updated_email(task_id, email, len(_tried)-1)
                except Exception: pass
            page = _poll_for_stripe(page, rounds=20)
            if _on_stripe(page):
                print('   ✅ Stripe checkout detected after name form', flush=True)
            else:
                print(f'   ⚠️ Stripe checkout URL not detected — current URL: {page.url[:80]}', flush=True)
        else:
            # Flow C — summary page; click Credit/Debit Card
            print(f'   ℹ️ No name form — trying Credit/Debit Card (URL: {page.url[:60]})', flush=True)
            _card_btn_clicked = False
            for _cbs in ['button:has-text("Credit/Debit Card")', 'button:has-text("Credit")',
                         'button:has-text("Card")', '[class*="card-btn"]', '[data-payment="card"]']:
                try:
                    _cb = page.locator(_cbs).first
                    if _cb.is_visible(timeout=3000):
                        _cb.click(timeout=10000)
                        _card_btn_clicked = True
                        print('   ✅ Credit/Debit Card clicked', flush=True)
                        time.sleep(2)
                        break
                except Exception:
                    pass
            if not _card_btn_clicked:
                try: page.screenshot(path=os.path.join(SCREENSHOT_DIR, "CARD_BTN_MISSING_"+email_to_filename(email)))
                except: pass
                raise Exception(f"Could not navigate to payment: no name form or card button (URL={page.url})")
            page = _poll_for_stripe(page, rounds=20)
            if _on_stripe(page):
                print('   ✅ Stripe checkout detected after Credit/Debit Card click', flush=True)

        # Common Stripe hosted-checkout setup: uncheck Link, cardholder name, country →
        # India. Wrapped in a function so we can RE-RUN it if the payment form gets
        # reloaded below — a reload wipes the name/country/uncheck, and re-doing it keeps
        # the country=India (so the card isn't declined on a reverted country).
        def _stripe_prep(p):
            if not _on_stripe(p):
                return
            try:
                _save_chk = p.locator('input[type="checkbox"]').first
                if _save_chk.is_visible(timeout=2000) and _save_chk.is_checked():
                    _save_chk.uncheck()
                    print('   ℹ️ Unchecked "Save my information"', flush=True)
            except Exception:
                pass
            _name_sels_stripe = ['input[placeholder*="Full name" i]', 'input[autocomplete="cc-name"]',
                                 'input[name="billingName"]', 'input[id*="billingName"]']
            if fill_with_retry(p, _name_sels_stripe, name_used):
                print(f'   ✅ Cardholder name filled on Stripe: {name_used}', flush=True)
            try:
                for _cc_sel in ['select[name="billingCountry"]', 'select[id*="country" i]',
                                'select[autocomplete*="country" i]', 'select[name*="country" i]']:
                    _cc_el = p.locator(_cc_sel).first
                    if _cc_el.is_visible(timeout=2000):
                        _cc_el.select_option('IN')
                        print('   ✅ Billing country → India', flush=True)
                        time.sleep(0.5)
                        break
            except Exception:
                pass

        _stripe_prep(page)
        local.log("CHECKOUT", "success", time.time()-t0, name_used)
        time.sleep(0.5)

        # ── PAYMENT — fill across page + all iframes (fill_in_frames, from aws) ───
        t0=time.time()
        def fill_in_frames(sels, value, quick_timeout=3000):
            """Quick scan across page + all frames; short per-selector timeout to
            avoid blocking on a wrong selector. Keeps #cardNumber as one variant."""
            if isinstance(sels, str): sels = [sels]
            for ctx in [page] + list(page.frames):
                for sel in sels:
                    try:
                        ctx.wait_for_selector(sel, timeout=quick_timeout, state="visible")
                        ctx.fill(sel, value)
                        return True
                    except Exception:
                        pass
            return False

        # Last-chance new-tab detection before PAYMENT.
        if not _on_stripe(page):
            t = _switch_to_stripe_tab()
            if t is not None:
                page = t
                print('   ✅ Stripe in new tab (PAYMENT entry) → switched', flush=True)

        # Wait for the Stripe payment form (up to ~90s; reload embedded Stripe at ~45s).
        _card_loaded = False
        _stripe_reloads = 0
        _stripe_window_start = time.time()
        _stripe_hard_deadline = time.time() + 210   # ~4 windows of 40s + reload overhead
        _stripe_poll = 0
        _card_detect = ['[placeholder*="1234" i]','#cardNumber','input[name="cardNumber"]',
                        '[placeholder*="Card number" i]','input[autocomplete="cc-number"]']
        while time.time() < _stripe_hard_deadline:
            _stripe_poll += 1
            for _ctx in [page] + list(page.frames):
                for _cs in _card_detect:
                    try:
                        if _ctx.locator(_cs).first.is_visible(timeout=1000):
                            _card_loaded = True; break
                    except Exception: pass
                if _card_loaded: break
            if _card_loaded: break
            # USER RULE: captcha on the payment page -> Stripe never opens its card form, so
            # fast-fail to retry immediately instead of sitting through the whole wait.
            if _hcaptcha_present(page):
                try: page.screenshot(path=os.path.join(SCREENSHOT_DIR,"CAPTCHA_PAY_"+email_to_filename(email)))
                except: pass
                raise Exception("Captcha appeared — fast-fail to retry")
            # If the card form hasn't become stable within 40s of this window, reload ONCE and
            # reset the window. Up to 3 reloads — INCLUDING hosted checkout.stripe.com (its
            # cs_live_… URL is reload-safe and restores the form).
            if (time.time() - _stripe_window_start) >= 40:
                if _stripe_reloads >= 3:
                    break                        # 3 reloads used + window expired → give up
                _stripe_reloads += 1
                print(f"   ⚠️ Stripe card step not stable in 40s — reload {_stripe_reloads}/3...", flush=True)
                try:
                    page.reload(timeout=20000, wait_until="domcontentloaded")
                    time.sleep(5)
                except Exception: pass
                try: _stripe_prep(page)          # name/country/uncheck wiped by the reload
                except Exception: pass
                _stripe_window_start = time.time()
            if _stripe_poll % 10 == 5:
                dec = page_has_error(page, DECLINE_MSGS)
                if dec: raise Exception(f"Card declined: {dec}")
            time.sleep(1)
        _stripe_reloaded = _stripe_reloads > 0
        if not _card_loaded:
            try: page.screenshot(path=os.path.join(SCREENSHOT_DIR,"PAYMENT_MISSING_"+email_to_filename(email)))
            except: pass
            raise Exception("Stripe payment form not loaded")

        # If we reloaded the Stripe page above, the earlier hosted-checkout prep (uncheck
        # Save-info / cardholder name / country=India) was wiped — RE-DO it now on the
        # fresh form before filling the card, so nothing is left blank or reverted.
        if _stripe_reloaded:
            print("   ↻ Re-applying Stripe prep after reload (name / country / uncheck)", flush=True)
            _stripe_prep(page)

        # Card number / expiry / cvc / name — many variants, #cardNumber kept.
        if not fill_in_frames(['#cardNumber','input[name="cardNumber"]','[placeholder*="Card number" i]',
                               '[placeholder*="1234" i]','input[autocomplete="cc-number"]'], card_no):
            raise Exception("Card field not fillable")
        fill_in_frames(['#cardExpiry','[placeholder*="MM / YY" i]','[placeholder*="MM/YY" i]',
                        '[placeholder*="expir" i]','input[autocomplete="cc-exp"]'], expiry)
        fill_in_frames(['#cardCvc','[placeholder*="CVC" i]','[placeholder*="CVV" i]',
                        '[placeholder*="security" i]','input[autocomplete="cc-csc"]'], cvv)
        fill_in_frames(['#billingName','input[name="name"]','[placeholder*="Full name" i]',
                        '[placeholder*="Name" i]','input[autocomplete="cc-name"]'], name_used, quick_timeout=2000)
        local.log("PAYMENT","success",time.time()-t0)
        time.sleep(random.uniform(2,3))

        # SUBMIT — search all frames for the Stripe pay button; fall back to Enter.
        t0=time.time()
        _submitted = False
        _pay_sels = ['button[data-testid="hosted-payment-submit-button"]','button.SubmitButton',
                     'div.SubmitButton-IconContainer','button:has-text("Pay")','button:has-text("Subscribe")']
        for _ctx in [page] + list(page.frames):
            for _ps in _pay_sels:
                try:
                    _pb = _ctx.locator(_ps).first
                    if _pb.is_visible(timeout=3000):
                        _pb.click(timeout=ELEMENT_WAIT)
                        _submitted = True
                        break
                except Exception:
                    pass
            if _submitted: break
        if not _submitted:
            page.keyboard.press("Enter")
        local.log("SUBMIT","success",time.time()-t0)
        time.sleep(random.uniform(5,8))

        # hCaptcha checkbox handler (from aws) — a "I am human" hCaptcha can appear
        # right after Subscribe on Stripe when the IP/fingerprint is flagged. The
        # checkbox lives inside an iframe (src contains "hcaptcha.com"); clicking it
        # auto-solves the easy challenges. Complements the 2captcha token solver used
        # at the corporate step below.
        def _try_solve_hcaptcha():
            try:
                _hc_iframe_sels = [
                    'iframe[src*="hcaptcha"]',
                    'iframe[data-hcaptcha-widget-id]',
                    'iframe[title*="hCaptcha"]',
                    'iframe[title*="Human"]',
                ]
                for _sel in _hc_iframe_sels:
                    try:
                        _fl = page.frame_locator(_sel).first
                        _cb = _fl.locator('#checkbox, .checkbox, [aria-label*="human" i]')
                        if _cb.count() > 0:
                            _cb.first.click(timeout=3000)
                            print('   ✅ hCaptcha solved (iframe click)', flush=True)
                            time.sleep(3)
                            return True
                    except Exception:
                        pass
                for _fr in page.frames:
                    if 'hcaptcha' in (_fr.url or '').lower():
                        try:
                            _fr.locator('#checkbox, [role="checkbox"]').first.click(timeout=2000)
                            print('   ✅ hCaptcha solved (frame URL match)', flush=True)
                            time.sleep(3)
                            return True
                        except Exception:
                            pass
            except Exception:
                pass
            return False

        # Stripe "I am human" hCaptcha after Subscribe. A flagged IP/fingerprint shows a
        # real CHALLENGE that a checkbox-click can NEVER pass — that's the "captcha keeps
        # coming back, bot loops forever" you saw. So: cheap checkbox click first (passes
        # easy ones), THEN solve it PROPERLY via 2captcha (token injection) which handles
        # challenges. Capped (no infinite loop) — if it still can't pass, we fall through
        # and the corp-form wait below fail-fasts into a retry instead of hanging.
        _try_solve_hcaptcha()
        try:
            if solve_hcaptcha(page) is False:
                print("   ⚠️ Stripe hCaptcha 2captcha solve failed — continuing", flush=True)
        except Exception as _ce:
            print(f"   ⚠️ Stripe captcha error: {str(_ce)[:100]}", flush=True)

        # ── CORPORATE — fuzzy selectors, search page + iframes, 3x reload retry ───
        t0=time.time()

        def _find_corp_ctx():
            for ctx in [page] + list(page.frames):
                for cs in CORP_ID_SELS:
                    try:
                        if ctx.locator(cs).count() > 0:
                            return ctx
                    except Exception:
                        pass
            return None

        local.mark("CORPORATE-WAIT")   # dashboard: instance is now waiting for corp form
        corp_ctx = _find_corp_ctx()
        _cap_deadline = time.time() + CAPTCHA_MAX_TOTAL   # cap corp+captcha; else RETRY
        for corp_try in range(1, 4):                      # 3 attempts (2 reloads)
            if corp_ctx: break
            if time.time() > _cap_deadline:
                print("   ⏱️ corp/captcha over 5-min budget — bailing to RETRY", flush=True); break
            print(f"   ⏳ Waiting for corporate form (try {corp_try}/3, up to 40s)...")
            # If an hCaptcha is what's blocking the corp form from appearing, solve it via
            # 2captcha ONCE per try (challenge-capable, unlike a checkbox click). Cheap
            # no-op ('none') when there's no captcha.
            try:
                if time.time() < _cap_deadline: solve_hcaptcha(page)
            except Exception:
                pass
            for n in range(40):                           # 40s/try × 3 = ~2 min (was 6 min)
                corp_ctx = _find_corp_ctx()
                if corp_ctx: break
                if time.time() > _cap_deadline: break
                if n % 5 == 0:
                    dec_err = page_has_error(page, DECLINE_MSGS)
                    if dec_err: raise Exception(f"Card declined: {dec_err}")
                # NOTE: we deliberately do NOT click the hCaptcha checkbox here. Clicking it
                # flips the corp-form hCaptcha into challenge mode, which makes the 2captcha
                # token we inject just before submit get IGNORED — that's exactly why the
                # buyer's captcha stopped working vs the root script. The corp hCaptcha is
                # solved purely by token injection in solve_hcaptcha() right before submit.
                time.sleep(1)
            if corp_ctx: break
            if corp_try < 3:
                print("   🔄 Corporate form not found — reloading page and retrying...", flush=True)
                try: page.reload(wait_until="domcontentloaded", timeout=NAVIGATION_TIMEOUT)
                except Exception as _re: print(f"   ⚠️ reload error: {str(_re)[:80]}", flush=True)
                time.sleep(5)
                dismiss_popups(page)
        if not corp_ctx:
            try:
                body = (page.locator('body').inner_text(timeout=5000) or "")[:400]
                print(f"   🔎 Corporate not found after 3 tries — page says: {body!r}", flush=True)
            except Exception: pass
            try: page.screenshot(path=os.path.join(SCREENSHOT_DIR,"CORP_MISSING_"+email_to_filename(email)))
            except Exception: pass
            raise Exception("Corporate form not found")

        def corp_gone():
            try: return not corp_ctx.locator(CORP_ID_SELS[0]).is_visible()
            except: return True

        confirmed = False
        otp_failure_recorded = False

        # Serialize the corp-submit → OTP-fetch → CONFIRM window per employee across
        # all instances so two bots on the same emp never consume each other's OTP.
        with db.otp_lock(emp_id):
            # Baseline (no-op consume-on-fetch); kept for signature parity.
            prev_otp = fetch_otp_once(emp_id, card_last_four=card_no[-4:])

            fill_with_retry(corp_ctx, CORP_ID_SELS, corp_id)
            fill_with_retry(corp_ctx, EMP_ID_SELS, emp_id)
            time.sleep(1)

            # Debug dump (from aws): list every button/submit/anchor in the corp frame
            # so a missing/renamed submit control is visible in the logs.
            try:
                _btns = corp_ctx.eval_on_selector_all("button,input[type='submit'],a.btn",
                    "els=>els.map(e=>({tag:e.tagName,cls:e.className,txt:e.innerText.trim().slice(0,30),vis:e.offsetParent!==null}))")
                print(f"   🔎 Corp frame buttons: {_btns}", flush=True)
            except Exception:
                pass

            # hCaptcha on the corporate form — solve it via 2captcha RIGHT BEFORE submit
            # (like the proven root script). The token is only valid ~120s, so solving
            # here, immediately before clicking Submit, avoids it going stale. We do NOT
            # click the hCaptcha checkbox (that flips the widget into challenge mode and
            # makes the injected token be ignored) — pure token injection is what works.
            try:
                if solve_hcaptcha(page) is False:
                    print("   ⚠️ hCaptcha solve failed — submitting anyway", flush=True)
            except Exception as _ce:
                print(f"   ⚠️ captcha step error: {str(_ce)[:100]}", flush=True)

            # JS-click-first for ICICI <a> submit anchors, then regular click.
            submitted = False
            _corp_submit_sels = ["a.btn.primary__btn", "button:has-text('SUBMIT')",
                                 "button:has-text('Submit')", "input[type='submit']", "button[type='submit']"]
            for sub in _corp_submit_sels:
                try:
                    btn = corp_ctx.locator(sub).first
                    if not btn.is_visible(timeout=2000): continue
                    try:
                        corp_ctx.eval_on_selector(sub, "el => el.click()")
                        print(f"   🖱️ JS-clicked corp submit: {sub}", flush=True)
                    except Exception:
                        btn.click(timeout=ELEMENT_WAIT)
                        print(f"   🖱️ Clicked corp submit: {sub}", flush=True)
                    for _w in range(60):
                        if corp_gone(): submitted = True; break
                        if _w % 5 == 0:
                            dec = page_has_error(page, DECLINE_MSGS)
                            if dec: raise Exception(f"Card declined: {dec}")
                        time.sleep(1)
                    if submitted: break
                except Exception as _se:
                    if 'declined' in str(_se).lower(): raise
                    continue

            if not submitted:
                try: page.screenshot(path=os.path.join(SCREENSHOT_DIR,"CORP_SUBMIT_FAIL_"+email_to_filename(email)))
                except: pass
                raise Exception("Corporate form did not submit")
            local.log("CORPORATE","success",time.time()-t0,f"{corp_id}/{emp_id}")

            # ── HDFC 3D-Secure: "Static Password" PIN page (buyer_hdfc only) ─────────
            # Some cards (e.g. HDFC) show a static-password 3DS PIN page instead of OTP.
            # Detect it (in any frame); if present, fill the configured PIN and Submit.
            # The page hashes the PIN itself on submit, so we fill the RAW value.
            # If it's an OTP page instead (ICICI etc.), we fall through to the OTP flow.
            print("   ✅ Corporate submitted, waiting for 3DS auth screen...")
            _static_done = False
            for _sn in range(60):
                _sframe = None
                for _fr in page.frames:
                    try:
                        _spl = _fr.locator("#staticPassword, input[name='passCode']").first
                        if _spl.is_visible(timeout=800): _sframe = _fr; break
                    except Exception:
                        continue
                if _sframe is not None:
                    print("   🔐 HDFC static-password 3DS page detected", flush=True)
                    if not HDFC_3DS_PIN:
                        raise Exception("HDFC_3DS_PIN not set in config.json")
                    _sframe.locator("#staticPassword, input[name='passCode']").first.fill(
                        HDFC_3DS_PIN, timeout=ELEMENT_WAIT)
                    print("   🔐 HDFC PIN filled", flush=True)
                    time.sleep(1)
                    _sp_clicked = False
                    for _ss in ["a.btn.primary__btn","a.primary__btn","button.primary__btn",
                                "button:has-text('Submit')","a:has-text('Submit')","input[type='submit']"]:
                        try:
                            _sb = _sframe.locator(_ss).first
                            if _sb.is_visible(timeout=1500):
                                try: _sframe.eval_on_selector(_ss, "el => el.click()")
                                except Exception: _sb.click(timeout=ELEMENT_WAIT)
                                print(f"   🖱️ Clicked PIN submit: {_ss}", flush=True)
                                _sp_clicked = True; break
                        except Exception:
                            continue
                    if not _sp_clicked:
                        try: _sframe.evaluate("typeof authSubmit==='function' && authSubmit()")
                        except Exception: pass
                    print("   ✅ HDFC PIN submitted (page hashes + submits)", flush=True)
                    local.mark("OTP-WAIT")
                    # let the payment settle; bail early on a card decline
                    for _w in range(10):
                        try: _t = page.locator('body').inner_text(timeout=5000).lower()
                        except Exception: _t = ""
                        _dec = next((m for m in DECLINE_MSGS if m in _t), None)
                        if _dec: raise Exception(f"Card declined: {_dec}")
                        time.sleep(2)
                    _static_done = True
                    break
                # not a static-password page — if OTP shows, use the OTP flow below
                if find_otp_field(page)[0]:
                    break
                time.sleep(1)

            # OTP screen detection (skipped automatically when the HDFC PIN path ran)
            otp_ctx,otp_sel=None,None
            otp_text_seen=False
            for n in range(0 if _static_done else 120):
                otp_ctx,otp_sel=find_otp_field(page)
                if otp_ctx: print("   ✅ OTP field detected (enabled, non-payment)",flush=True);break
                if n % 15 == 0:
                    try: txt=page.locator('body').inner_text(timeout=5000).lower()
                    except Exception: txt=""
                    if any(k in txt for k in ("otp","verification code","one-time","one time code","enter the code","verify your")):
                        otp_text_seen=True
                time.sleep(1)

            if not otp_ctx and not _static_done:
                try:
                    inputs=page.eval_on_selector_all('input',
                        "els=>els.map(e=>({name:e.name,id:e.id,type:e.type,ph:e.placeholder,maxlen:e.maxLength})).slice(0,20)")
                    print(f"   🔎 No OTP input matched. Inputs on page: {inputs}",flush=True)
                except Exception: pass
                if not otp_text_seen:
                    raise Exception("OTP screen not reached")
                print("   ⚠️ OTP text seen but input selector didn't match — calling API anyway",flush=True)

            t0=time.time()
            success_urls=["success","thank","welcome","receipt","subscribed","home","library",
                          "profile","gold","confirmation","complete","order","congratulation",
                          "activated","payment-success"]
            success_text=["thank you","successfully","enjoy","subscription is active","you're all set",
                          "you are all set","payment successful","order confirmed","welcome to",
                          "activated","congratulations","is now active","you're subscribed","your plan",
                          # the real Magzter Gold success page (no login needed):
                          "subscribing to magzter gold","for subscribing to magzter",
                          "you're just one step away","one step away","thank you for subscribing"]

            local.mark("OTP-WAIT")   # dashboard: instance is now waiting for / entering OTP
            for otp_attempt in range(1, (0 if _static_done else MAX_OTP_ATTEMPTS)+1):
                print(f"   🔐 Fetching OTP (attempt {otp_attempt}/{MAX_OTP_ATTEMPTS})...")
                _poll_delay = 4 if otp_attempt == 1 else 2
                _max_polls  = 30 if otp_attempt == 1 else 60
                otp = get_otp(emp_id, prev_otp=prev_otp, max_polls=_max_polls,
                              delay=_poll_delay, card_last_four=card_no[-4:])

                if not otp:
                    if otp_attempt < MAX_OTP_ATTEMPTS:
                        print("   ⚠️ No OTP from API — clicking Resend and retrying", flush=True)
                        prev_otp = fetch_otp_once(emp_id, card_last_four=card_no[-4:])
                        click_resend(page)
                        time.sleep(6)
                        otp_ctx,otp_sel = find_otp_field(page)
                        continue
                    raise Exception("OTP not received")

                if otp=="manual":
                    input("   Press Enter after manual OTP...")
                    status="SUCCESS"; confirmed=True
                    break

                print(f"   ✅ OTP: {otp}")
                if not otp_ctx: otp_ctx,otp_sel=find_otp_field(page)
                if not otp_ctx: raise Exception("OTP field lost")

                loc=otp_sel
                loc.fill(otp,timeout=ELEMENT_WAIT)
                print(f"   ✅ OTP filled")
                time.sleep(1)

                # JS-click-first for ICICI <a> anchor OTP submit.
                _otp_submit_sels = ["a.btn.primary__btn","button.primary__btn","button[type='submit']",
                                    "#submitBtn","button:has-text('SUBMIT')","button:has-text('Submit')",
                                    "input[type='submit']"] + SUBMIT_BTN
                _otp_clicked = False
                for _os in _otp_submit_sels:
                    try:
                        _ob = otp_ctx.locator(_os).first
                        if _ob.is_visible(timeout=3000):
                            try:
                                otp_ctx.eval_on_selector(_os, "el => el.click()")
                                print(f"   🖱️ JS-clicked OTP submit: {_os}", flush=True)
                            except Exception:
                                _ob.click(timeout=ELEMENT_WAIT)
                            _otp_clicked = True
                            break
                    except Exception:
                        continue
                if not _otp_clicked:
                    loc.press("Enter")
                print(f"   ✅ OTP submitted")
                time.sleep(2)

                print("   ⏳ Waiting for confirmation...")
                invalid=False
                # After payment Stripe redirects THIS SAME tab to the Magzter "Thank you for
                # subscribing to Magzter GOLD" page. That redirect is often SLOW and the page
                # sometimes lands BLANK/half-loaded — the bot then just waits and times out
                # into a false "unconfirmed". So: be patient, and if we've left Stripe but the
                # page is blank/stuck, RELOAD it to force the thank-you to render.
                blank=0
                for i in range(40):                       # ~80s — login→my_orders verify below is the real proof
                    try:
                        url=(page.url or "").lower()
                        text=page.locator('body').inner_text(timeout=5000).lower()
                    except Exception:
                        url=(page.url or "").lower(); text=""
                    dec=next((m for m in DECLINE_MSGS if m in text), None)
                    if dec: raise Exception(f"Card declined: {dec}")
                    if any(w in text for w in OTP_INVALID_MSGS):
                        invalid=True; break
                    if any(w in url for w in success_urls) or any(w in text for w in success_text):
                        confirmed=True; break
                    # left Stripe/hCaptcha but page is blank/stuck -> reload to render the thank-you
                    if 'stripe.com' not in url and 'hcaptcha' not in url and len(text.strip()) < 25:
                        blank += 1
                        if blank in (5, 10, 16):
                            try:
                                print(f"   ↻ post-payment page blank — reloading ({blank})", flush=True)
                                page.reload(wait_until="domcontentloaded", timeout=25000)
                            except Exception: pass
                    time.sleep(2)

                if confirmed:
                    break

                if invalid and otp_attempt < MAX_OTP_ATTEMPTS:
                    print(f"   ⚠️ OTP invalid/expired — clicking Resend and retrying", flush=True)
                    prev_otp = fetch_otp_once(emp_id, card_last_four=card_no[-4:])
                    click_resend(page)
                    time.sleep(6)
                    otp_ctx,otp_sel = find_otp_field(page)
                    continue

                break

            # DEFINITIVE verify — the thank-you page often never loads after payment, so
            # don't sit waiting. LOG IN with the same email in a fresh tab and read the
            # Transaction ID from my_orders (account order-history = real proof). A
            # freshly-bought email hits the "Create Account" form (we set the password); an
            # existing one → password login. Needs VERIFY_LOGIN_PASSWORD in config.
            if not confirmed:
                print("   🔎 Thank-you not seen — verifying via login → my_orders…", flush=True)
                _vpass = (task.get('password') or "").strip() or VERIFY_LOGIN_PASSWORD
                txn = verify_via_login(context, email, name_used, _vpass)
                if txn and txn.upper() != "NOT_FOUND":
                    confirmed = True; _txn_id = txn
                    print(f"   ✅ Confirmed via login → my_orders — Transaction ID: {txn}", flush=True)
                else:
                    print(f"   ❌ login verify: no Transaction ID (txn={txn!r})", flush=True)

            try: page.screenshot(path=os.path.join(SCREENSHOT_DIR,email_to_filename(email)))
            except: pass

            if confirmed:
                print("   ✅ Confirmed!")
                local.log("OTP","success",time.time()-t0)
                status="SUCCESS"
                db.record_otp_success(emp_id)
            else:
                try:
                    final_txt = (page.locator('body').inner_text(timeout=5000) or "")[:400]
                    print(f"   🔎 Unconfirmed — url={page.url} | page says: {final_txt!r}", flush=True)
                except Exception: pass
                try: page.screenshot(path=os.path.join(SCREENSHOT_DIR,"CONFIRMDEBUG_"+email_to_filename(email)))
                except Exception: pass
                local.log("OTP","failed",time.time()-t0,error="No confirmation")
                error_msg="No purchase confirmation"
                status="UNCONFIRMED"
                # The OTP itself ARRIVED and was submitted — reaching here is a PURCHASE
                # confirmation problem (handled by the Needs-Review queue), NOT an OTP
                # delivery failure. Recording an OTP failure here wrongly inflated the
                # streak so the OTP alert never cleared even while OTP was working. Mark
                # OTP delivery healthy; the unconfirmed buy is tracked separately.
                db.record_otp_success(emp_id)

        time.sleep(8)

    except Exception as e:
        error_msg=str(e)[:300]
        print(f"   ❌ Task failed: {error_msg}", flush=True)
        if error_msg.startswith("Card declined"): status="DECLINED"
        elif error_msg.startswith("Not eligible"): status="INELIGIBLE"
        elif any(re_err in error_msg for re_err in RETRYABLE_ERRORS): status="RETRY"
        else: status="FAILED"
        # An OTP that never arrived drives the dashboard alert banner.
        if "OTP not received" in error_msg:
            try: db.record_otp_failure(emp_id)
            except Exception: pass
        local.log("ERROR","failed",0,error=error_msg)
        try:
            if page: page.screenshot(path=os.path.join(SCREENSHOT_DIR,email_to_filename(email)))
        except: pass

    finally:
        total_dur=(datetime.now()-start_time).total_seconds()
        local.save(status,proxy_ip,error_msg)

        # TERMINAL only for a clean SUCCESS or an UNCONFIRMED buy (handed to the reader to
        # confirm — never retried, that would double-buy). EVERY other outcome is a FAILURE
        # and (user rule) goes to RETRY: re-queued behind all fresh work, run again only once
        # fresh is done, and marked its REAL terminal status after MAX_TASK_RETRIES attempts.
        if status in ("SUCCESS", "UNCONFIRMED"):
            db.update_task(task_id, db.ST_COMPLETED if status == "SUCCESS" else db.ST_UNCONFIRMED,
                           name_used=name_used, proxy_ip=proxy_ip, duration_sec=round(total_dur,1),
                           error=error_msg, transaction_id=_txn_id)
        else:
            final = {"DECLINED": db.ST_DECLINED, "INELIGIBLE": db.ST_INELIGIBLE}.get(status, db.ST_FAILED)
            outcome = db.retry_or_fail(task_id, max_retries=MAX_TASK_RETRIES,
                                       error=f"Retry: {error_msg[:200]}", final_status=final,
                                       name_used=name_used, proxy_ip=proxy_ip,
                                       duration_sec=round(total_dur,1))
            if outcome == db.ST_PENDING:
                print(f"   🔄 Re-queued for retry ({status.lower()}): {error_msg[:80]}", flush=True)
            else:
                print(f"   ⛔ Retries exhausted — marked {outcome}: {error_msg[:80]}", flush=True)

        for closer in (
            lambda: context.close() if context else None,
            lambda: browser.close() if browser else None,
            lambda: pw.stop() if pw else None,
        ):
            try: closer()
            except: pass

    return {"status":status}

# ================= MAIN =================

def main():
    global _task_deadline
    # Stuck-task watchdog: restarts this instance if a task hangs.
    threading.Thread(target=_watchdog, daemon=True).start()

    # Tasks come from Postgres — created by the quota engine, no sheet involved.
    try:
        db.assert_db_ready()
    except Exception as e:
        print(f"❌ DB not reachable: {e}")
        sys.exit(1)

    # SECURITY: an OTP API URL without a token means every OTP fetch would be
    # unauthenticated. Refuse to start rather than run insecurely.
    if OTP_API_URL and not OTP_FETCH_TOKEN:
        print("❌ OTP_API_URL is set but OTP_FETCH_TOKEN is empty — refusing to start. "
              "Set the OTP token in Settings → Buy Subscriptions.", flush=True)
        sys.exit(1)

    ip = get_ip()
    print(f"\n📡 IP: {ip}")

    tunnel = Socks5Tunnel(PROXY_HOST, PROXY_PORT, PROXY_USERNAME, PROXY_PASSWORD)
    pport = tunnel.start()
    time.sleep(5)

    pip = get_proxy_ip(pport)
    print(f"🔒 Proxy: {pip}\n")

    all_start = datetime.now()
    success = failed = unconfirmed = 0
    total_done = 0
    task_secs = []                       # per-task wall time, for ETA
    ips_set = set(); cards_set = set()

    def _fmt_min(mins):
        mins = max(0, int(round(mins)))
        return f"{mins//60}h {mins%60}m" if mins >= 60 else f"{mins}m"

    # Work-stealing loop: keep claiming the next available emp_id group until none left.
    _paused_logged = False
    while True:
        # GLOBAL PAUSE — operator kill-switch. Finish nothing new while paused: just wait
        # and re-poll (the current task, if any, already completed before this point).
        # Does NOT exit, so the bot resumes claiming the moment pause is lifted.
        if db.is_paused():
            if not _paused_logged:
                print("⏸️  PAUSED by operator — waiting (no new tasks claimed)…", flush=True)
                _paused_logged = True
            time.sleep(15)
            continue
        if _paused_logged:
            print("▶️  Resumed — claiming work again.", flush=True)
            _paused_logged = False
        # LIVE value — a dashboard change to INSTANCES_PER_EMP takes effect here on the
        # next claim, so no bot has to be restarted mid-payment to apply it.
        ipe = current_instances_per_emp()
        group = db.claim_next_group(INSTANCE_ID, instances_per_emp=ipe)
        if not group:
            break

        emp = group[0]['emp_id']
        pend_rows, pend_groups = db.count_pending()
        print(f"\n{'='*60}\n👔 Group {emp}: {len(group)} task(s) claimed by instance {INSTANCE_ID}")
        print(f"   🌐 DB pending now: ~{pend_rows} transaction(s) in {pend_groups} group(s)")
        for idx, task in enumerate(group, 1):
            total_done += 1
            print(f"{'#'*60}\nGroup {emp} — task {idx}/{len(group)} (overall {total_done})")
            pip = get_proxy_ip(pport) or f"IP-{total_done}"
            ips_set.add(pip); cards_set.add(f"{task['card_no'][:4]}...{task['card_no'][-4:]}")

            t_task = time.time()
            _task_deadline = time.time() + MAX_TASK_SECONDS   # arm stuck-watchdog
            result = run_task(task, pport, pip)
            _task_deadline = None                             # disarm between tasks
            task_secs.append(time.time() - t_task)

            if result['status'] == 'SUCCESS': success += 1
            elif result['status'] == 'UNCONFIRMED': unconfirmed += 1
            else: failed += 1

            print(f"\n📊 done {total_done} | {success}✅ {failed}❌ {unconfirmed}⚠️")

            avg = sum(task_secs) / len(task_secs)
            per_task = avg + WAIT_TASKS
            grp_left = len(group) - idx
            glob_left = max(pend_rows - idx, 0)
            grp_eta = grp_left * per_task / 60
            glob_eta = (glob_left * per_task) / max(TOTAL_INSTANCES, 1) / 60
            print(f"⏱️ avg {avg:.0f}s/txn | this group: {grp_left} left ~{_fmt_min(grp_eta)} | "
                  f"sheet ~{glob_left} left → all done in ~{_fmt_min(glob_eta)} "
                  f"({TOTAL_INSTANCES} instance{'s' if TOTAL_INSTANCES != 1 else ''})", flush=True)

            if idx < len(group):
                wait = random.uniform(WAIT_TASKS, WAIT_TASKS+20)
                print(f"⏰ Wait {wait:.0f}s...")
                time.sleep(wait)

    if total_done == 0:
        print(f"\n✅ Instance {INSTANCE_ID}: No pending tasks!")
        tunnel.stop()
        return

    tunnel.stop()
    total_time = (datetime.now() - all_start).total_seconds() / 60

    rate = (success/total_done*100) if total_done else 0
    avg_txn = (sum(task_secs)/len(task_secs)) if task_secs else 0
    print(f"""
╔══════════════════════════════════════════╗
║  ✅ {success} | ❌ {failed} | ⚠️ {unconfirmed} | 📈 {rate:.1f}%
║  ⏱️ {total_time:.1f} min total | {avg_txn:.0f}s/txn avg | {total_done} txns
╚══════════════════════════════════════════╝
""")

if __name__ == "__main__":
    main()
