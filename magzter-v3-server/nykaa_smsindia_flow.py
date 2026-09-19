

import os
import re
import sys

import json
import random
import asyncio
import urllib.parse
import urllib.request
from datetime import datetime

# .exe / Windows console (cp1252) me emoji crash na ho -> stdout UTF-8
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# ROOT = jis folder me exe/script hai (frozen .exe me exe ka folder, warna script ka).
if getattr(sys, "frozen", False):
    ROOT = os.path.dirname(sys.executable)
else:
    ROOT = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, ROOT)

import nykaa_login as nk
# Prefer patchright (stealth/undetected Playwright) if present; else plain playwright —
# same as buyer.py / source.py. Nykaa fingerprints hard, so the stealth build matters.
try:
    from patchright.async_api import async_playwright
    _ENGINE = "patchright"
except ImportError:
    from playwright.async_api import async_playwright
    _ENGINE = "playwright"


# =====================================
# CONFIG
# =====================================
SMSINDIA_API_KEY = "CHANGE_ME_API_KEY"
SMSINDIA_BASE = "https://api.smsindia.pro/stubs/handler_api.php"

# Provider-side values, so they are env-tunable: when smsindia changes what it accepts
# the bot must not need a code edit on eight servers. OPERATOR="" omits the param.
SERVICE  = os.environ.get("NYKAA_SMS_SERVICE",  "yla")    # Nykaa
COUNTRY  = os.environ.get("NYKAA_SMS_COUNTRY",  "22")     # India
OPERATOR = os.environ.get("NYKAA_SMS_OPERATOR", "10")     # high-success operator

MAX_ACCOUNTS = 200           # standalone run me total accounts
CONCURRENT_SESSIONS = 1      # ek saath kitne (1 recommended)

SKIP_EXISTING_ACCOUNTS = True

# ---- EMAIL (Cloudflare Email Worker) ----
# Domain SABME same rahega; local-part har account me alag + realistic banega.
EMAIL_DOMAIN = "test@example.com"
WORKER_OTP_URL = "https://nykaa-otp.buzzaro-otp.workers.dev/otp"
WORKER_API_TOKEN = "CHANGE_ME_TOKEN"
def _nk_setting(key, default):
    """settings.json -> nykaa.<key>. Launch par padha jaata hai, to dashboard se badalne
    ke baad slot Stop -> Start karna kaafi hai; deploy dobara nahi."""
    try:
        from settings_util import load_settings
        v = (load_settings("nykaa") or {}).get(key)
        return default if v in (None, "") else type(default)(v)
    except Exception:
        return default


# Intezaar ab MINUTE me set hota hai, retries me nahi — "24" ka matlab samajhne ke liye
# interval yaad rakhna padta tha. Retries usse khud nikal aate hain.
EMAIL_OTP_INTERVAL = 10
EMAIL_OTP_WAIT_MIN = _nk_setting("email_otp_wait_min", 7)
EMAIL_OTP_RETRIES  = max(1, int(EMAIL_OTP_WAIT_MIN * 60 / EMAIL_OTP_INTERVAL))

# Accounts ab DATABASE me jaate hain (nykaa_accounts table) — Google Sheet aur CSV
# dono hata diye gaye. Dashboard se hi sab dikhta hai.

# Session storage. Per-instance, because slots on one box would otherwise write into
# each other's folder — the same reason nykaa_login's Chrome profile is per-instance.
SESSIONS_DIR = os.path.join(
    ROOT, f"sessions_{nk.INSTANCE}" if getattr(nk, "INSTANCE", 0) else "sessions")
os.makedirs(SESSIONS_DIR, exist_ok=True)

# Mobile OTP ka wait — dashboard se (Settings -> Nykaa -> "SMS OTP wait (minutes)").
OTP_POLL_INTERVAL = 30
SMS_OTP_WAIT_MIN  = _nk_setting("sms_otp_wait_min", 12)
OTP_MAX_RETRIES   = max(1, int(SMS_OTP_WAIT_MIN * 60 / OTP_POLL_INTERVAL))
STOCK_WAIT_SECONDS = 15
STOCK_WAIT_RETRIES = 8


# =====================================
# IDENTITY (random name + email)  — har account alag
# =====================================
_FIRST_NAMES = [
    "aarav", "vivaan", "aditya", "rahul", "rohan", "arjun", "karan", "amit",
    "raj", "sahil", "ishan", "dev", "yash", "nikhil", "varun", "ankit",
    "manish", "saurabh", "gaurav", "harsh", "abhishek", "vikas", "deepak",
    "priya", "neha", "pooja", "anjali", "sneha", "kavya", "riya", "divya",
    "meera", "simran", "isha", "aditi", "shreya", "nidhi", "swati", "payal",
]
_LAST_NAMES = [
    "sharma", "verma", "gupta", "singh", "kumar", "yadav", "mishra", "patel",
    "reddy", "nair", "das", "jain", "mehta", "agarwal", "chauhan", "rana",
    "bansal", "arora", "malhotra", "joshi", "saxena", "tiwari", "shukla",
]

# Ek run me email dobara na bane iske liye
_used_emails = set()


def generate_identity():
    """
    Return (name, email). Domain hamesha EMAIL_DOMAIN (buzzaro.in).
    Local-part har baar alag realistic: firstname[.|_]lastname<digits> style.
    """
    for _ in range(50):
        first = random.choice(_FIRST_NAMES)
        last = random.choice(_LAST_NAMES)
        sep = random.choice([".", "_", ""])
        num = random.randint(1, 99999)
        style = random.randint(0, 3)
        if style == 0:
            local = f"{first}{sep}{last}{num}"
        elif style == 1:
            local = f"{first}{sep}{last}{sep}{num}"
        elif style == 2:
            local = f"{first}{num}"
        else:
            local = f"{first}{sep}{last}"
        # sirf valid email chars
        local = re.sub(r"[^a-z0-9._]", "", local.lower()).strip("._") or f"{first}{num}"
        email = f"{local}@{EMAIL_DOMAIN}"
        if email not in _used_emails:
            _used_emails.add(email)
            return first.capitalize(), email
    # extreme fallback (kabhi nahi aayega)
    rand = "".join(random.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(8))
    email = f"user{rand}@{EMAIL_DOMAIN}"
    _used_emails.add(email)
    return "User", email


# =====================================
# SMALL HELPERS
# =====================================
def to_10_digit(number):
    digits = re.sub(r"\D", "", number or "")
    return digits[-10:] if len(digits) >= 10 else digits


def clean_otp(otp):
    return re.sub(r"\D", "", str(otp or ""))


def extract_sms_otp(text):
    if not text:
        return ""
    m = re.search(r"(?<!\d)(\d{6})(?!\d)", text)
    if m:
        return m.group(1)
    m = re.search(r"(?<!\d)(\d{4,8})(?!\d)", text)
    return m.group(1) if m else ""


# =====================================
# RECORD SAVE  — DATABASE
# =====================================
# The Google Sheet and the CSV fallback are gone. A sheet needs credentials on every
# box, rate-limits once a fleet is appending to it, and cannot be joined against the
# task queue. The CSV was worse: several slots on one box appending to one file.
#
# `mobile` is unique in nykaa_accounts, so a retry that re-uses a number cannot create
# a second row (ON CONFLICT DO NOTHING).


def _save_record_sync(record):
    """Blocking DB write — runs in an executor. Never raises: an account that was
    genuinely created must not be reported as failed just because the insert hiccuped,
    and the row is still recoverable from the log."""
    try:
        import db
        rid = db.save_nykaa_account(record,
                                    ran_by=getattr(nk, "INSTANCE", None) or None,
                                    task_id=record.get("task_id"))
        if rid:
            print(f"[DB] ✅ account saved (id {rid}) -> {record.get('email')}")
        else:
            print(f"[DB] duplicate mobile {record.get('mobile')} — pehle se hai, skip")
    except Exception as e:
        print(f"[DB] ❌ save failed for {record.get('mobile')}: {e}")
        print(f"[DB] record: {json.dumps(record, ensure_ascii=False)}")


async def save_record(record):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _save_record_sync, record)


async def save_session(context, mobile, email):
    """Session waise hi sessions/<mobile>.json me store hota hai."""
    try:
        session_path = os.path.join(SESSIONS_DIR, f"{mobile}.json")
        state = await context.storage_state()
        with open(session_path, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        print(f"[SESSION] 💾 Saved: {mobile}.json")
        return os.path.basename(session_path)
    except Exception as e:
        print(f"[SESSION] Error: {e}")
        return None


# =====================================
# SMSINDIA API
# =====================================
def _api_get_sync(url):
    req = urllib.request.Request(url, headers={"Accept": "text/plain", "User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read().decode("utf-8", "ignore").strip()
    except Exception as e:
        return f"HTTP_ERROR:{e}"


async def sms_api(action, **params):
    q = {"api_key": SMSINDIA_API_KEY, "action": action}
    q.update({k: v for k, v in params.items() if v is not None})
    url = SMSINDIA_BASE + "?" + urllib.parse.urlencode(q)
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _api_get_sync, url)


async def sms_buy():
    for i in range(1, STOCK_WAIT_RETRIES + 1):
        resp = await sms_api("getNumber", service=SERVICE, country=COUNTRY,
                             operator=OPERATOR or None, maxPrice=None)
        # BAD_COUNTRY / BAD_OPERATOR frequently mean "this OPERATOR is not valid for
        # this country+service" — the API reports the country, not the operator. The
        # same request without the operator usually goes through, so try that once
        # before spending a retry or failing the account.
        if resp.startswith("BAD_") and OPERATOR:
            print(f"[SMS] {resp} with operator={OPERATOR} — bina operator ke retry")
            resp = await sms_api("getNumber", service=SERVICE, country=COUNTRY,
                                 maxPrice=None)
        if resp.startswith("ACCESS_NUMBER:"):
            parts = resp.split(":")
            return parts[1], parts[2]
        if "NO_BALANCE" in resp:
            raise RuntimeError("smsindia balance khatam (recharge karo).")
        if "NO_NUMBERS" in resp:
            print(f"[SMS] Stock 0. Waiting {STOCK_WAIT_SECONDS}s... ({i}/{STOCK_WAIT_RETRIES})")
            if i < STOCK_WAIT_RETRIES:
                await asyncio.sleep(STOCK_WAIT_SECONDS)
                continue
            return None, None
        print(f"[SMS] Buy failed: {resp}  "
              f"(service={SERVICE} country={COUNTRY} operator={OPERATOR or '-'})")
        return None, None
    return None, None


async def sms_get_otp(activation_id):
    for attempt in range(1, OTP_MAX_RETRIES + 1):
        await asyncio.sleep(OTP_POLL_INTERVAL)
        resp = await sms_api("getStatus", id=activation_id)
        if resp.startswith("STATUS_OK"):
            raw = resp.split(":", 1)[1] if ":" in resp else ""
            return extract_sms_otp(raw)
        if "STATUS_CANCEL" in resp or "NO_ACTIVATION" in resp:
            return None
        print(f"[SMS] Waiting OTP... {attempt}/{OTP_MAX_RETRIES}")
    return None


async def sms_cancel(activation_id):
    await sms_api("setStatus", status="8", id=activation_id)


# =====================================
# EMAIL OTP (Cloudflare Worker)
# =====================================
def _worker_get_sync(url):
    req = urllib.request.Request(url, headers={
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    })
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read().decode("utf-8", "ignore"))
    except Exception as e:
        return {"error": str(e)}


# Resend. Pehle ye loop 7 minute tak chup baitha rehta tha: agar mail pehli baar me nahi
# aaya to aur 6 minute wait karne se kuch nahi badalta tha, aur account partial reh jaata
# tha — jabki screen par "Resend OTP" ka button maujood hota hai. Ab har RESEND_AFTER
# second baad ek baar dabaya jaata hai, zyada se zyada MAX_RESENDS baar.
RESEND_AFTER = int(os.environ.get("NYKAA_EMAIL_RESEND_AFTER", 90))    # seconds
MAX_RESENDS  = int(os.environ.get("NYKAA_EMAIL_MAX_RESENDS", 3))

# Nykaa ka asli DOM (screen se liya gaya):
#     <div aria-hidden="true">Resend OTP on <button aria-label="SMS">SMS</button></div>
# Yaani dabane wali cheez par "Resend OTP" likha hi NAHI hai — wo text ek aria-hidden div
# me hai, aur button ka naam sirf "SMS" hai. Isliye "Resend OTP" wale selectors kabhi
# match hi nahi karte the aur resend chalta hua dikhta tha par hota nahi tha.
_RESEND_SELECTORS = [
    'button[aria-label="SMS"]',
    'button[aria-label="WhatsApp"]',          # kuch screens par ye vikalp bhi hota hai
    'button:has-text("SMS")',
    r"text=/^\s*resend\s*otp\s*$/i",          # agar Nykaa aage jaake DOM badle
]

# Timer chalte waqt ye line nahi hoti; timer khatam hone par page khud likhta hai.
_RESEND_READY = "You can now resend"


async def _try_resend(page):
    """Screen par resend dabane layak ho to daba do. Kabhi raise nahi karta — resend na
    ho paana OTP ke wait ko rokna nahi chahiye."""
    # Timer abhi chal raha ho to click bekaar jaata hai; agli baari me phir dekhenge.
    try:
        body = (await page.inner_text("body")) or ""
        if _RESEND_READY.lower() not in body.lower():
            return False
    except Exception:
        pass                                   # padha na ja sake to click try kar lo

    for sel in _RESEND_SELECTORS:
        try:
            loc = page.locator(sel).first
            if await loc.count() == 0:
                continue
            if not await loc.is_visible() or not await loc.is_enabled():
                continue
            await loc.click(timeout=5000)
            return True
        except Exception:
            continue
    return False


async def fetch_email_otp(email, page=None):
    print(f"[MAIL] {email} pe email OTP ka wait...")
    waited = 0
    resends = 0
    for attempt in range(1, EMAIL_OTP_RETRIES + 1):
        await asyncio.sleep(EMAIL_OTP_INTERVAL)
        waited += EMAIL_OTP_INTERVAL
        url = WORKER_OTP_URL + "?email="test@example.com"&token="CHANGE_ME_TOKEN"otp"):
            code = clean_otp(data["otp"])
            print(f"[MAIL] ✅ Email OTP mila: {code}")
            return code
        print(f"[MAIL] email OTP wait {attempt}/{EMAIL_OTP_RETRIES}")

        if page is not None and resends < MAX_RESENDS and waited >= RESEND_AFTER * (resends + 1):
            if await _try_resend(page):
                resends += 1
                print(f"[MAIL] 🔁 Resend OTP dabaya ({resends}/{MAX_RESENDS}) — "
                      f"{waited}s ho gaye the")
            else:
                # timer abhi chal raha hoga; agle round me phir dekhenge
                resends += 0
    return None


# =====================================
# NYKAA — SESSION RESET (fresh account)
# =====================================
async def nykaa_reset_session(context, page):
    """Har naye account se pehle: cookies + storage clear -> account1 ka data hat jaaye."""
    print("[NK] 🔄 Fresh session reset (cookies + storage clear)...")
    try:
        await context.clear_cookies()
    except Exception as e:
        print(f"[NK] (clear_cookies: {e})")
    # Residential proxies drop connections; a page that did not load is a NETWORK
    # failure, not this account's fault. It used to be swallowed here and the flow
    # marched on to "Mobile input nahi mila" — spending a bought SMS number on a browser
    # that was never on the site. Retry, then hand it to the runner as an InfraError so
    # the number is cancelled and the queue row goes back.
    last = None
    for attempt in range(1, 4):
        try:
            await page.goto("https://www.nykaa.com/", timeout=nk.NAV_TIMEOUT,
                            wait_until="domcontentloaded")
            await page.evaluate("() => { try { localStorage.clear(); sessionStorage.clear(); } catch(e){} }")
            await page.reload(wait_until="domcontentloaded")
            last = None
            break
        except Exception as e:
            last = str(e).split("\n")[0][:160]
            print(f"[NK] (reset load {attempt}/3: {last})")
            if attempt < 3:
                await asyncio.sleep(5)
    if last:
        raise nk.InfraError(f"nykaa.com load nahi hua (proxy/network): {last}")
    await page.wait_for_timeout(3000)


# =====================================
# NYKAA — MOBILE FIELD (robust: click + hard-clear + type + VERIFY + retry)
# =====================================
_MOBILE_SELECTORS = [
    'input[aria-label="Mobile Number"]',
    'input[type="tel"]',
    'input.css-1ytd58c[type="tel"]',
]


async def _find_mobile_input(page):
    """Sign-in modal ka mobile input handle dhoondo (visible wala)."""
    for _ in range(20):   # ~20s: modal/animation ke liye
        for sel in _MOBILE_SELECTORS:
            try:
                el = await page.query_selector(sel)
                if el and await el.is_visible():
                    return el
            except Exception:
                continue
        await page.wait_for_timeout(1000)
    return None


async def set_mobile_number(page, mobile_10):
    """
    Mobile field me number RELIABLY daalo:
      - input dhoondo (visible)
      - click (force) -> focus
      - HARD clear (keyboard + native value setter, taaki purana/autofill number hate)
      - digit-by-digit type
      - VERIFY: field me sach me wahi 10 digit? nahi -> dobara (max 4 try)
    Return True/False.
    """
    el = await _find_mobile_input(page)
    if el is None:
        print("[NK] ❌ Mobile input field nahi mila.")
        return False

    for attempt in range(1, 5):
        try:
            # focus (force click overlay/animation ke bawajood)
            try:
                await el.click(force=True, timeout=5000)
            except Exception:
                await el.evaluate("e => e.focus()")
            await page.wait_for_timeout(150)

            # hard clear: select-all + delete
            await page.keyboard.press("Control+A")
            await page.keyboard.press("Delete")
            # native setter se value '' + React ko input event (autofill/purana number saaf)
            await el.evaluate("""e => {
                const setter = Object.getOwnPropertyDescriptor(
                    window.HTMLInputElement.prototype, 'value').set;
                setter.call(e, '');
                e.dispatchEvent(new Event('input',  {bubbles: true}));
                e.dispatchEvent(new Event('change', {bubbles: true}));
            }""")
            await page.wait_for_timeout(150)

            # type digit-by-digit (React onChange trigger hota rahe)
            await el.type(mobile_10, delay=90)
            await page.wait_for_timeout(400)

            # VERIFY: field me kya hai?
            try:
                val = await el.input_value()
            except Exception:
                val = await el.evaluate("e => e.value")
            got = to_10_digit(val or "")
            if got == mobile_10:
                print(f"[NK] 📱 Mobile set + verified: {mobile_10}")
                return True
            print(f"[NK] ⚠️ Mobile mismatch (field='{val}', chahiye {mobile_10}) "
                  f"-> retry {attempt}/4")
            # agar element stale ho gaya to dobara dhoondo
            el = await _find_mobile_input(page) or el
        except Exception as e:
            print(f"[NK] mobile set error (try {attempt}): {e}")
            el = await _find_mobile_input(page) or el
        await page.wait_for_timeout(500)

    print(f"[NK] ❌ Mobile number {mobile_10} set nahi ho paya (4 try ke baad).")
    return False


async def _click_get_or_send_otp(page):
    """Nykaa kabhi 'Get OTP', kabhi 'Send OTP' -> dono handle."""
    clicked = await page.evaluate(r"""()=>{
        const norm = s => (s||'').replace(/\s+/g,' ').trim().toLowerCase();
        const bs = [...document.querySelectorAll('button,[role=button]')]
                   .filter(x => x.offsetParent !== null);
        let b = bs.find(x => norm(x.textContent) === 'get otp' || norm(x.textContent) === 'send otp')
             || bs.find(x => /\b(get|send)\s*otp\b/.test(norm(x.textContent)));
        if (b) { b.scrollIntoView({block:'center'}); b.click(); return norm(b.textContent); }
        return null;
    }""")
    return clicked


async def _otp_screen_present(page):
    try:
        return (await page.query_selector(nk.OTP_DIGIT(1))) is not None
    except Exception:
        return False


async def nykaa_signin_and_send_otp(page, mobile_10):
    """Sign in -> mobile (verify) -> Get/Send OTP -> OTP screen aane tak."""
    # Sign in button (fresh session me hamesha dikhega)
    if await page.query_selector(nk.SIGN_IN_BTN) is None:
        print("[NK] ⚠️ 'Sign in' nahi mila (shayad logout nahi hua) -> reset ke baad bhi.")
    else:
        await page.click(nk.SIGN_IN_BTN, timeout=nk.PW_TIMEOUT)
        await page.wait_for_timeout(2500)

    # Mobile daalo (verify + retry)
    if not await set_mobile_number(page, mobile_10):
        raise RuntimeError("Mobile input set fail")

    clicked = await _click_get_or_send_otp(page)
    print(f"[NK] OTP button clicked: {clicked}")

    # OTP screen aane ka poll; warna mobile screen wapas -> dobara daalo
    for _ in range(3):
        for _ in range(12):
            if await _otp_screen_present(page):
                print("[NK] ✅ OTP screen mil gaya.")
                return True
            await page.wait_for_timeout(1000)
        # 12s me OTP screen nahi -> mobile screen wapas hai kya?
        again = await _find_mobile_input(page)
        if again:
            print("[NK] 🔁 Mobile screen wapas -> number DOBARA + Get/Send OTP...")
            await set_mobile_number(page, mobile_10)
            await _click_get_or_send_otp(page)
        else:
            await page.wait_for_timeout(3000)

    await nk.wait_for_otp_screen(page)
    return True


# =====================================
# NYKAA — SIGNUP FORM (name + email + email OTP)
# =====================================
async def nykaa_complete_account(page, context, mobile_10):
    """Return: ("created", (name,email)) / ("existing", None) / ("failed", None)."""
    if not await nk.wait_for_signup_form(page):
        if await page.query_selector(nk.SIGN_IN_BTN) is None:
            print("[NK] Number PEHLE SE registered -> naya account nahi bana.")
            return "existing", None
        return "failed", None

    name, email = generate_identity()
    print(f"[NK] 🆕 Signup -> Name: {name} | Email: {email}")

    name_sel = await nk.find_present(page, nk.NAME_INPUTS)
    if name_sel:
        await page.click(name_sel)
        await page.type(name_sel, name, delay=80)
        await page.wait_for_timeout(600)

    email_sel = await nk.find_present(page, nk.EMAIL_INPUTS)
    if not email_sel:
        try:
            # mobile OTP ke baad ka wait -> lamba wala, kyunki number kharch ho chuka hai
            await page.wait_for_selector(nk.EMAIL_INPUTS[0], timeout=nk.POST_OTP_TIMEOUT)
            email_sel = nk.EMAIL_INPUTS[0]
        except Exception:
            email_sel = None
    if email_sel:
        await page.click(email_sel)
        await page.type(email_sel, email, delay=80)
        await page.wait_for_timeout(600)
        await page.keyboard.press("Tab")
        await page.wait_for_timeout(1200)

    await nk.robust_click(page, nk.YES_PROCEED_BTN, text="Yes, Proceed", label="Yes, Proceed")
    await page.wait_for_timeout(2500)

    # Yahan tak aa gaye to number verify ho chuka hai aur account BAN CHUKA hai — sirf
    # email verify hona baaki hai. Pehle yahan se aage koi bhi rukawat poore account ko
    # fail kar deti thi: session save hi nahi hota tha, to khareeda hua number aur bana
    # hua account dono bekaar. Ab aisi rukawat "partial" hai, "failed" nahi — caller
    # session save karega taaki account kaam ka rahe.
    try:
        # POST_OTP_TIMEOUT (10 min), PW_TIMEOUT (2 min) nahi — number kharch ho chuka hai
        await nk.wait_for_otp_screen(page, timeout=nk.POST_OTP_TIMEOUT)
    except Exception as e:
        print(f"[NK] ⚠️ Email OTP screen nahi aayi: {str(e).splitlines()[0][:90]}")
        await nk.dump_page(page, "email_otp_screen")
        return "partial", (name, email)

    email_code = await fetch_email_otp(email, page)
    if not email_code:
        print("[NK] ❌ Email OTP nahi mila — account bana hua hai, session bacha rahe hain.")
        return "partial", (name, email)

    # 7 minute tak page ko haath nahi lagaya gaya — is beech Nykaa tab replace kar sakta
    # hai. Purane handle pe seedha type karne se "Target page has been closed" milta tha.
    page = nk.live_page(context, page)
    await nk.fill_otp(page, email_code)
    await page.wait_for_timeout(5000)
    return "created", (name, email)


# =====================================
# SINGLE ACCOUNT  (GUI isko call karta hai)
# =====================================
async def create_single_account(semaphore):
    async with semaphore:
        async with async_playwright() as p:
            # Browser se connect — Chrome band/crash ho to clean False (GUI retry karega)
            try:
                browser, context, page = await nk.launch_browser(p)
            except nk.InfraError:
                # Box problem, not this account's — let it reach the fleet runner so the
                # queue row goes BACK instead of being spent.
                raise
            except Exception as e:
                print(f"[ERR] Browser setup nahi hua ({e}) — retry hoga.")
                return False

            activation_id = None
            try:
                activation_id, phone = await sms_buy()
                if not activation_id:
                    print("[SMS] Number nahi mila.")
                    return False

                mobile_10 = to_10_digit(phone)
                print(f"[SMS] NUMBER MILA: {mobile_10}  (id {activation_id})")

                # FRESH session -> account1 ka number/login hat jaaye
                await nykaa_reset_session(context, page)
                await nykaa_signin_and_send_otp(page, mobile_10)

                code = await sms_get_otp(activation_id)
                if not code:
                    print(f"[SMS] ⏰ {mobile_10} pe OTP nahi aaya -> cancel.")
                    await sms_cancel(activation_id)
                    return False

                print(f"[SMS] ✅ MOBILE OTP: {code}")
                await nk.fill_otp(page, code)
                await page.wait_for_timeout(4000)

                result, ident = await nykaa_complete_account(page, context, mobile_10)

                if result == "created":
                    name, email = ident
                    session_file = await save_session(context, mobile_10, email)
                    record = {
                        "mobile": mobile_10,
                        "name": name,
                        "email": email,
                        "session_file": session_file or f"{mobile_10}.json",
                        "created_at": datetime.now().isoformat(timespec="seconds"),
                    }
                    await save_record(record)
                    print(f"🎉 ACCOUNT CREATED: {mobile_10}  ({email})")
                    return True

                if result == "existing":
                    print("[NK] Number already registered -> agla number.")
                    return False

                print("[NK] Account step adhoora.")
                return False

            except RuntimeError as e:
                print(f"[STOP] {e}")
                if activation_id:
                    await sms_cancel(activation_id)
                raise
            except Exception as e:
                print(f"[ERR] {e}")
                if activation_id:
                    await sms_cancel(activation_id)
                return False


# =====================================
# MAIN (standalone; GUI ke bina bhi chalta hai)
# =====================================
async def main():
    print("=" * 70)
    print("NYKAA ACCOUNT CREATOR  (SMSINDIA + Postgres)")
    print(f"Target: {MAX_ACCOUNTS} | Concurrent: {CONCURRENT_SESSIONS}")
    print("=" * 70)

    resp = await sms_api("getBalance")
    print(f"[SMS] Balance: {resp}")

    nk.launch_real_chrome()

    semaphore = asyncio.Semaphore(CONCURRENT_SESSIONS)
    created = 0
    attempts = 0
    max_attempts = MAX_ACCOUNTS * 4 + 15

    while created < MAX_ACCOUNTS and attempts < max_attempts:
        attempts += 1
        print(f"\n===== ACCOUNT {created + 1}/{MAX_ACCOUNTS}  (attempt #{attempts}) =====")
        try:
            nk.launch_real_chrome()
            ok = await create_single_account(semaphore)
        except RuntimeError as e:
            print(f"[STOP] {e}")
            break
        except Exception as e:
            print(f"[ERR] {e}")
            ok = False
        if ok:
            created += 1
            print(f"[OK] {created}/{MAX_ACCOUNTS}")
        else:
            await asyncio.sleep(3)

    print(f"\n🎊 FINISHED! Total accounts created: {created}/{MAX_ACCOUNTS}")


if __name__ == "__main__":
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except Exception:
        pass
    asyncio.run(main())
