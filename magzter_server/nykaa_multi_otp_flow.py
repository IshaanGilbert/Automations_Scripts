import os
import sys
import time
import json
import asyncio
import urllib.parse
import urllib.request
import urllib.error

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

if getattr(sys, "frozen", False):
    ROOT = os.path.dirname(sys.executable)
else:
    ROOT = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, ROOT)

import nykaa_login as nk
import nykaa_smsindia_flow as sf          # smsindia + saara nykaa/email/sheet logic (reuse)
# Prefer patchright (stealth/undetected Playwright) if present; else plain playwright —
# same as buyer.py / source.py. Nykaa fingerprints hard, so the stealth build matters.
try:
    from patchright.async_api import async_playwright
    _ENGINE = "patchright"
except ImportError:
    from playwright.async_api import async_playwright
    _ENGINE = "playwright"

# GUI compatibility (balance check waise ka waisa)
sms_api = sf.sms_api


# =====================================
# CONFIG
# =====================================
MAX_ACCOUNTS = 200
CONCURRENT_SESSIONS = 1

# Provider order (pehla primary, doosra fallback). Toggle inhi ke beech hota hai.
PROVIDER_ORDER = ["smsindia", "techyindia"]

# ---- techyindia ----
TECHY_BASE = "https://api.techyindia.org"
TECHY_EMAIL = "test@example.com"
TECHY_PASSWORD = "CHANGE_ME_PASSWORD"
# Nykaa (serviceId, server) — server 2 (Operator2) sabse acha deliver karta hai, pehle wahi.
TECHY_NYKAA_SERVERS = [
    ("69ce4383ef5b0596887baec9", "2"),   # Nykaa  ₹10  (Operator2 - best)
    ("69aa7837eb35fa0f1a685e01", "5"),   # Nykaa  ₹8
    ("69d0c0085c9ea1730e955c1f", "3"),   # Nykaa - Beauty ₹11
    ("681e77cfa86ef3156ea05c12", "7"),   # Nykaa  ₹12
]
# techyindia OTP poll. (Test se: asli OTP ~2 min me aa jaata hai; dud number 'pending'
#  reh jaata hai -> wait khatam hone par smsindia fallback pe chala jaata hai.)
# Wait dashboard se (Settings -> Nykaa -> "techyindia OTP wait").
TECHY_OTP_INTERVAL = 15
TECHY_OTP_WAIT_MIN = sf._nk_setting("techy_otp_wait_min", 4)
TECHY_OTP_RETRIES  = max(1, int(TECHY_OTP_WAIT_MIN * 60 / TECHY_OTP_INTERVAL))

# Mobile OTP resend ka schedule — seconds, OTP bhejne ke baad se. Nykaa attempts ginta
# hai, isliye 4 se upar mat le jaana.
def _resend_schedule():
    """90s aur 180s par shuruaati koshish, phir wait window ke AAKHRI hisse me do aur.
    Aakhri wale window se nikale jaate hain, fix nahi — warna SMS wait 12 minute se
    ghata kar 6 kar do to 570/660 kabhi aate hi nahi aur aakhir wali koshish gayab ho
    jaati. NYKAA_SMS_RESEND_AT set ho to wahi chalega."""
    raw = os.environ.get("NYKAA_SMS_RESEND_AT", "").strip()
    if raw:
        return sorted({int(x) for x in raw.split(",") if x.strip()})
    window = sf.OTP_MAX_RETRIES * sf.OTP_POLL_INTERVAL          # seconds
    late = [int(window * 0.79), int(window * 0.92)]             # ~19/24 aur ~22/24
    return sorted({t for t in [90, 180] + late if 30 <= t < window})


SMS_RESEND_AT = _resend_schedule()



# =====================================
# techyindia HTTP (urllib, sync -> executor)
# =====================================
_techy_token = None


def _techy_http(path, method="GET", body=None, token=None):
    url = TECHY_BASE + path
    data = json.dumps(body).encode("utf-8") if body is not None else None
    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    }
    if data is not None:
        headers["Content-Type"] = "application/json"
    if token:
        headers["authorization"] = token
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode("utf-8", "ignore"))
    except urllib.error.HTTPError as e:
        # Wajah hamesha BODY me hoti hai ("insufficient balance", "service not found"),
        # par log me sirf "HTTP Error 400: Bad Request" chhapta tha aur body phenk di
        # jaati thi. e.code waise ka waisa rehta hai, to _techy_authed ka re-login wala
        # retry pehle jaisa hi chalta rahega.
        try:
            body = e.read().decode("utf-8", "ignore").strip()[:300]
        except Exception:
            body = ""
        if body:
            e.msg = f"{e.msg} — {body}"
        raise


def _techy_login_sync():
    global _techy_token
    resp = _techy_http("/users/login", "POST", {
        "email": TECHY_EMAIL, "password": TECHY_PASSWORD,
        "flag": True, "session": int(time.time() * 1000),
    })
    _techy_token = resp.get("token")
    return _techy_token


def _techy_token_get():
    return _techy_token or _techy_login_sync()


def _techy_authed(path, method="GET", body=None):
    """
    Authed call — 401/403/409 (single-session ka conflict) aaye to ek baar
    RE-LOGIN karke retry. techyindia sirf latest login ke token ko valid rakhta hai.
    """
    tok = _techy_token_get()
    try:
        return _techy_http(path, method, body, token=tok)
    except urllib.error.HTTPError as e:
        if e.code in (401, 403, 409):
            tok = _techy_login_sync()
            return _techy_http(path, method, body, token=tok)
        raise


def _techy_buy_sync():
    """Nykaa number generate (servers ek-ek try). Return handle dict ya None."""
    for sid, srv in TECHY_NYKAA_SERVERS:
        try:
            d = _techy_authed("/mobile/generate", "POST", {"serviceId": sid, "server": srv})
        except Exception as e:
            d = {"message": str(e), "isNumberGenerated": False}
        if isinstance(d, dict) and d.get("isNumberGenerated") and d.get("mobile"):
            m = d["mobile"][0]
            return {"mobileno": m.get("mobileno", ""),
                    "serialNumber": m.get("serialNumber", ""),
                    "mobileId": m.get("_id", ""),
                    "server": srv}
        msg = d.get("message", "") if isinstance(d, dict) else str(d)
        print(f"[techyindia] srv{srv}: {msg}")
    return None


def _techy_find_otp_sync(mobileno):
    try:
        d = _techy_authed("/otp/mobile-history?limit=10&page=1&time=all")
    except Exception as e:
        print(f"[techyindia] history error: {e}")
        return None
    for row in (d.get("data", []) or []):
        if row.get("mobileno") == mobileno:
            for o in (row.get("otpIds", []) or []):
                code = sf.extract_sms_otp(o.get("otpMessage", ""))
                if code:
                    return code
    return None


def _techy_cancel_sync(handle):
    try:
        _techy_authed("/otp/cancelOtp", "POST", {
            "serialNumber": handle.get("serialNumber", ""),
            "mobileno": handle.get("mobileno", ""),
            "mobileId": handle.get("mobileId", ""),
        })
    except Exception as e:
        print(f"[techyindia] cancel error: {e}")


# =====================================
# PROVIDER: async wrappers (dono ka same interface)
#   buy()      -> {"phone": <10digit>, ...} ya None
#   get_otp(h) -> code ya None
#   cancel(h)  -> None
# =====================================
async def _run(fn, *a):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, fn, *a)


# ---- smsindia (nykaa_smsindia_flow ka logic AS-IS) ----
async def smsindia_buy():
    try:
        activation_id, phone = await sf.sms_buy()
    except RuntimeError as e:      # balance khatam etc. -> is provider ko fail maano
        print(f"[smsindia] {e}")
        return None
    if not activation_id:
        return None
    return {"phone": sf.to_10_digit(phone), "handle": activation_id}


async def smsindia_get_otp(h):
    return await sf.sms_get_otp(h["handle"])


async def smsindia_cancel(h):
    try:
        await sf.sms_cancel(h["handle"])
    except Exception:
        pass


# ---- techyindia ----
async def techy_buy():
    h = await _run(_techy_buy_sync)
    if not h:
        return None
    h["phone"] = sf.to_10_digit(h["mobileno"])
    print(f"[techyindia] number: {h['phone']}  (server {h['server']})")
    return h


async def techy_get_otp(h):
    for attempt in range(1, TECHY_OTP_RETRIES + 1):
        await asyncio.sleep(TECHY_OTP_INTERVAL)
        code = await _run(_techy_find_otp_sync, h["mobileno"])
        if code:
            return code
        print(f"[techyindia] OTP wait {attempt}/{TECHY_OTP_RETRIES}")
    return None


async def techy_cancel(h):
    await _run(_techy_cancel_sync, h)


PROVIDERS = {
    "smsindia":   {"buy": smsindia_buy, "get_otp": smsindia_get_otp, "cancel": smsindia_cancel},
    "techyindia": {"buy": techy_buy,     "get_otp": techy_get_otp,     "cancel": techy_cancel},
}

# ---- provider ka chunaav: dashboard se, per instance ----
# Settings -> Nykaa me teen cheezein aati hain:
#   provider : "auto" | "smsindia" | "techyindia"
#   fallback : ek provider fail kare to doosre par jaana hai ya nahi
# "auto" me har instance ka apna primary hota hai — instance 1 smsindia se, instance 2
# techyindia se, 3 phir smsindia... — taaki ek hi provider par poora fleet na toot pade
# aur dono ka stock saath me use ho. Ye har launch par padha jaata hai, isliye dashboard
# se badalne ke baad slot restart karna kaafi hai, deploy nahi.
def _nykaa_settings():
    try:
        from settings_util import load_settings
        return load_settings("nykaa") or {}
    except Exception:
        return {}


def _chosen_providers(s):
    """Settings -> nykaa.providers. List bhi chal jaati hai aur comma wali string bhi.
    Khaali chhoda to sab use honge. Purani `provider` (ek hi naam) wali setting bhi
    padhi jaati hai, taaki upgrade par kisi ka chunaav gum na ho."""
    raw = s.get("providers")
    if isinstance(raw, (list, tuple)):
        picked = [str(x).strip().lower() for x in raw if str(x).strip()]
    elif isinstance(raw, str):
        picked = [x.strip().lower() for x in raw.split(",") if x.strip()]
    else:
        picked = []
    if not picked:                                   # purani setting se compatibility
        one = str(s.get("provider", "")).strip().lower()
        if one and one != "auto":
            picked = [one]

    known = [p for p in picked if p in PROVIDERS]
    unknown = [p for p in picked if p not in PROVIDERS]
    if unknown:
        print(f"[PROVIDER] '{', '.join(unknown)}' abhi maujood nahi — chhod diya")
    return known or list(PROVIDER_ORDER)             # kuch na chuna -> sab


def _provider_plan():
    """(order, fallback_on) — is instance ke liye providers kis kram me try honge.

    Chune hue providers ko instance ke hisaab se ghumaya jaata hai, taaki poora fleet ek
    hi provider par na toot pade: 2 chune hain to instance 1 pehle se, instance 2 doosre
    se shuru karega. Sirf 1 chuna hai to sab usi se chalenge, aur fallback ka koi matlab
    nahi rehta."""
    s = _nykaa_settings()
    fallback = s.get("fallback", True)
    fallback = str(fallback).strip().lower() not in ("false", "0", "no", "off")

    chosen = _chosen_providers(s)
    inst = int(getattr(nk, "INSTANCE", 0) or 0)
    shift = inst % len(chosen)
    order = chosen[shift:] + chosen[:shift]
    if not fallback:
        order = order[:1]                   # sirf primary, switch nahi
    return order, fallback


PROVIDER_PLAN, PROVIDER_FALLBACK = _provider_plan()

# provider rotation pointer (fail par aage badhta hai)
_prov_idx = 0


def _current_provider_name():
    return PROVIDER_PLAN[_prov_idx % len(PROVIDER_PLAN)]


def _rotate_provider():
    global _prov_idx
    if len(PROVIDER_PLAN) < 2:
        # fallback band hai — switch ka koi matlab nahi, warna log jhooth bolta hai
        print("[PROVIDER] fallback band hai -> usi provider se agli koshish.")
        return
    _prov_idx += 1
    print(f"[PROVIDER] switch -> ab '{_current_provider_name()}' se try hoga.")


# =====================================
# SINGLE ACCOUNT  (GUI isko call karta hai)
# =====================================
async def create_single_account(semaphore):
    async with semaphore:
        async with async_playwright() as p:
            try:
                browser, context, page = await nk.launch_browser(p)
            except nk.InfraError:
                # Box problem, not this account's — let it reach the fleet runner so the
                # queue row goes BACK instead of being spent.
                raise
            except Exception as e:
                print(f"[ERR] Browser setup nahi hua ({e}) — retry hoga.")
                return False

            pname = _current_provider_name()
            prov = PROVIDERS[pname]
            print(f"\n[PROVIDER] is attempt me OTP source: '{pname}'")

            handle = None
            try:
                handle = await prov["buy"]()
                if not handle:
                    print(f"[{pname}] number nahi mila.")
                    _rotate_provider()      # is provider se number/OTP nahi -> switch
                    return False

                mobile_10 = handle["phone"]
                print(f"[{pname}] NUMBER: {mobile_10}")

                # --- Nykaa: fresh session + number + send OTP (browser issue par no-rotate) ---
                try:
                    await sf.nykaa_reset_session(context, page)
                    await sf.nykaa_signin_and_send_otp(page, mobile_10)
                except Exception as e:
                    print(f"[NK] signin/send-otp issue: {e}")
                    await prov["cancel"](handle)
                    return False

                # --- provider se mobile OTP ---
                # Watch the BROWSER while waiting. sms_get_otp only polls an HTTP API —
                # it never touches the page — so a browser that died right after "Send
                # OTP" went unnoticed for the full 12-minute wait, and only surfaced as
                # "Target page... closed" at fill time. By then the SMS number is spent
                # and 12 minutes are gone. Bail the moment the page is gone.
                #
                # Isi loop me RESEND bhi. Pehla SMS operator ke level par gir jaana aam
                # hai, aur chup baithe rehne se 12 minute nikal jaate the aur number waise
                # hi kharch ho jaata tha. Resend ka koi extra paisa nahi lagta — number
                # pehle se rented hai aur provider kisi bhi SMS ka intezaar karta hai.
                # Ginti seemit hai: zyada baar dabane par Nykaa "too many attempts" laga
                # deta hai aur wahi number bekaar ho jaata hai.
                async def _otp_or_dead_browser():
                    otp_task = asyncio.create_task(prov["get_otp"](handle))
                    waited, done_n = 0, 0
                    pending = list(SMS_RESEND_AT)
                    while not otp_task.done():
                        done, _ = await asyncio.wait({otp_task}, timeout=15)
                        if done:
                            break
                        waited += 15
                        if page.is_closed() or not context.pages:
                            otp_task.cancel()
                            raise nk.InfraError(
                                "OTP ke wait ke dauraan page/browser band — "
                                + nk.close_state(browser, context, page))
                        if pending and waited >= pending[0]:
                            pending.pop(0)
                            try:
                                if await sf._try_resend(page):
                                    done_n += 1
                                    print(f"[NK] 🔁 Mobile OTP resend dabaya "
                                          f"({done_n}/{len(SMS_RESEND_AT)}) — {waited}s baad")
                                else:
                                    # button abhi timer me hai ("Resend OTP in 00:24") —
                                    # ye baari gawaao mat, 30s baad dobara dekho
                                    pending.insert(0, waited + 30)
                            except Exception:
                                pass
                    return otp_task.result()

                try:
                    code = await _otp_or_dead_browser()
                except nk.InfraError:
                    # Box problem: give the number back, and let the runner put the queue
                    # row back rather than spending it on a box whose browser died.
                    print("🛑 browser gayab — number cancel, task queue me wapas")
                    await prov["cancel"](handle)
                    raise
                if not code:
                    print(f"[{pname}] ⏰ OTP nahi aaya -> cancel + provider switch.")
                    await prov["cancel"](handle)
                    _rotate_provider()      # FALLBACK: agla attempt doosre provider se
                    return False

                print(f"[{pname}] ✅ MOBILE OTP: {code}")
                await nk.fill_otp(page, code)
                await page.wait_for_timeout(4000)

                # --- signup form + email OTP (reuse) ---
                result, ident = await sf.nykaa_complete_account(page, context, mobile_10)

                if result == "created":
                    name, email = ident
                    session_file = await sf.save_session(context, mobile_10, email)
                    record = {
                        "mobile": mobile_10, "name": name, "email": email,
                        "session_file": session_file or f"{mobile_10}.json",
                        "created_at": sf.datetime.now().isoformat(timespec="seconds"),
                    }
                    await sf.save_record(record)
                    print(f"🎉 ACCOUNT CREATED via {pname}: {mobile_10}  ({email})")
                    return True

                if result == "partial":
                    # Account Nykaa pe ban chuka hai, bas email verify nahi hua. Session
                    # yahin bacha lo — number kharch ho chuka hai, use bekaar mat jaane
                    # do. File ka naam alag rakha hai taaki poore verified accounts se
                    # chhaant sako.
                    name, email = ident
                    session_file = await sf.save_session(context, f"{mobile_10}_partial", email)
                    record = {
                        "mobile": mobile_10, "name": name, "email": email,
                        "session_file": session_file or f"{mobile_10}_partial.json",
                        "created_at": sf.datetime.now().isoformat(timespec="seconds"),
                    }
                    await sf.save_record(record)
                    print(f"⚠️  ACCOUNT BANA (email verify baaki): {mobile_10} ({email}) "
                          f"— session {session_file} save ho gaya")
                    return True

                if result == "existing":
                    print("[NK] Number already registered -> agla number (same provider).")
                    return False

                print("[NK] Account step adhoora.")
                return False

            except Exception as e:
                print(f"[ERR] {e}")
                print(f"[STATE] {nk.close_state(browser, context, page)}")
                # ek fail = ek khareeda hua number gaya. Screen save kar lo, warna agli
                # baar bhi sirf "element nahi mila" hi pata chalega, wajah nahi.
                try:
                    await nk.dump_page(page, "account")
                except Exception:
                    pass
                if handle:
                    await prov["cancel"](handle)
                return False


# =====================================
# MAIN (standalone)
# =====================================
async def main():
    print("=" * 72)
    print("NYKAA ACCOUNT CREATOR — MULTI-PROVIDER OTP (smsindia + techyindia)")
    print(f"Providers: {PROVIDER_ORDER}  | Target: {MAX_ACCOUNTS}")
    print("=" * 72)

    try:
        print(f"[smsindia] balance: {await sf.sms_api('getBalance')}")
    except Exception:
        pass
    try:
        tok = await _run(_techy_login_sync)
        bal = await _run(lambda: _techy_http('/payment/balance', token=tok))
        print(f"[techyindia] login OK, balance: {bal.get('balance')}")
    except Exception as e:
        print(f"[techyindia] login/balance issue: {e}")

    nk.launch_real_chrome()

    semaphore = asyncio.Semaphore(CONCURRENT_SESSIONS)
    created = 0
    attempts = 0
    max_attempts = MAX_ACCOUNTS * 5 + 15

    while created < MAX_ACCOUNTS and attempts < max_attempts:
        attempts += 1
        print(f"\n===== ACCOUNT {created + 1}/{MAX_ACCOUNTS}  (attempt #{attempts}) =====")
        try:
            nk.launch_real_chrome()
            ok = await create_single_account(semaphore)
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