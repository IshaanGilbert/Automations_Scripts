#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sheet_db.py  —  Google Sheet backed drop-in replacement for db.py (buyer bot).

Kaam: buyer.py ab Postgres ki jagah ek Google Sheet se task uthata hai. Har row =
ek transaction. Ye module wahi function/naam deta hai jo buyer.py `db.` se bulata hai,
isliye buyer.py me sirf ONE line badalni hai:

    import db            ->   import sheet_db as db

--------------------------------------------------------------------------------------
GOOGLE SHEET COLUMNS
--------------------------------------------------------------------------------------
INPUT (ye aap bharte ho — ek transaction ke liye zaroori):
    card_no      : card number (16 digit)
    month        : expiry  (MM/YY ya MMYY)
    cvv          : cvv / cvc
    email        : account email
    password     : account password (verify/login-verify ke liye)
    corp_id      : corporate id
    emp_id       : employee id
    first_name   : buyer ka first name
    last_name    : buyer ka last name
    campaign_id  : (optional) grouping/report ke liye

OUTPUT (script khud bana kar bharti hai — na hon to auto-add ho jaate hain):
    status        : pending/running/completed/failed/declined/ineligible/unconfirmed
    transaction_id: success par Magzter transaction id
    name_used     : jo naam use hua
    proxy_ip      : jis proxy IP se transaction hua
    duration_sec  : kitne second lage
    error         : fail hone ki wajah
    updated_email : email mutation hone par nayi email (original chhui nahi jaati)
    email_attempts: kitni baar email mutate hui
    retries       : kitni baar retry hui
    claimed_by    : abhi kaunsa instance kaam kar raha (CLAIM lock token)
    step          : live progress step
    updated_at    : aakhri update ka time

Blank status ya 'pending' = script uthayegi. Baaki (completed/failed/...) = chhod degi.
--------------------------------------------------------------------------------------
"""

import os
import re
import sys
import time
import json
import random
import hashlib
import tempfile
import threading
import contextlib
from datetime import datetime

# Kisi bhi Windows system par emoji/print crash na kare (buyer.py bhut emoji print karta
# hai; cp1252 console par UnicodeEncodeError aa sakta hai). utf-8 + errors=replace se safe.
for _stream in ("stdout", "stderr"):
    try:
        getattr(sys, _stream).reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import gspread
from google.oauth2.service_account import Credentials

# ================= STATUS CONSTANTS (db.py jaise) =================
ST_PENDING     = "pending"
ST_RUNNING     = "running"
ST_COMPLETED   = "completed"
ST_FAILED      = "failed"
ST_DECLINED    = "declined"
ST_INELIGIBLE  = "ineligible"
ST_UNCONFIRMED = "unconfirmed"
ST_DONE        = "done"
ST_RETRY       = "retry"

_TERMINAL = {ST_COMPLETED, ST_FAILED, ST_DECLINED, ST_INELIGIBLE, ST_UNCONFIRMED, ST_DONE}

# ================= CONFIG =================
def _base_dir():
    import sys
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

BASE = _base_dir()
CONFIG_FILE = os.path.join(BASE, "config.json")

def _load_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.loads(f.read().strip() or "{}")
    except Exception:
        return {}

_cfg = _load_config()

# Sheet id / url config.json se (ya env se). Dono naam support: SHEET_ID / GOOGLE_SHEET_URL_OR_ID
_sheet_raw = (os.environ.get("SHEET_ID")
              or _cfg.get("SHEET_ID")
              or _cfg.get("GOOGLE_SHEET_URL_OR_ID")
              or "")
_m = re.search(r"/d/([a-zA-Z0-9\-_]+)", _sheet_raw)
SPREADSHEET_ID = _m.group(1) if _m else _sheet_raw
TAB_NAME = os.environ.get("SHEET_TAB") or _cfg.get("BUY_SHEET", "Buy")

SCOPES = ["https://www.googleapis.com/auth/spreadsheets",
          "https://www.googleapis.com/auth/drive"]
NUM_ACCOUNTS = 6

# instance id (buyer.py --instance) taaki har instance alag creds use kare (rate-limit spread)
def _instance_id():
    try:
        # buyer.py already parsed --instance; sabse aasaan: env se ya default 1
        return int(os.environ.get("BUYER_INSTANCE", "1"))
    except Exception:
        return 1

import socket as _socket
_WORKER_ID = None
def _worker_id():
    """GLOBALLY unique worker id = host + pid + instance.
    Do alag system agar dono --instance 1 chalayein, tab bhi token alag rahe ->
    na row double claim ho, na per-emp count galat ho. ':' nahi use karte (token
    ':' se split hota hai). Ek baar compute hota hai (BUYER_INSTANCE tab tak set ho chuka)."""
    global _WORKER_ID
    if _WORKER_ID is None:
        host = re.sub(r"[^A-Za-z0-9]", "", _socket.gethostname())[:16] or "host"
        _WORKER_ID = f"{host}.{os.getpid()}.{_instance_id()}"
    return _WORKER_ID

def _creds_dirs():
    """Creds kin folders me dhoondni hain (priority order):
       1) config/env CREDS_DIR   2) script folder   3) uska parent folder."""
    dirs = []
    cd = os.environ.get("CREDS_DIR") or _cfg.get("CREDS_DIR")
    if cd:
        dirs.append(cd)
    dirs.append(BASE)
    dirs.append(os.path.dirname(BASE))
    seen, out = set(), []
    for d in dirs:
        d = os.path.abspath(d)
        if d not in seen:
            seen.add(d); out.append(d)
    return out

def _creds_file():
    """Is instance ke liye ek service-account json chuno (round-robin), jahan bhi mile.
       creds{N}.json -> google_credentials.json -> koi bhi creds*.json."""
    idx = ((_instance_id() - 1) % NUM_ACCOUNTS) + 1
    names = [f"creds{idx}.json", "google_credentials.json"]
    for d in _creds_dirs():
        for n in names:
            f = os.path.join(d, n)
            if os.path.exists(f):
                return f
    # last resort: kisi bhi folder me pehli creds*.json / google_credentials
    import glob
    for d in _creds_dirs():
        hits = sorted(glob.glob(os.path.join(d, "creds*.json"))) or \
               glob.glob(os.path.join(d, "google_credentials.json"))
        if hits:
            return hits[0]
    raise RuntimeError("Koi service-account creds file nahi mili (creds1..6.json / "
                       "google_credentials.json). Sheet-shared account ki json is folder me rakho "
                       "ya config.json me CREDS_DIR set karo.")

# ================= INPUT / OUTPUT COLUMNS =================
INPUT_COLS = ["card_no", "month", "cvv", "email", "password",
              "corp_id", "emp_id", "first_name", "last_name"]
OUTPUT_COLS = ["status", "transaction_id", "name_used", "proxy_ip", "duration_sec",
               "error", "updated_email", "email_attempts", "retries",
               "claimed_by", "step", "updated_at"]

CLAIM_STALE_SECONDS = int(_cfg.get("CLAIM_STALE_SECONDS", 1800))   # 30 min

# ================= LOW-LEVEL SHEET ACCESS =================
_ws = None
_ws_lock = threading.RLock()
_header = None            # list of header names
_col = {}                # name -> 1-based col index

def _api(fn, *a, **k):
    """429/5xx pe exponential backoff. gspread ka koi bhi call yahan se."""
    delay = 5
    last = None
    for attempt in range(6):
        try:
            return fn(*a, **k)
        except gspread.exceptions.APIError as e:
            last = e
            s = str(e)
            if any(x in s for x in ("429", "Quota exceeded", "RATE_LIMIT", "500", "503")):
                time.sleep(delay + random.uniform(0, 4))
                delay = min(delay * 2, 90)
                continue
            raise
    raise last

def _col_letter(n):
    s = ""
    while n > 0:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s

def _open():
    global _ws
    if _ws is not None:
        return _ws
    with _ws_lock:
        if _ws is not None:
            return _ws
        if not SPREADSHEET_ID:
            raise RuntimeError("SHEET_ID / GOOGLE_SHEET_URL_OR_ID config.json me set karo")
        # Creds priority:
        #   1) config.json ka embedded GOOGLE_CREDENTIALS (ek hi account -> access-safe)
        #   2) warna creds1..6.json / google_credentials.json (round-robin, rate spread)
        emb = _cfg.get("GOOGLE_CREDENTIALS")
        if isinstance(emb, dict) and emb.get("client_email"):
            info = emb
            src = f"config.GOOGLE_CREDENTIALS"
        else:
            cf = _creds_file()
            with open(cf, "r", encoding="utf-8") as f:
                info = json.load(f)
            src = os.path.basename(cf)
        client = gspread.authorize(Credentials.from_service_account_info(info, scopes=SCOPES))
        _ws = _api(lambda: client.open_by_key(SPREADSHEET_ID).worksheet(TAB_NAME))
        print(f"📄 Sheet connected: tab='{TAB_NAME}' via {src} "
              f"({info.get('client_email','?')})", flush=True)
        _ensure_columns(_ws)
        return _ws

def _ensure_columns(ws):
    """Header padho; output columns na hon to end me jod do; col-index map bana lo."""
    global _header, _col
    headers = _api(ws.row_values, 1)
    missing_in = [c for c in INPUT_COLS if c not in headers]
    if missing_in:
        raise RuntimeError(f"Sheet me ye INPUT columns nahi hain: {missing_in}\n"
                           f"Mile: {headers}")
    add = [c for c in OUTPUT_COLS if c not in headers]
    if add:
        new_headers = headers + add
        rng = f"A1:{_col_letter(len(new_headers))}1"
        _api(ws.update, values=[new_headers], range_name=rng)
        print(f"📄 Naye output columns bane: {add}", flush=True)
        headers = new_headers
    _header = headers
    _col = {h: i + 1 for i, h in enumerate(headers) if h}

def _get(row, name):
    i = _col.get(name)
    if not i:
        return ""
    return str(row[i - 1]).strip() if i - 1 < len(row) else ""

# ================= EMAIL HELPERS (db.py se copy — pure functions) =================
_EMAIL_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*@[a-z0-9-]+(\.[a-z0-9-]+)+$")
_DOMAIN_FIX = {
    "gmail.con": "gmail.com", "gmail.co": "gmail.com", "gmial.com": "gmail.com",
    "gmai.com": "gmail.com", "gmail.cm": "gmail.com", "gmailcom": "gmail.com",
    "gnail.com": "gmail.com", "gmaill.com": "gmail.com",
    "outlook.con": "outlook.com", "outlok.com": "outlook.com", "outlookcom": "outlook.com",
    "hotmail.con": "hotmail.com", "hotmial.com": "hotmail.com", "hotmailcom": "hotmail.com",
    "yahoo.con": "yahoo.com", "yaho.com": "yahoo.com", "yahoocom": "yahoo.com",
}

def sanitize_email(email):
    if not email:
        return None
    e = str(email).strip().lower().replace(" ", "")
    e = re.sub(r"@{2,}", "@", e)
    if e.count("@") != 1:
        return None
    local, domain = e.split("@", 1)
    local = re.sub(r"\.{2,}", ".", local).strip(".")
    domain = re.sub(r"\.{2,}", ".", domain).strip(".")
    domain = _DOMAIN_FIX.get(domain, domain)
    if "." not in domain and domain in ("gmail", "outlook", "hotmail", "yahoo"):
        domain += ".com"
    e = f"{local}@{domain}"
    return e if _EMAIL_RE.match(e) else None

def mutate_email(original, tried=None):
    clean = sanitize_email(original)
    if not clean:
        return None
    if isinstance(tried, int):
        tried = None
    tried = set(tried or ())
    tried.add(clean)
    local, domain = clean.split("@", 1)
    base = re.sub(r"[.]", "", local)
    domains = ["gmail.com", "outlook.com", "hotmail.com", "yahoo.com"]
    for _ in range(40):
        b, d = base, domain
        s = random.randint(0, 4)
        if s == 0 and len(b) > 1:
            p = random.randint(1, len(b) - 1); cl = b[:p] + "." + b[p:]
        elif s == 1:
            cl = b + str(random.randint(1, 99))
        elif s == 2 and len(b) > 1:
            p = random.randint(1, len(b)); cl = b[:p] + str(random.randint(0, 9)) + b[p:]
        elif s == 3:
            cl = b; d = random.choice([x for x in domains if x != domain])
        else:
            p = random.randint(1, max(1, len(b) - 1))
            cl = b[:p] + "." + b[p:] + str(random.randint(1, 9))
        cand = f"{cl}@{d}"
        if cand != clean and cand not in tried and _EMAIL_RE.match(cand):
            return cand
    return None

# ================= TASK SHAPE =================
def _to_task(row_index, row):
    return {
        "task_id": row_index,
        "row": row_index,
        "card_no": _get(row, "card_no"),
        "month": _get(row, "month"),
        "cvv": _get(row, "cvv"),
        "email": _get(row, "email"),
        "updated_email": _get(row, "updated_email") or None,
        "email_attempts": int(_get(row, "email_attempts") or 0),
        "password": _get(row, "password") or None,
        "corp_id": _get(row, "corp_id"),
        "emp_id": _get(row, "emp_id"),
        "first_name": _get(row, "first_name"),
        "last_name": _get(row, "last_name"),
    }

def _claimable(status, claimed_by):
    st = (status or "").strip().lower()
    if st in _TERMINAL or st == ST_RETRY:
        return False
    cb = (claimed_by or "").strip()
    if cb.startswith("CLAIM:"):
        try:
            ts = int(cb.split(":")[2])
            return (time.time() - ts) > CLAIM_STALE_SECONDS   # stale = wapas uthao
        except Exception:
            return True
        return False
    # blank / pending / running-with-stale-claim
    if st in ("", ST_PENDING):
        return True
    if st == ST_RUNNING:
        return not cb or cb.startswith("CLAIM:")   # running but claim stale handled above
    return False

# ================= READINESS / PAUSE =================
def assert_db_ready():
    """Sheet reachable + zaroori columns present. Warna raise (buyer sys.exit karega)."""
    ws = _open()
    _ = _api(ws.row_values, 1)
    return True

def is_paused():
    """Optional global pause: config.json me {"PAUSED": true} rakh do to bots ruk jayenge.
    Fail-safe: koi dikkat -> False (fleet kabhi galti se ruke na)."""
    try:
        return str(_load_config().get("PAUSED", False)).lower() in ("1", "true", "yes", "on")
    except Exception:
        return False

# ================= CLAIM =================
_fail_counts = {}   # row -> local retry count (retry_or_fail ke liye)

def _all_rows():
    ws = _open()
    vals = _api(ws.get_all_values)
    return ws, vals

def count_pending():
    """(pending_rows, pending_groups) — rough ETA ke liye."""
    try:
        _, vals = _all_rows()
        rows = 0
        emps = set()
        for r in vals[1:]:
            st = _get(r, "status").lower()
            if st in ("", ST_PENDING, ST_RUNNING):
                rows += 1
                emps.add(_get(r, "emp_id"))
        return rows, len(emps)
    except Exception:
        return 0, 0

def claim_next_group(instance_id, attempts=25, instances_per_emp=1):
    """Ek emp_id ka pending group claim karo (jaise db.py).
      instances_per_emp = N  -> ek emp pe max N instance.
      instances_per_emp = 0  -> unlimited.
    Har claimable row me CLAIM token likho + read-back verify. Task dicts list return,
    ya None jab kuch claim karne layak na bache."""
    me = int(instance_id)
    ipe = 10**9 if int(instances_per_emp) <= 0 else max(1, int(instances_per_emp))

    for _ in range(max(1, attempts)):
        ws, vals = _all_rows()
        # emp_id -> {rows:[...], active_instances:set()}
        groups = {}
        for idx, r in enumerate(vals[1:]):
            row_index = idx + 2
            emp = _get(r, "emp_id")
            if not emp:
                continue
            g = groups.setdefault(emp, {"rows": [], "insts": set()})
            cb = _get(r, "claimed_by")
            st = _get(r, "status")
            # kaun se instance abhi is emp pe kaam kar rahe (fresh claim)
            if cb.startswith("CLAIM:"):
                try:
                    parts = cb.split(":")
                    if (time.time() - int(parts[2])) <= CLAIM_STALE_SECONDS:
                        g["insts"].add(parts[1])
                except Exception:
                    pass
            if _get(r, "card_no") and _claimable(st, cb):
                g["rows"].append((row_index, r))

        # pehla emp jisme claimable rows hain aur instance-cap bacha ho
        picked_emp = None
        for emp, g in groups.items():
            if not g["rows"]:
                continue
            insts = set(g["insts"])
            if _worker_id() not in insts and len(insts) >= ipe:
                continue   # is emp pe pehle se enough workers (har machine ka apna id) lage hain
            picked_emp = emp
            break

        if picked_emp is None:
            # kuch bhi claim karne layak nahi
            any_pending = any(g["rows"] for g in groups.values())
            if not any_pending:
                return None
            time.sleep(1.5)
            continue

        # is emp ki rows claim karo (read-back verify ke saath)
        claimed = []
        for row_index, r in groups[picked_emp]["rows"]:
            if _claim_one(ws, row_index):
                claimed.append(_to_task(row_index, _api(ws.row_values, row_index)))
        if claimed:
            return claimed
        time.sleep(1.5)   # race haar gaye, dobara

    return None

def _claim_one(ws, row_index):
    """claimed_by cell me token likho, 0.8s ruk kar wapas padho. Match = humari row.
    Token me globally-unique worker id -> do machine ek saath bhi same row double na karein."""
    ci = _col["claimed_by"]
    si = _col["status"]
    token = f"CLAIM:{_worker_id()}:{int(time.time())}"
    try:
        _api(ws.update_cell, row_index, ci, token)
        time.sleep(0.8)
        cur = str(_api(ws.cell, row_index, ci).value or "").strip()
        if cur != token:
            return False
        _api(ws.update_cell, row_index, si, ST_RUNNING)
        return True
    except Exception:
        return False

# ================= STATUS WRITEBACK =================
def _batch_update(row_index, data):
    """data = {col_name: value} -> ek batch call me minimum range update."""
    ws = _open()
    idxs = [_col[c] for c in data if c in _col]
    if not idxs:
        return False
    lo, hi = min(idxs), max(idxs)
    # existing row padho taaki beech ke jo columns update nahi karne wo chhede na jayen
    try:
        cur = _api(ws.row_values, row_index)
    except Exception:
        cur = []
    values = [""] * (hi - lo + 1)
    for j in range(lo, hi + 1):
        values[j - lo] = cur[j - 1] if j - 1 < len(cur) else ""
    for c, v in data.items():
        if c in _col:
            values[_col[c] - lo] = "" if v is None else str(v)
    rng = f"{_col_letter(lo)}{row_index}:{_col_letter(hi)}{row_index}"
    _api(ws.update, values=[values], range_name=rng)
    return True

def update_task_step(task_id, step):
    try:
        return _batch_update(int(task_id), {"step": str(step)[:40],
                                            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    except Exception:
        return False

def update_task(task_id, status, name_used="", proxy_ip="", duration_sec=None,
                error="", transaction_id=None):
    """Result wapas sheet me likho. FINAL status sirf tab jab row abhi 'running' ho
    (finished row dobara overwrite na ho — instance collision protection)."""
    row = int(task_id)
    ws = _open()
    try:
        cur = _api(ws.row_values, row)
    except Exception:
        cur = []
    cur_status = _get(cur, "status").lower() if cur else ""
    if status != ST_RUNNING and cur_status not in ("", ST_RUNNING, ST_PENDING):
        print(f"   ⚠️ update_task: row {row} pehle hi finalize ho chuki ({cur_status}) — skip", flush=True)
        return False

    data = {"status": status,
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    if name_used:
        data["name_used"] = name_used
    if proxy_ip:
        data["proxy_ip"] = proxy_ip
    if duration_sec is not None:
        data["duration_sec"] = str(duration_sec)
    if error:
        data["error"] = str(error)[:500]
    if transaction_id:
        data["transaction_id"] = transaction_id
    if status != ST_RUNNING:
        data["claimed_by"] = ""   # claim release on finalize
    try:
        return _batch_update(row, data)
    except Exception as e:
        print(f"❌ sheet update_task failed: {e}", flush=True)
        return False

def retry_or_fail(task_id, max_retries=3, error="", final_status=None,
                  name_used="", proxy_ip="", duration_sec=None, transaction_id=None):
    """Har fail pehle retry hoti hai, phir apni asli status pe. retries < max ->
    wapas 'pending' (claim release). Warna final_status (default failed)."""
    row = int(task_id)
    fs = final_status or ST_FAILED
    ws = _open()
    try:
        cur = _api(ws.row_values, row)
    except Exception:
        cur = []
    try:
        prev_retries = int(_get(cur, "retries") or 0)
    except Exception:
        prev_retries = 0
    new_retries = prev_retries + 1

    data = {"retries": str(new_retries),
            "error": str(error)[:500],
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    if name_used:
        data["name_used"] = name_used
    if proxy_ip:
        data["proxy_ip"] = proxy_ip
    if duration_sec is not None:
        data["duration_sec"] = str(duration_sec)
    if transaction_id:
        data["transaction_id"] = transaction_id

    if new_retries < max_retries:
        data["status"] = ST_PENDING
        data["claimed_by"] = ""          # release -> koi bhi instance dobara utha le
        landed = ST_PENDING
    else:
        data["status"] = fs
        data["claimed_by"] = ""
        landed = fs
    try:
        _batch_update(row, data)
        return landed
    except Exception as e:
        print(f"❌ sheet retry_or_fail failed: {e}", flush=True)
        return None

def set_updated_email(task_id, email, attempts=None):
    """In-session mutation se jo email actually use hui wo alag column me. Original chhui nahi."""
    data = {"updated_email": email}
    if attempts is not None:
        data["email_attempts"] = str(int(attempts))
    try:
        return _batch_update(int(task_id), data)
    except Exception:
        return False

# ================= OTP PER-EMP LOCK (cross-machine, sheet-based) =================
# corp-submit -> OTP fetch -> confirm window ko EK emp_id pe SABHI instances/systems ke
# beech serialize karna hai (do bot ek doosre ka OTP na consume karein).
# Postgres advisory lock ki jagah: ek chhota lock-tab '_otp_locks' me per-emp row,
# CLAIM token + read-back verify (wahi lock jo rows pe use hota hai). Cross-machine kaam
# karta hai. Agar lock-tab kisi wajah se na chale to FILE lock (same-machine) fallback.
LOCK_TAB = os.environ.get("OTP_LOCK_TAB") or _cfg.get("OTP_LOCK_TAB", "_otp_locks")
OTP_LOCK_STALE = int(_cfg.get("OTP_LOCK_STALE_SECONDS", 320))   # dead holder is release
_lock_ws = None
_lock_ws_lock = threading.RLock()
_LOCK_DIR = os.path.join(tempfile.gettempdir(), "magzter_otp_locks")
os.makedirs(_LOCK_DIR, exist_ok=True)

def _lock_sheet():
    """'_otp_locks' worksheet (na ho to bana do). Columns: emp_id | holder."""
    global _lock_ws
    if _lock_ws is not None:
        return _lock_ws
    with _lock_ws_lock:
        if _lock_ws is not None:
            return _lock_ws
        ws = _open()
        sh = ws.spreadsheet
        try:
            lw = sh.worksheet(LOCK_TAB)
        except Exception:
            lw = _api(sh.add_worksheet, title=LOCK_TAB, rows=200, cols=3)
            _api(lw.update, values=[["emp_id", "holder"]], range_name="A1")
        _lock_ws = lw
        return lw

def _lock_row_for(lw, emp_id):
    """emp_id ki lock-row ka number do; na ho to bana do (pehli matching consistent)."""
    vals = _api(lw.get_all_values)
    for i, r in enumerate(vals[1:], start=2):
        if r and str(r[0]).strip() == str(emp_id):
            return i
    _api(lw.append_row, [str(emp_id), ""])
    vals = _api(lw.get_all_values)
    for i, r in enumerate(vals[1:], start=2):
        if r and str(r[0]).strip() == str(emp_id):
            return i
    return None

def _sheet_lock_acquire(emp_id, deadline):
    lw = _lock_sheet()
    row = _lock_row_for(lw, emp_id)
    if not row:
        return None
    token = f"L:{_worker_id()}:{int(time.time())}"
    while time.time() < deadline:
        cur = str(_api(lw.cell, row, 2).value or "").strip()
        free = (not cur)
        if cur.startswith("L:"):
            try:
                free = (time.time() - int(cur.split(":")[2])) > OTP_LOCK_STALE   # stale holder
            except Exception:
                free = True
        if free:
            _api(lw.update_cell, row, 2, token)
            time.sleep(0.8)
            if str(_api(lw.cell, row, 2).value or "").strip() == token:
                return (lw, row, token)        # lock mila
        time.sleep(1.5)                          # kisi aur ke paas hai -> wait
    return None

def _sheet_lock_release(handle):
    try:
        lw, row, token = handle
        if str(_api(lw.cell, row, 2).value or "").strip() == token:
            _api(lw.update_cell, row, 2, "")
    except Exception:
        pass

@contextlib.contextmanager
def _file_lock(emp_id, deadline):
    key = hashlib.md5(str(emp_id).encode()).hexdigest()
    fh = open(os.path.join(_LOCK_DIR, f"{key}.lock"), "a+")
    got = False
    try:
        try:
            import msvcrt
            while time.time() < deadline:
                try: msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1); got = True; break
                except OSError: time.sleep(0.5)
        except ImportError:
            import fcntl
            while time.time() < deadline:
                try: fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB); got = True; break
                except OSError: time.sleep(0.5)
        yield got
    finally:
        try:
            if got:
                try:
                    import msvcrt; fh.seek(0); msvcrt.locking(fh.fileno(), msvcrt.LK_UNLCK, 1)
                except ImportError:
                    import fcntl; fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
        except Exception: pass
        try: fh.close()
        except Exception: pass

@contextlib.contextmanager
def otp_lock(emp_id, timeout_s=300):
    """Per-emp lock: pehle sheet-based (cross-machine); fail ho to file-lock (same-machine).
    Hamesha release. `with db.otp_lock(emp_id):` — buyer.py jaisa hi."""
    deadline = time.time() + timeout_s
    handle = None
    try:
        try:
            handle = _sheet_lock_acquire(emp_id, deadline)
        except Exception as e:
            print(f"   ⚠️ sheet OTP-lock fail ({str(e)[:60]}) — file-lock fallback", flush=True)
            handle = None
        if handle:
            yield True
        else:
            with _file_lock(emp_id, deadline) as got:
                yield got
    finally:
        if handle:
            _sheet_lock_release(handle)

# ================= OTP ALERT COUNTERS (best-effort no-op) =================
def record_otp_failure(emp_id):
    # Dashboard alert banner DB me tha; sheet mode me sirf log. Bot flow pe koi asar nahi.
    print(f"   ⚠️ OTP fail noted for emp {emp_id}", flush=True)

def record_otp_success(emp_id):
    return None
