"""
Magzter Order Reader
--------------------
Google Sheet se email/password uthata hai -> Magzter pe login -> My Orders page se
Transaction ID + Date nikaal kar usi row ke aage sheet me likh deta hai.

Multi-instance safe:
  * Machine-level partition : --instance-id / --total-instances  (row % total)
  * Worker-level claim lock : read_status cell me CLAIM token + read-back verify
  * Creds round-robin       : creds1..creds6.json (Google 60-write/min/account limit)
  * 429 backoff             : har sheet call _api() se, crash nahi hota

Run:
  python magzter_orders.py --headed --instances 2 --limit 3
  python magzter_orders.py --headless --instances 5
  python magzter_orders.py --headless --instances 5 --instance-id 2 --total-instances 3
"""

import asyncio
import argparse
import json
import logging
import os
import random
import re
import socket
import struct
import sys
import threading
import time
from datetime import datetime
from urllib.parse import quote

import gspread
from google.oauth2.service_account import Credentials

os.environ["TZ"] = "Asia/Calcutta"
try:
    time.tzset()
except Exception:
    pass


# ====================== PATHS (exe-safe) ======================
def base_dir():
    """PyInstaller exe ke saath bhi creds wahi folder se milen jahan exe rakha hai."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


BASE = base_dir()

# Browser kahan se uthana hai - ye playwright import se PEHLE set hona zaroori hai.
#   1) exe ke bagal me 'ms-playwright' folder rakha ho  -> wahi use karo
#   2) exe ke andar browsers bundle hain (.local-browsers) -> "0" matlab bundled
#   3) warna default: %LOCALAPPDATA%\ms-playwright (dev machine)
# Isi wajah se exe doosri machine pe bina 'playwright install' ke chal jata hai.
if not os.environ.get("PLAYWRIGHT_BROWSERS_PATH"):
    _external = os.path.join(BASE, "ms-playwright")
    if os.path.isdir(_external):
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = _external
    elif getattr(sys, "frozen", False):
        _bundled = os.path.join(getattr(sys, "_MEIPASS", BASE),
                                "playwright", "driver", "package", ".local-browsers")
        if os.path.isdir(_bundled):
            os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "0"   # 0 = driver ke andar wale browsers

from playwright.async_api import async_playwright  # noqa: E402


def p(name):
    """File dhoondo: pehle exe/script ke bagal me, phir exe ke andar bundled copy.
    Isse user creds ko exe ke saath rakh kar override bhi kar sakta hai."""
    outside = os.path.join(BASE, name)
    if os.path.exists(outside):
        return outside
    bundled = os.path.join(getattr(sys, "_MEIPASS", BASE), name)
    if os.path.exists(bundled):
        return bundled
    return outside


# ====================== ARGUMENTS ======================
DEFAULT_SHEET = "1_jYQTfb5BlyKCLCTGVqQA9XTND9OEFu1mZRPSXkSkb0"

parser = argparse.ArgumentParser(description="Magzter My-Orders reader -> Google Sheet")
parser.add_argument("--sheet-id", default=DEFAULT_SHEET, help="Google Sheet ID ya poora URL")
parser.add_argument("--tab", default="Sheet1", help="Worksheet/tab ka naam")
parser.add_argument("--instances", type=int, default=1, help="Is machine pe kitne browser parallel chalein")
parser.add_argument("--instance-id", type=int, default=1, help="Multi-machine setup me is machine ka number")
parser.add_argument("--total-instances", type=int, default=1, help="Total machines (row partition ke liye)")
parser.add_argument("--headed", dest="headed", action="store_true", help="Browser dikhega")
parser.add_argument("--headless", dest="headed", action="store_false", help="Browser chhupa rahega (default)")
parser.set_defaults(headed=False)
parser.add_argument("--limit", type=int, default=0, help="Sirf itni rows karo (0 = sab)")
parser.add_argument("--min-delay", type=int, default=3, help="Do accounts ke beech min second")
parser.add_argument("--max-delay", type=int, default=8, help="Do accounts ke beech max second")
parser.add_argument("--retry-failed", action="store_true", help="Pehle se FAILED rows dobara try karo")
parser.add_argument("--no-prompt", action="store_true", help="Interactive sawal mat poochho")
# ---- Geonode / koi bhi HTTP proxy ----
parser.add_argument("--proxy", dest="proxy", action="store_true", help="Proxy se chalao (config.json se settings)")
parser.add_argument("--no-proxy", dest="proxy", action="store_false", help="Proxy band, seedha apne IP se")
parser.set_defaults(proxy=None)     # None = config.json khud tay karega
parser.add_argument("--proxy-host", default=None, help="jaise sg.proxy.geonode.io")
parser.add_argument("--proxy-port", type=int, default=None, help="ek fix port (jaise 11000)")
parser.add_argument("--proxy-port-min", type=int, default=None, help="port range ka shuru (har browser alag IP)")
parser.add_argument("--proxy-port-max", type=int, default=None, help="port range ka aakhir")
parser.add_argument("--proxy-user", default=None)
parser.add_argument("--proxy-pass", default=None)
args = parser.parse_args()


# ====================== CONFIG.JSON ======================
def load_config():
    """config.json exe ke bagal me ho to usse settings uthao (proxy waghairah)."""
    f = p("config.json")
    try:
        with open(f, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {}


CONFIG = load_config()


def _cfg(key, cli, default=None):
    """CLI sabse upar, phir config.json, phir default."""
    if cli is not None:
        return cli
    return CONFIG.get(key, default)


PROXY_HOST = _cfg("PROXY_HOST", args.proxy_host, "")
PROXY_USERNAME = _cfg("PROXY_USERNAME", args.proxy_user, "")
PROXY_PASSWORD = _cfg("PROXY_PASSWORD", args.proxy_pass, "")
PROXY_PORT = int(_cfg("PROXY_PORT", args.proxy_port, 11000) or 11000)
PROXY_PORT_MIN = _cfg("PROXY_PORT_MIN", args.proxy_port_min, None)
PROXY_PORT_MAX = _cfg("PROXY_PORT_MAX", args.proxy_port_max, None)

# --proxy / --no-proxy diya ho to wahi; warna config.json me host hai to on.
USE_PROXY = args.proxy if args.proxy is not None else bool(CONFIG.get("USE_PROXY", bool(PROXY_HOST)))
USE_PROXY = bool(USE_PROXY and PROXY_HOST)


# Geonode ke HTTP gateway pe Chrome seedha nahi chalta (ClientHello bada hone se
# gateway "400 Bad Request" de deta hai). Isliye yahan ek chhota local HTTP-CONNECT
# proxy chalate hain jo aage SOCKS5 (username/password auth) se geonode ko jaata hai -
# Chrome sirf 127.0.0.1 se baat karta hai. Wahi tareeka jo v3 server me lagaya gaya tha.
class Socks5Tunnel:
    def __init__(self, host, port, user, pwd):
        self.host, self.port, self.user, self.pwd = host, port, user, pwd
        self.local_port, self.running, self.srv = None, False, None

    def _free_port(self):
        for _ in range(200):
            cand = random.randint(21000, 60000)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                s.bind(("127.0.0.1", cand))
                s.close()
                return cand
            except Exception:
                s.close()
        return None

    def _socks5(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(120)
        s.connect((self.host, int(self.port)))
        s.send(b"\x05\x01\x02")
        s.recv(2)
        u, w = self.user.encode(), (self.pwd or "").encode()
        s.send(b"\x01" + bytes([len(u)]) + u + bytes([len(w)]) + w)
        if s.recv(2) != b"\x01\x00":
            raise Exception("proxy auth fail")
        return s

    def _handle(self, client):
        remote = None
        try:
            remote = self._socks5()
            data = b""
            while b"\r\n\r\n" not in data:
                d = client.recv(4096)
                if not d:
                    return
                data += d
            req = data.decode("utf-8", errors="ignore")
            if not req.startswith("CONNECT"):
                return
            hostport = req.split(" ")[1]
            h, _, pt = hostport.rpartition(":")
            port = int(pt)
            remote.send(b"\x05\x01\x00\x03" + bytes([len(h)]) + h.encode() + struct.pack("!H", port))
            remote.recv(10)
            client.send(b"HTTP/1.1 200 Connection Established\r\n\r\n")

            def pump(src, dst):
                try:
                    while True:
                        d = src.recv(8192)
                        if not d:
                            break
                        dst.sendall(d)
                except Exception:
                    pass
                finally:
                    try:
                        dst.close()
                    except Exception:
                        pass

            t1 = threading.Thread(target=pump, args=(client, remote), daemon=True)
            t2 = threading.Thread(target=pump, args=(remote, client), daemon=True)
            t1.start()
            t2.start()
            t1.join(600)
            t2.join(600)
        except Exception:
            pass
        finally:
            for sk in (client, remote):
                try:
                    if sk:
                        sk.close()
                except Exception:
                    pass

    def start(self):
        self.local_port = self._free_port()
        if not self.local_port:
            raise Exception("Local port nahi mila (tunnel)")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("127.0.0.1", self.local_port))
        s.listen(16)
        s.settimeout(1)
        self.srv, self.running = s, True

        def accept():
            while self.running:
                try:
                    c, _ = s.accept()
                    threading.Thread(target=self._handle, args=(c,), daemon=True).start()
                except socket.timeout:
                    continue
                except Exception:
                    break
            try:
                s.close()
            except Exception:
                pass

        threading.Thread(target=accept, daemon=True).start()
        return self.local_port

    def stop(self):
        self.running = False
        try:
            if self.srv:
                self.srv.close()
        except Exception:
            pass


def gateway_port():
    """Port range ho to har browser alag gateway -> geonode alag residential IP deta hai."""
    if PROXY_PORT_MIN and PROXY_PORT_MAX and int(PROXY_PORT_MAX) >= int(PROXY_PORT_MIN):
        return random.randint(int(PROXY_PORT_MIN), int(PROXY_PORT_MAX))
    return PROXY_PORT


def start_tunnel():
    """Naya tunnel -> (playwright proxy dict, tunnel). Proxy off ho to (None, None)."""
    if not USE_PROXY:
        return None, None
    t = Socks5Tunnel(PROXY_HOST, gateway_port(), PROXY_USERNAME, PROXY_PASSWORD)
    lp = t.start()
    return {"server": f"http://127.0.0.1:{lp}"}, t


def interactive_setup():
    """exe ko double-click kiya aur koi flag nahi diya -> settings pooch lo."""
    print("=" * 58)
    print("            MAGZTER ORDER READER")
    print("=" * 58)
    try:
        m = input("Browser mode  [1] Headless (chhupa)  [2] Headed (dikhega) : ").strip()
        args.headed = (m == "2")
        n = input("Kitne instance parallel chalane hain? (1-10) [1]         : ").strip()
        args.instances = max(1, min(10, int(n))) if n else 1
        l = input("Kitni rows process karni hain? (0 = sab) [0]            : ").strip()
        args.limit = int(l) if l else 0
        print("-" * 58)
        print(f"Mode: {'HEADED' if args.headed else 'HEADLESS'} | Instances: {args.instances} | Limit: {args.limit or 'ALL'}")
        print("-" * 58)
    except (EOFError, KeyboardInterrupt):
        print("\nDefault settings se chala rahe hain...")
    except ValueError:
        print("Galat input - default settings use kar rahe hain.")


if getattr(sys, "frozen", False) and len(sys.argv) == 1 and not args.no_prompt:
    interactive_setup()

INSTANCE_ID = args.instance_id
TOTAL_INSTANCES = max(1, args.total_instances)
WORKERS = max(1, args.instances)

# ====================== LOGGING ======================
log_dir = p("logs")
os.makedirs(log_dir, exist_ok=True)
log_filename = os.path.join(log_dir, f"orders_i{INSTANCE_ID}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(log_filename, encoding="utf-8"), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("magzter")

# ====================== SHEET CONFIG ======================
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
NUM_ACCOUNTS = 6

_m = re.search(r"/d/([a-zA-Z0-9\-_]+)", args.sheet_id)
SPREADSHEET_ID = _m.group(1) if _m else args.sheet_id

COL_EMAIL = "test@example.com"
COL_PASS = "password"
OUT_COLS = ["transaction_id", "transaction_date", "read_status", "worker", "updated_at", "reason"]

CLAIM_STALE_SECONDS = 1800   # 30 min purana claim = dead worker, row wapas le lo
MAX_ATTEMPTS = 3


def creds_for(worker_no):
    """Machine + worker ka combo -> alag service account (rate limit spread)."""
    idx = ((INSTANCE_ID - 1) * WORKERS + (worker_no - 1)) % NUM_ACCOUNTS + 1
    f = p("creds{}.json".format(idx))
    if not os.path.exists(f):
        f = p("google_credentials.json")
    return f


def _api(fn, *a, **k):
    """Har sheet call yahan se - 429/5xx pe exponential backoff, crash nahi."""
    delay = 5
    last = None
    for attempt in range(6):
        try:
            return fn(*a, **k)
        except gspread.exceptions.APIError as e:
            last = e
            s = str(e)
            if "429" in s or "Quota exceeded" in s or "RATE_LIMIT" in s or "503" in s or "500" in s:
                wait = delay + random.uniform(0, 4)
                logger.warning(f"[RateLimit] backoff {wait:.0f}s (try {attempt + 1}/6)")
                time.sleep(wait)
                delay = min(delay * 2, 90)
                continue
            raise
    raise last


def open_sheet(worker_no=1):
    cf = creds_for(worker_no)
    with open(cf, "r", encoding="utf-8") as f:
        info = json.load(f)
    client = gspread.authorize(Credentials.from_service_account_info(info, scopes=SCOPES))
    ws = _api(lambda: client.open_by_key(SPREADSHEET_ID).worksheet(args.tab))
    logger.info(f"[Sheet] creds: {os.path.basename(cf)} ({info['client_email']})")
    return ws


def col_letter(n):
    s = ""
    while n > 0:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def ensure_output_columns(ws):
    """Header row me output columns na hon to end me jod do (data chhede bina)."""
    headers = _api(ws.row_values, 1)
    added = [c for c in OUT_COLS if c not in headers]
    if added:
        new_headers = headers + added
        rng = f"A1:{col_letter(len(new_headers))}1"
        _api(ws.update, values=[new_headers], range_name=rng)
        logger.info(f"[Sheet] Naye columns bane: {added}")
        headers = new_headers
    for c in (COL_EMAIL, COL_PASS):
        if c not in headers:
            raise SystemExit(f"[Error] Sheet me '{c}' column nahi hai. Headers: {headers}")
    return {h: i + 1 for i, h in enumerate(headers) if h}


def _claimable(val, retry_failed=False):
    val = (val or "").strip()
    if not val:
        return True
    up = val.upper()
    if up in ("DONE", "NO_ORDERS", "NOT_FOUND"):
        return False
    if up.startswith("FAILED"):
        return retry_failed
    if val.startswith("CLAIM:"):
        try:
            return (time.time() - int(val.split(":")[2])) > CLAIM_STALE_SECONDS
        except Exception:
            return True
    return False


def fetch_pending(ws):
    """Poori sheet ek call me padho -> is machine ki pending rows."""
    all_values = _api(ws.get_all_values)
    if not all_values:
        return []
    headers = all_values[0]
    ei = headers.index(COL_EMAIL)
    pi = headers.index(COL_PASS)
    si = headers.index("read_status") if "read_status" in headers else None
    ti = headers.index("transaction_id") if "transaction_id" in headers else None

    def cell(row, i):
        return str(row[i]).strip() if i is not None and i < len(row) else ""

    pending = []
    for n, row in enumerate(all_values[1:]):
        row_index = n + 2
        # machine-level partition: row 2->m2, row 3->m3 ... wrap around
        if TOTAL_INSTANCES > 1 and (row_index % TOTAL_INSTANCES) != (INSTANCE_ID % TOTAL_INSTANCES):
            continue
        email = cell(row, ei)
        if not email:
            continue
        if cell(row, ti):                                  # transaction pehle se hai
            continue
        if not _claimable(cell(row, si), args.retry_failed):
            continue
        pending.append({"row": row_index, "email": email, "password": cell(row, pi)})
    return pending


def claim_row(ws, cmap, row, worker_no):
    """Token likho -> 0.8s ruko -> wapas padho. Match = row humari, warna kisi aur ki."""
    col = cmap["read_status"]
    token = f"CLAIM:{INSTANCE_ID}.{worker_no}:{int(time.time())}"
    try:
        _api(ws.update_cell, row, col, token)
        time.sleep(0.8)
        current = str(_api(ws.cell, row, col).value or "").strip()
        if current == token:
            return True
        logger.info(f"[Claim] row {row} kisi aur ne le li ({current[:30]}) - skip")
        return False
    except Exception as e:
        logger.warning(f"[Claim] row {row} fail: {e}")
        return False


def write_result(ws, cmap, row, worker_no, txn_id, txn_date, status, reason=""):
    """Saare output cells EK hi batch call me - quota bachta hai."""
    idxs = [cmap[c] for c in OUT_COLS]
    lo, hi = min(idxs), max(idxs)
    values = [""] * (hi - lo + 1)
    data = {
        "transaction_id": txn_id,
        "transaction_date": txn_date,
        "read_status": status,
        "worker": f"{INSTANCE_ID}.{worker_no}",
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "reason": reason,
    }
    for c, v in data.items():
        values[cmap[c] - lo] = v
    rng = f"{col_letter(lo)}{row}:{col_letter(hi)}{row}"
    _api(ws.update, values=[values], range_name=rng)
    logger.info(f"[Sheet] row {row} <- {status} | txn={txn_id} | date={txn_date}")


def release_row(ws, cmap, row, note=""):
    try:
        _api(ws.update_cell, row, cmap["read_status"], note)
    except Exception as e:
        logger.warning(f"[Release] row {row}: {e}")


# ====================== BROWSER ======================
POPUP_KILL_JS = """
(function(){
  try {
    Object.defineProperty(window,'clevertap',{configurable:true,
      get:function(){return this.__ct;},
      set:function(nv){try{if(nv){nv.notifications=nv.notifications||{};nv.notifications.push=function(){};}}catch(e){}this.__ct=nv;}});
  } catch(e){}
  try { if (window.Notification) { Notification.requestPermission=function(cb){if(cb)cb('denied');return Promise.resolve('denied');}; } } catch(e){}
  function rm(){ try{ document.querySelectorAll('.wzrk-alert,.wzrk-overlay,.wzrk-backdrop,[id^="wzrk"],[class*="wzrk"]').forEach(function(el){el.remove();}); }catch(e){} }
  try { new MutationObserver(rm).observe(document.documentElement||document,{childList:true,subtree:true}); } catch(e){}
  document.addEventListener('DOMContentLoaded', rm);
  setInterval(rm, 800);
})();
"""

CLOSE_SELECTORS = [
    "#tooltipOkBtnD",
    "button.tooltip-ok",
    "button.jsx-a5473e9fc229b582.close-btn",
    'button:has-text("AGREE")',
    'button:has-text("Agree")',
]


async def dismiss_popups(page):
    for sel in CLOSE_SELECTORS:
        try:
            btn = page.locator(sel).first
            if await btn.count() and await btn.is_visible():
                await btn.click(timeout=3000)
                await page.wait_for_timeout(300)
        except Exception:
            pass


async def new_browser(pw, headed):
    # AHEM - headless me channel="chromium" zaroori hai.
    # Playwright ka default headless "headless_shell" hai, jise Magzter ka Akamai
    # 403 Access Denied de deta hai. channel="chromium" asli Chrome binary ko
    # --headless=new mode me chalata hai -> page normal khulta hai (status 200).
    launch_args = {
        "headless": not headed,
        "args": ["--disable-blink-features=AutomationControlled", "--no-sandbox", "--disable-dev-shm-usage"],
    }
    px, tunnel = await asyncio.to_thread(start_tunnel)
    if px:
        launch_args["proxy"] = px
    if not headed:
        launch_args["channel"] = "chromium"
    try:
        try:
            browser = await pw.chromium.launch(**launch_args)
        except Exception as e:
            if not headed:
                logger.warning(f"[Browser] channel=chromium nahi mila ({str(e)[:80]}) - default headless se try")
                launch_args.pop("channel")
                browser = await pw.chromium.launch(**launch_args)
            else:
                raise
        ctx = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"),
        )
        await ctx.add_init_script(POPUP_KILL_JS)
    except Exception:
        if tunnel:
            tunnel.stop()
        raise
    return browser, ctx, tunnel


async def _fill_first(page, sels, value):
    for s in sels:
        try:
            loc = page.locator(s).first
            if await loc.count() and await loc.is_visible():
                await loc.fill(value)
                return True
        except Exception:
            pass
    return False


async def _click_first(page, sels):
    for s in sels:
        try:
            loc = page.locator(s).first
            if await loc.count() and await loc.is_visible() and await loc.is_enabled():
                await loc.click()
                return True
        except Exception:
            pass
    return False


CONTINUE_BTNS = [
    "#continue_btn",
    'button:has-text("Continue")',
    'button[type="submit"].max-width',
    'button[type="submit"]',
]

# Email daalne ke baad Magzter do me se ek page deta hai:
#   CASE 1 - LOGIN  : /login/email?/userData   -> #user-pass + button #continue_btn ("Continue")
#   CASE 2 - SIGNUP : /signup?email=...        -> "Almost there!" form:
#                     #inp_box (Full Name) + #pass (Password) + button "CREATE ACCOUNT"
# Signup wale form me Full Name khaali aata hai; bhare bina form
# "Name field should not be empty" pe atak jata hai aur session banta hi nahi.
SIGNUP_NAME_SEL = '#inp_box, input[name="name"], input[placeholder="Test Holder"]'

CREATE_ACCOUNT_BTNS = [
    'button:has-text("CREATE ACCOUNT")',
    'button:has-text("Create Account")',
    'button[type="submit"]',
]

COOKIE_OK_BTNS = ['button:has-text("AGREE")', 'button:has-text("Agree")', "#cookie-accept"]

# signup form apni galti isi tarah dikhata hai ("Name field should not be empty" etc.)
SIGNUP_ERR_SEL = '.error, .err_msg, .error-msg, [class*="error"]'


async def _first_text(page, sel):
    try:
        for i in range(min(await page.locator(sel).count(), 6)):
            el = page.locator(sel).nth(i)
            if await el.is_visible():
                t = (await el.inner_text() or "").strip()
                if t:
                    return t[:100]
    except Exception:
        pass
    return ""


def name_from_email(email):
    """test@example.com -> 'Sanjay Chatterjee'."""
    local = (email or "").split("@")[0]
    local = re.sub(r"\d+", " ", local)                 # ginti hata do
    parts = [p for p in re.split(r"[._\-+]+", local) if p.strip()]
    name = " ".join(w.capitalize() for w in parts).strip()
    return name or "Magzter User"


async def _visible(page, sel):
    try:
        loc = page.locator(sel).first
        return bool(await loc.count()) and await loc.is_visible()
    except Exception:
        return False


async def has_session(page):
    """Login sach me hua ya nahi - session cookie se pata chalta hai."""
    try:
        names = {c["name"] for c in await page.context.cookies()}
        return bool(names & {"isLogged", "sess", "userId"})
    except Exception:
        return False


async def submit_signup_form(page, email, password, tag):
    """"Almost there!" form bharo aur CREATE ACCOUNT dabao.
    Har koshish me form DOBARA bharo - submit fail hone pe form khud ko saaf kar
    deta hai, aur khaali form "Name field should not be empty" pe atak jata hai."""
    full_name = name_from_email(email)
    for attempt in (1, 2, 3):
        if attempt > 1:
            await accept_cookies(page)
            await dismiss_popups(page)
            logger.info(f"{tag} [Signup] form dobara bhar ke CREATE ACCOUNT ({attempt})")
        if not await _fill_first(page, [SIGNUP_NAME_SEL, "#inp_box", 'input[name="name"]'], full_name):
            raise Exception("Full Name field nahi mila")
        if not await _fill_first(page, ["#pass", 'input[name="password"]', 'input[type="password"]'], password):
            raise Exception("Password field nahi mila")
        if attempt == 1:
            logger.info(f"{tag} [3/4] Signup form: naam '{full_name}' + password bhara")
        if not await _click_first(page, CREATE_ACCOUNT_BTNS):
            raise Exception("CREATE ACCOUNT button nahi mila")
        await page.wait_for_timeout(7000)
        if "/signup" not in page.url:
            return
        msg = await _first_text(page, SIGNUP_ERR_SEL)
        if msg:
            logger.warning(f"{tag} [Signup] form ne kaha: {msg}")


async def accept_cookies(page):
    """Cookie banner ka AGREE - iske bina session cookie theek set nahi hoti."""
    for sel in COOKIE_OK_BTNS:
        try:
            b = page.locator(sel).first
            if await b.count() and await b.is_visible():
                await b.click(timeout=3000)
                await page.wait_for_timeout(800)
                return True
        except Exception:
            pass
    return False

ERROR_SELECTORS = [
    "text=incorrect password",
    "text=Incorrect password",
    "text=invalid password",
    "text=Invalid credentials",
    "text=wrong password",
    ".alert-danger",
    'div[role="alert"]',
    "#error-message",
]


async def do_login(page, email, password, tag):
    logger.info(f"{tag} [1/4] Login page khol rahe hain...")
    EMAIL_SEL = 'test@example.com"mail"], #user-email, input[type="email"]'

    for attempt in (1, 2):
        await page.goto("https://www.magzter.com/login/email", wait_until="domcontentloaded", timeout=60000)
        try:
            # headless me page dher rendering leta hai - fixed sleep ki jagah asli wait
            await page.wait_for_selector(EMAIL_SEL, state="visible", timeout=25000)
            break
        except Exception:
            await dismiss_popups(page)
            try:
                await page.wait_for_selector(EMAIL_SEL, state="visible", timeout=5000)
                break
            except Exception:
                if attempt == 2:
                    raise Exception("Email field nahi mila (login page load nahi hua)")
                logger.warning(f"{tag} login page dobara load kar rahe hain...")
                await page.wait_for_timeout(2000)

    await dismiss_popups(page)
    # cookie banner sabse pehle hata do - warna neeche wale button pe click
    # kabhi-kabhi usi banner pe lag jata hai (headless me ye zyada hota hai)
    await accept_cookies(page)
    if not await _fill_first(page, ["#user-email-inp", 'input[name="mail"]', "#user-email", 'input[type="email"]'], email):
        raise Exception("Email field nahi mila")
    logger.info(f"{tag} [2/4] Email bhara: {email}")
    await _click_first(page, CONTINUE_BTNS)
    await page.wait_for_timeout(3500)
    await dismiss_popups(page)

    # Email ke baad Magzter do me se ek page deta hai:
    #   CASE 1 - LOGIN  : /login/email?/userData  -> sirf password + "Continue"
    #   CASE 2 - SIGNUP : /signup?email=...       -> Full Name + password + "CREATE ACCOUNT"
    # Ye beech wali screen kabhi-kabhi 30s me bhi nahi aati - us haalat me fail mat
    # karo, neeche wala seedha-signup raasta usko sambhal lega.
    try:
        await page.wait_for_selector('#pass, #user-pass, input[type="password"]',
                                     state="visible", timeout=30000)
        password_screen = True
    except Exception:
        logger.info(f"{tag} [Login] password screen nahi aayi - signup raaste se jayenge")
        password_screen = False

    if password_screen:
        if "/signup" in page.url or await _visible(page, SIGNUP_NAME_SEL):
            # ---- CASE 2: signup form khud aa gaya ----
            await submit_signup_form(page, email, password, tag)
        else:
            # ---- CASE 1: seedha login ----
            if not await _fill_first(page, ["#user-pass", 'input[name="pass"]', 'input[type="password"]'], password):
                raise Exception("Password field nahi mila")
            logger.info(f"{tag} [3/4] Password bhara")
            if not await _click_first(page, CONTINUE_BTNS):
                raise Exception("Continue button nahi mila")

        # session banne do (URL login/signup se hat jaye)
        try:
            await page.wait_for_url(lambda u: "/login" not in u and "/signup" not in u, timeout=25000)
        except Exception:
            pass
        await page.wait_for_timeout(2500)
        await accept_cookies(page)      # "AGREE" banner - iske bina cookie set nahi hoti
        await dismiss_popups(page)

    # Magzter ab NAYI email pe bhi password page dikha deta hai, /signup pe khud nahi
    # bhejta. Aise me password kabhi match nahi karta: page wahin ka wahin reh jata
    # hai, koi error bhi nahi dikhta, aur baad me my_orders login pe phenk deta hai.
    # Isliye: session na bane to seedhe signup URL pe jaakar account bana lo.
    if not await has_session(page):
        logger.info(f"{tag} [Signup] login se session nahi bana - seedha signup kar rahe hain")
        await page.goto(f"https://www.magzter.com/signup?email={quote(email)}",
                        wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(3000)
        await accept_cookies(page)
        await dismiss_popups(page)
        if not await _visible(page, SIGNUP_NAME_SEL):
            raise Exception("ACCOUNT_NOT_FOUND")
        await submit_signup_form(page, email, password, tag)
        try:
            await page.wait_for_url(lambda u: "/signup" not in u, timeout=25000)
        except Exception:
            pass
        await page.wait_for_timeout(2500)
        await accept_cookies(page)
        await dismiss_popups(page)

    for sel in ERROR_SELECTORS:
        try:
            loc = page.locator(sel).first
            if await loc.count() and await loc.is_visible():
                txt = (await loc.inner_text()).strip()[:80]
                if txt:
                    raise Exception(f"INVALID_LOGIN: {txt}")
        except Exception as e:
            if "INVALID_LOGIN" in str(e):
                raise
    logger.info(f"{tag} [4/4] Login ho gaya")


async def read_orders(page, tag):
    """My Orders page -> pehli (latest) row ka Transaction ID + Date."""
    # my_orders kabhi-kabhi session set hone se pehle login pe redirect kar deta hai.
    # Naye bane account me ye der aur zyada hoti hai -> 5 baar, badhte hue wait ke saath.
    LAST = 5
    for attempt in range(1, LAST + 1):
        await page.goto("https://www.magzter.com/dashboard/my_orders", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(3000)
        await dismiss_popups(page)
        if "login" not in page.url:
            break
        if attempt < LAST:
            logger.info(f"{tag} [Orders] session late - reload ({attempt})")
            await page.wait_for_timeout(2000 * attempt)   # 2s, 4s, 6s, 8s
        else:
            raise Exception("my_orders ne login pe wapas bheja (session late) - retry")

    try:
        await page.wait_for_selector('td[data-title="Transaction ID"]', timeout=15000)
        ids = [x.strip() for x in await page.locator('td[data-title="Transaction ID"]').all_inner_texts() if x.strip()]
        dates = [x.strip() for x in await page.locator('td[data-title="Date"]').all_inner_texts() if x.strip()]
    except Exception:
        body = (await page.inner_text("body")).lower()
        # Magzter khaali account pe likhta hai: "You have not purchased anything yet."
        if ("no order" in body or "haven't" in body or "not placed" in body
                or "not purchased anything" in body or "no purchase" in body):
            logger.info(f"{tag} [Orders] Is account me koi order nahi")
            return "", "", "NO_ORDERS"
        logger.warning(f"{tag} [Orders] Transaction table nahi mila")
        return "", "", "NOT_FOUND"

    if not ids:
        return "", "", "NOT_FOUND"

    txn_id = ids[0]
    txn_date = dates[0] if dates else ""
    if len(ids) > 1:
        logger.info(f"{tag} [Orders] {len(ids)} orders mile - latest liya")
    logger.info(f"{tag} [Orders] Transaction ID: {txn_id} | Date: {txn_date}")
    return txn_id, txn_date, "DONE"


# ====================== WORKER ======================
_attempts = {}


async def worker_loop(pw, worker_no, queue, ws, cmap, counters):
    tag = f"[W{INSTANCE_ID}.{worker_no}]"
    while True:
        try:
            item = queue.get_nowait()
        except asyncio.QueueEmpty:
            logger.info(f"{tag} Koi row baaki nahi - worker band.")
            return

        row, email, password = item["row"], item["email"], item["password"]

        # sheet calls blocking hain -> thread me, taki baaki workers na ruken
        if not await asyncio.to_thread(claim_row, ws, cmap, row, worker_no):
            continue

        logger.info(f"{tag} ===== row {row} | {email} =====")
        browser = None
        tunnel = None
        t0 = time.time()
        try:
            browser, ctx, tunnel = await new_browser(pw, args.headed)
            page = await ctx.new_page()
            await do_login(page, email, password, tag)
            txn_id, txn_date, status = await read_orders(page, tag)
            await asyncio.to_thread(write_result, ws, cmap, row, worker_no, txn_id, txn_date, status, "")
            counters["done" if status == "DONE" else "empty"] += 1
            logger.info(f"{tag} row {row} khatam ({time.time() - t0:.0f}s)")
        except Exception as e:
            err = str(e)
            logger.error(f"{tag} row {row} FAIL: {err[:200]}")
            counters["failed"] += 1
            permanent = ("INVALID_LOGIN" in err) or ("ACCOUNT_NOT_FOUND" in err)
            _attempts[row] = _attempts.get(row, 0) + 1
            try:
                if permanent:
                    reason = "invalid password" if "INVALID_LOGIN" in err else "account not found"
                    await asyncio.to_thread(write_result, ws, cmap, row, worker_no, "", "", "FAILED", reason)
                elif _attempts[row] >= MAX_ATTEMPTS:
                    await asyncio.to_thread(write_result, ws, cmap, row, worker_no, "", "", "FAILED", err[:120])
                else:
                    await asyncio.to_thread(release_row, ws, cmap, row, "")   # claim chhodo -> dobara try
            except Exception as ee:
                logger.warning(f"{tag} recovery fail: {ee}")
        finally:
            if browser:
                try:
                    await browser.close()
                except Exception:
                    pass
            if tunnel:
                try:
                    tunnel.stop()
                except Exception:
                    pass
            await asyncio.sleep(random.uniform(args.min_delay, args.max_delay))


# ====================== MAIN ======================
async def main():
    logger.info("=" * 62)
    logger.info(f"[Start] machine {INSTANCE_ID}/{TOTAL_INSTANCES} | workers={WORKERS} | "
                f"mode={'HEADED' if args.headed else 'HEADLESS'} | tab={args.tab}")
    if USE_PROXY:
        rng = (f"{PROXY_PORT_MIN}-{PROXY_PORT_MAX}"
               if PROXY_PORT_MIN and PROXY_PORT_MAX else str(PROXY_PORT))
        logger.info(f"[Proxy] ON  {PROXY_HOST}:{rng}  user={PROXY_USERNAME[:28]}")
    else:
        logger.info("[Proxy] OFF - seedha is machine ke IP se")
    logger.info("=" * 62)

    ws = await asyncio.to_thread(open_sheet, 1)
    cmap = await asyncio.to_thread(ensure_output_columns, ws)

    counters = {"done": 0, "empty": 0, "failed": 0}
    t_start = time.time()

    async with async_playwright() as pw:
        while True:
            pending = await asyncio.to_thread(fetch_pending, ws)
            if not pending:
                logger.info("[Info] Koi pending row nahi bachi.")
                break

            if args.limit:
                remaining = args.limit - sum(counters.values())
                if remaining <= 0:
                    logger.info(f"[Info] Limit {args.limit} poori ho gayi.")
                    break
                pending = pending[:remaining]

            logger.info(f"[Info] {len(pending)} rows queue me | {WORKERS} worker chal rahe hain")
            queue = asyncio.Queue()
            for item in pending:
                queue.put_nowait(item)

            await asyncio.gather(*[worker_loop(pw, i + 1, queue, ws, cmap, counters)
                                   for i in range(WORKERS)])

            if args.limit and sum(counters.values()) >= args.limit:
                logger.info(f"[Info] Limit {args.limit} poori ho gayi.")
                break
            await asyncio.sleep(3)

    dur = time.time() - t_start
    logger.info("=" * 62)
    logger.info(f"[Complete] DONE={counters['done']} | NO_ORDERS/NOT_FOUND={counters['empty']} | "
                f"FAILED={counters['failed']} | time={dur / 60:.1f} min")
    logger.info(f"[Log] {log_filename}")
    logger.info("=" * 62)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("[Stop] User ne rok diya.")
    if getattr(sys, "frozen", False) and not args.no_prompt:
        try:
            input("\nEnter dabaye band karne ke liye...")
        except Exception:
            pass
