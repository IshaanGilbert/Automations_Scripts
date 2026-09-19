#!/usr/bin/env python3
"""
CONTROLLER — single dashboard for ALL worker servers (slot-based).

Talks to each worker's node_agent.py over HTTP (token-secured, ideally over a
Tailscale private network). Drives per-slot dynamic script assignment (buyer /
reader / eligibility) and shows a leads CRM synced from the Google Sheet.

Run:  ./venv/bin/python3 controller.py     # http://<controller>:5050
Config: nodes.json (see nodes.example.json)
"""

from flask import (Flask, request, jsonify, Response, session, redirect,
                   render_template)
import os, json, html, re, threading, secrets, time as _time
# All timestamps in IST (Asia/Calcutta), regardless of the server clock.
os.environ["TZ"] = "Asia/Calcutta"
try: _time.tzset()
except Exception: pass
from functools import wraps
from concurrent.futures import ThreadPoolExecutor
# timedelta ko top level par hi import karo. Pehle ye sirf neeche wale fallback branch
# me tha, aur jis box par zoneinfo chalta hai (yaani sab par) wo branch kabhi nahi
# chalta — to session lifetime wali line par NameError aa gaya aur controller boot par
# hi crash-loop me chala gaya.
from datetime import datetime, timedelta
try:
    from zoneinfo import ZoneInfo
    IST = ZoneInfo("Asia/Kolkata")
except Exception:                       # py<3.9 / missing tzdata -> fixed +5:30 offset
    from datetime import timezone
    IST = timezone(timedelta(hours=5, minutes=30))
def now_ist():
    """Wall-clock time in IST regardless of the server's OS timezone (which is UTC).
    Use this everywhere instead of datetime.now() so the dashboard never shows UTC."""
    return datetime.now(IST)

import requests
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash

from envload import load_env
load_env()

HERE = os.path.dirname(os.path.abspath(__file__))
NODES_FILE = os.environ.get("NODES_FILE", os.path.join(HERE, "nodes.json"))
PASS_FILE = os.path.join(HERE, ".controller_pass")
SECRET_FILE = os.path.join(HERE, ".controller_secret")
# Master copies the dashboard edits, then pushes to every node.
MASTER_CONFIG = os.path.join(HERE, "config.json")
MASTER_SETTINGS = os.path.join(HERE, "settings.json")

# Initial admin login. Change the password from the UI (/changepw) after first
# login — the new hash is persisted to .controller_pass and overrides this.
#
# There is no hardcoded fallback password any more. A real one used to live here in
# plaintext, in a file that ships to every worker; anyone who could read the repo
# could sign in. If DASHBOARD_PASS is unset and no .controller_pass exists, the
# controller generates a random one and PRINTS IT ONCE at startup — so a fresh
# install is usable without ever shipping a known-good credential.
DASHBOARD_USER = os.environ.get("DASHBOARD_USER", "admin")
DASHBOARD_PASS = os.environ.get("DASHBOARD_PASS", "")

HTTP_TIMEOUT = (3, 10)            # (connect, read) — never hang the dashboard

# ── Shared HTTP session for ALL controller→agent calls ────────────────────────
# Previously every agent_call() did a bare requests.request(), opening a NEW TCP+TLS
# connection each time. The live dashboard polls /api/status + one /screen per visible
# slot every few seconds, and "start servers" fans out to every node at once — so the
# controller was churning hundreds of one-shot connections and drowning in
# "HTTPConnectionPool(host=…): Max retries exceeded" / pool-full noise (the old
# sheet-based bots had NO such controller↔node layer, which is why it never showed there).
# A pooled, keep-alive Session with a generous per-host pool fixes it: connections are
# reused, and enough are kept so concurrent screen polls to one node don't exhaust the pool.
# Retry ONLY on connection failures (connect=1) — those never reached the node, so it is
# safe even for POSTs (start/stop); reads/statuses are NOT retried (no double-actions).
import requests as _rq
from requests.adapters import HTTPAdapter as _HTTPAdapter
try:
    from urllib3.util.retry import Retry as _Retry
    _AGENT_RETRY = _Retry(total=1, connect=1, read=0, status=0, backoff_factor=0.3)
except Exception:
    _AGENT_RETRY = 0
_AGENT_SESSION = _rq.Session()
_agent_adapter = _HTTPAdapter(pool_connections=32, pool_maxsize=64, max_retries=_AGENT_RETRY)
_AGENT_SESSION.mount("http://", _agent_adapter)
_AGENT_SESSION.mount("https://", _agent_adapter)

_GENERATED_PASS = False
if not DASHBOARD_PASS and not os.path.exists(PASS_FILE):
    DASHBOARD_PASS = secrets.token_urlsafe(12)
    _GENERATED_PASS = True
    print("\n" + "=" * 66, flush=True)
    print("  No DASHBOARD_PASS set and no .controller_pass on disk.", flush=True)
    print("  Generated a one-time admin password — copy it now:\n", flush=True)
    print(f"      user: {DASHBOARD_USER}", flush=True)
    print(f"      pass: {DASHBOARD_PASS}\n", flush=True)
    print("  It is NOT stored. Set DASHBOARD_PASS in .env, or sign in and use", flush=True)
    print("  /changepw to persist a hash to .controller_pass.", flush=True)
    print("=" * 66 + "\n", flush=True)

app = Flask(__name__)
# Cap upload size so a huge (or malicious) email/name file can't exhaust memory —
# _parse_upload reads the whole file in. 16 MB is ~ hundreds of thousands of rows.
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024


# ---- artifacts: bot screenshots + logs ----------------------------------
# The bots save screenshots into screenshots/ with a CATEGORY prefix + an email-derived
# name (e.g. PAYMENT_MISSING_johnGmail.png). We categorise by that prefix so the
# dashboard can filter by error category and search by email, then view/clean them.
SHOTS_DIR = os.path.join(HERE, "screenshots")
LOGS_DIR = os.path.join(HERE, "instance_logs")

# (filename prefix, friendly category). Order matters — first match wins.
_SHOT_CATEGORIES = [
    ("EMAILFILL_FAIL_",   "Email fill failed"),
    ("EMAILDEBUG_",       "Email debug"),
    ("CARD_BTN_MISSING_", "Card button missing"),
    ("PAYMENT_MISSING_",  "Payment form missing"),
    ("CORP_SUBMIT_FAIL_", "Corporate submit failed"),
    ("CORP_MISSING_",     "Corporate form missing"),
    ("CONFIRMDEBUG_",     "Confirmation debug"),
    ("captcha_",          "Captcha (reader)"),
]


def _classify_shot(fname):
    """(category, email) for a screenshot filename. Unknown prefix => 'Final / success',
    with the email being the whole stem (the buyer saves <user><provider>.png on finish)."""
    base = os.path.basename(fname)
    for pref, cat in _SHOT_CATEGORIES:
        if base.startswith(pref):
            return cat, base[len(pref):].rsplit(".", 1)[0]
    return "Final / success", base.rsplit(".", 1)[0]


def _list_local_shots():
    """Walk screenshots/ (+ its instance<N>/ subdirs) -> [{name, rel, category, email,
    kind, size, mtime}]. `rel` is the path relative to SHOTS_DIR, used to serve/delete."""
    out = []
    if not os.path.isdir(SHOTS_DIR):
        return out
    for root, _dirs, files in os.walk(SHOTS_DIR):
        for f in files:
            if not f.lower().endswith((".png", ".jpg", ".jpeg")):
                continue
            full = os.path.join(root, f)
            rel = os.path.relpath(full, SHOTS_DIR)
            cat, email = _classify_shot(f)
            kind = "reader" if cat.startswith("Captcha") or "instance" in rel else "buyer"
            try:
                stt = os.stat(full)
            except OSError:
                continue
            out.append({"name": f, "rel": rel, "category": cat, "email": email,
                        "kind": kind, "size": stt.st_size, "mtime": int(stt.st_mtime)})
    out.sort(key=lambda x: x["mtime"], reverse=True)
    return out


def _safe_rel(rel):
    """Resolve `rel` under SHOTS_DIR, refusing any path traversal outside it."""
    full = os.path.normpath(os.path.join(SHOTS_DIR, rel))
    if not full.startswith(os.path.abspath(SHOTS_DIR) + os.sep) and full != os.path.abspath(SHOTS_DIR):
        return None
    return full


# ---- sidebar icons ------------------------------------------------------
# Inline SVG paths, not an icon font: one less asset to vendor, and a font that
# fails to load leaves the nav as unreadable boxes. Consumed by _layout.html.
_ICONS = {
    "home":       '<rect x="3" y="3" width="7" height="9"/><rect x="14" y="3" width="7" height="5"/>'
                  '<rect x="14" y="12" width="7" height="9"/><rect x="3" y="16" width="7" height="5"/>',
    "buyer":      '<circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/>'
                  '<path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/>',
    "reader":     '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>'
                  '<path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>',
    "infra":      '<rect x="2" y="2" width="20" height="8" rx="2"/><rect x="2" y="14" width="20" height="8" rx="2"/>'
                  '<line x1="6" y1="6" x2="6.01" y2="6"/><line x1="6" y1="18" x2="6.01" y2="18"/>',
    "artifacts":  '<rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/>'
                  '<polyline points="21 15 16 10 5 21"/>',
    "records":    '<rect x="3" y="3" width="18" height="18" rx="2"/><line x1="3" y1="9" x2="21" y2="9"/>'
                  '<line x1="3" y1="15" x2="21" y2="15"/><line x1="9" y1="3" x2="9" y2="21"/>',
    "cardgen":    '0000000000000000"1" y="4" width="22" height="16" rx="2"/><line x1="1" y1="10" x2="23" y2="10"/>'
                  '<line x1="6" y1="15" x2="10" y2="15"/>',
    "dataentry":  '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>'
                  '<polyline points="14 2 14 8 20 8"/><line x1="12" y1="18" x2="12" y2="12"/><line x1="9" y1="15" x2="15" y2="15"/>',
    "subscription": '<path d="M20 12V8H6a2 2 0 0 1-2-2c0-1.1.9-2 2-2h12v4"/><path d="M4 6v12c0 1.1.9 2 2 2h14v-4"/>'
                  '<path d="M18 12a2 2 0 0 0 0 4h4v-4z"/>',
    "read":       '<path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>',
    "campaign":   '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
    "cards":      '0000000000000000"1" y="4" width="22" height="16" rx="2"/><line x1="1" y1="10" x2="23" y2="10"/>',
    "identities": '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/>'
                  '<path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "review":     '<path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>'
                  '<line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>',
    "control":    '<line x1="4" y1="21" x2="4" y2="14"/><line x1="4" y1="10" x2="4" y2="3"/>'
                  '<line x1="12" y1="21" x2="12" y2="12"/><line x1="12" y1="8" x2="12" y2="3"/>'
                  '<line x1="20" y1="21" x2="20" y2="16"/><line x1="20" y1="12" x2="20" y2="3"/>'
                  '<line x1="1" y1="14" x2="7" y2="14"/><line x1="9" y1="8" x2="15" y2="8"/>'
                  '<line x1="17" y1="16" x2="23" y2="16"/>',
    "servers":    '<rect x="2" y="2" width="20" height="8" rx="2"/><rect x="2" y="14" width="20" height="8" rx="2"/>'
                  '<line x1="6" y1="6" x2="6.01" y2="6"/><line x1="6" y1="18" x2="6.01" y2="18"/>',
    "settings":   '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>',
}


@app.template_global()
def icon(key):
    return _ICONS.get(key, _ICONS["home"])


# ---- config -------------------------------------------------------------
def load_nodes():
    try:
        with open(NODES_FILE) as f:
            data = json.load(f)
    except Exception:
        return [], {}
    return data.get("nodes", []), data.get("sheet", {})


NODES, SHEET_CFG = load_nodes()
_nodes_lock = threading.Lock()


def reload_nodes():
    """Re-read nodes.json and rebind the module globals (runtime, no restart)."""
    global NODES, SHEET_CFG
    with _nodes_lock:
        NODES, SHEET_CFG = load_nodes()
    return NODES


def save_nodes(nodes, sheet):
    """Validate + atomically write nodes.json, then reload globals."""
    clean = []
    for n in nodes:
        if not isinstance(n, dict):
            continue
        name = str(n.get("name", "")).strip()
        base_url = str(n.get("base_url", "")).strip()
        if not name or not base_url.startswith("http"):
            raise ValueError("each node needs a name and an http base_url")
        clean.append({
            "name": name,
            "base_url": base_url.rstrip("/"),
            "token": str(n.get("token", "")),
            "max_instances": max(0, int(n.get("max_instances", 0) or 0)),
            "instance_offset": max(0, int(n.get("instance_offset", 0) or 0)),
            "vnc_host": str(n.get("vnc_host", "")).strip(),
        })
    data = {"nodes": clean, "sheet": sheet or {}}
    tmp = NODES_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, NODES_FILE)
    try: os.chmod(NODES_FILE, 0o600)
    except Exception: pass
    reload_nodes()
    return clean


# ---- auth ----------------------------------------------------------------
def _load_pw_hash():
    try:
        with open(PASS_FILE) as f:
            h = f.read().strip()
            if h:
                return h
    except Exception:
        pass
    return generate_password_hash(DASHBOARD_PASS)


def _load_secret():
    try:
        with open(SECRET_FILE, "rb") as f:
            s = f.read().strip()
            if s:
                return s
    except Exception:
        pass
    s = os.urandom(32)
    try:
        with open(SECRET_FILE, "wb") as f:
            f.write(s)
        os.chmod(SECRET_FILE, 0o600)
    except Exception:
        pass
    return s


users = {DASHBOARD_USER: _load_pw_hash()}
app.secret_key = _load_secret()
# SESSION_COOKIE_SECURE is opt-in via env: setting it unconditionally would break
# every plain-HTTP deploy (the browser silently refuses to send the cookie back,
# so login "succeeds" and then bounces straight back to /login). Turn it on when
# the controller sits behind TLS.
# ---- session lifetime ---------------------------------------------------
# There was none. `session.permanent = True` with no PERMANENT_SESSION_LIFETIME means
# Flask's default of 31 DAYS, and nothing ever forced a re-login — one successful login
# on any browser stayed valid for a month.
#
# Two separate limits, because they catch different things:
#   IDLE  — sliding. Every request pushes the cookie's expiry forward, so a session
#           dies only after this long with NO requests at all. Note the dashboard
#           polls /api/* on a timer, so an OPEN TAB keeps itself alive; this bites a
#           closed laptop, not a watched screen.
#   MAX   — absolute, measured from the moment of login and never extended. This is
#           the one that guarantees a re-login, open tab or not.
SESSION_IDLE_MINUTES = int(os.environ.get("DASHBOARD_IDLE_MINUTES", 120))
SESSION_MAX_HOURS    = int(os.environ.get("DASHBOARD_MAX_HOURS", 12))

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=(os.environ.get("SESSION_COOKIE_SECURE", "").lower()
                           in ("1", "true", "yes")),
    PERMANENT_SESSION_LIFETIME=timedelta(minutes=SESSION_IDLE_MINUTES),
    # re-send the cookie on every request so the idle window slides
    SESSION_REFRESH_EACH_REQUEST=True,
)


def _auth_fail(reason="auth required"):
    """API callers get JSON they can act on; humans get the login page. The dashboard's
    JS polls /api/*, so it must be able to tell "session expired" from a real error and
    send the operator back to /login instead of silently showing stale numbers."""
    if request.path.startswith("/api/"):
        return jsonify({"error": reason, "login": "/login"}), 401
    return redirect("/login?next=" + html.escape(request.path))


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get("user") not in users:
            return _auth_fail()
        # Absolute cap, counted from login and never extended by activity. Without it
        # a tab left open on the dashboard would never need a password again, because
        # its own polling keeps refreshing the idle window.
        if SESSION_MAX_HOURS:
            started = session.get("login_at")
            if not started or (_time.time() - float(started)) > SESSION_MAX_HOURS * 3600:
                session.clear()
                return _auth_fail("session expired")
        return f(*args, **kwargs)
    return wrapper


# ---- brute-force protection on /login -----------------------------------
# In-memory per-IP failed-login tracker. Not distributed (one controller), but that
# is exactly the deployment — a single control box. Locks an IP out after too many
# failures so the single admin password can't be brute-forced.
_LOGIN_FAILS = {}                 # ip -> [monotonic timestamps of recent failures]
_LOGIN_LOCK = threading.Lock()
_LOGIN_MAX_FAILS = 6              # within the window...
_LOGIN_WINDOW = 900              # ...15 minutes
_LOGIN_LOCKOUT = 900            # ...then locked out this long


# Trust X-Forwarded-For ONLY when the direct peer is a configured trusted proxy.
# Otherwise a client can spoof XFF to dodge the per-IP login lockout (a client-supplied
# header must never be trusted by default). Set TRUSTED_PROXIES to a comma list of the
# reverse-proxy IPs in front of the controller when there is one.
_TRUSTED_PROXIES = {p.strip() for p in os.environ.get("TRUSTED_PROXIES", "").split(",") if p.strip()}


def _client_ip():
    peer = request.remote_addr or "?"
    if peer in _TRUSTED_PROXIES:
        xff = request.headers.get("X-Forwarded-For", "")
        if xff:
            return xff.split(",")[0].strip() or peer
    return peer   # direct peer, or an untrusted one spoofing XFF -> use the real socket IP


def _login_locked(ip):
    now = _time.monotonic()
    with _LOGIN_LOCK:
        fails = [t for t in _LOGIN_FAILS.get(ip, []) if now - t < _LOGIN_WINDOW]
        _LOGIN_FAILS[ip] = fails
        return len(fails) >= _LOGIN_MAX_FAILS


def _login_record_fail(ip):
    now = _time.monotonic()
    with _LOGIN_LOCK:
        _LOGIN_FAILS.setdefault(ip, []).append(now)


def _login_clear(ip):
    with _LOGIN_LOCK:
        _LOGIN_FAILS.pop(ip, None)


@app.after_request
def _security_headers(resp):
    # Defensive headers on every response. Clickjacking, MIME-sniffing, referer leak.
    resp.headers.setdefault("X-Frame-Options", "DENY")
    resp.headers.setdefault("X-Content-Type-Options", "nosniff")
    resp.headers.setdefault("Referrer-Policy", "same-origin")
    # CSP: everything is self-hosted (vendored bootstrap/apexcharts/datatable, inline
    # styles, data: favicon). 'unsafe-inline' is required because the templates use
    # inline <script> and onclick handlers; it still blocks loading/exfiltrating to any
    # external origin, so a stray XSS can't phone home. connect-src 'self' keeps fetch
    # on-origin. No object/frame embedding.
    resp.headers.setdefault("Content-Security-Policy",
        "default-src 'self'; script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com data:; img-src 'self' data:; "
        "connect-src 'self'; frame-ancestors 'none'; object-src 'none'; base-uri 'self'")
    return resp


@app.errorhandler(413)
def _too_large(_e):
    # Werkzeug raises RequestEntityTooLarge past MAX_CONTENT_LENGTH; surface it as a
    # clean 413 instead of the upload route's generic 500.
    return jsonify({"error": "file too large (max 16 MB)"}), 413


# ---- agent communication -------------------------------------------------
def agent_call(node, path, method="GET", json_body=None):
    url = node["base_url"].rstrip("/") + path
    headers = {"X-Agent-Token": node.get("token", "")}
    try:
        r = requests.request(method, url, headers=headers, json=json_body, timeout=HTTP_TIMEOUT)
        if r.status_code == 200:
            ct = r.headers.get("Content-Type", "")
            return True, (r.json() if "json" in ct else r.content)
        return False, f"HTTP {r.status_code}"
    except requests.exceptions.RequestException as e:
        return False, str(e)[:120]


def broadcast(path, payload):
    """POST `payload` to `path` on every node in parallel. Returns per-node detail."""
    if not NODES:
        return []

    def one(node):
        ok, data = agent_call(node, path, "POST", payload)
        msg = data.get("msg") if (ok and isinstance(data, dict)) else data
        return {"node": node["name"], "ok": bool(ok), "msg": msg}

    with ThreadPoolExecutor(max_workers=min(8, len(NODES))) as ex:
        return list(ex.map(one, NODES))


def _read_json_file(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default


def _atomic_write_json(path, data, secret=False):
    import shutil
    text = json.dumps(data, indent=2)
    bak, tmp = path + ".bak", path + ".tmp"
    if os.path.exists(path):
        try: shutil.copy2(path, bak)
        except Exception: pass
    with open(tmp, "w") as f:
        f.write(text)
    os.replace(tmp, path)
    if secret:
        try: os.chmod(path, 0o600)
        except Exception: pass


def fetch_all_status():
    def one(idx_node):
        idx, node = idx_node
        ok, data = agent_call(node, "/api/status")
        base = {"id": idx, "name": node["name"],
                "base_url": node.get("base_url", ""),
                "vnc_host": node.get("vnc_host", ""),
                "max_instances": node.get("max_instances", 0),
                "instance_offset": node.get("instance_offset", 0)}
        if ok and isinstance(data, dict):
            base.update(data)
            base["online"] = True
            if not base.get("max_instances"):
                base["max_instances"] = data.get("max_instances", 0)
            return base
        base.update({"online": False, "error": data if isinstance(data, str) else "unreachable",
                     "slots": {}, "summary": {"running": 0, "idle": 0, "crashed": 0},
                     "cpus": 0})
        return base

    if not NODES:
        return []
    with ThreadPoolExecutor(max_workers=min(8, len(NODES))) as ex:
        return list(ex.map(one, enumerate(NODES)))




# ====================== ROUTES: auth =====================================
@app.route("/login", methods=["GET", "POST"])
def login():
    nxt = request.values.get("next", "/")
    # Must be a same-site path. Reject protocol-relative (//evil.com) and backslash
    # (/\evil.com) forms, which browsers treat as absolute -> open redirect.
    if (not nxt.startswith("/")) or nxt.startswith("//") or nxt.startswith("/\\"):
        nxt = "/"
    if request.method == "POST":
        ip = _client_ip()
        if _login_locked(ip):
            return _login_render(
                nxt, "Too many failed attempts. Try again in a few minutes.")
        u = request.form.get("username", "")
        p = request.form.get("password", "")
        if u in users and check_password_hash(users[u], p):
            _login_clear(ip)
            # Regenerate the session on privilege change (session-fixation defence):
            # a pre-login session id must not carry into the authenticated session.
            session.clear()
            session.permanent = True
            session["user"] = u
            # stamped once, never refreshed — this is what SESSION_MAX_HOURS measures
            session["login_at"] = _time.time()
            return redirect(nxt)
        _login_record_fail(ip)
        return _login_render(nxt, "Wrong username or password.")
    if session.get("user") in users:
        return redirect(nxt)
    return _login_render(nxt)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/changepw", methods=["GET", "POST"])
@login_required
def changepw():
    if request.method == "POST":
        cur = request.form.get("current", "")
        new = request.form.get("new", "")
        confirm = request.form.get("confirm", "")
        if not check_password_hash(users[DASHBOARD_USER], cur):
            return _changepw_render("Current password is incorrect.", False)
        if len(new) < 6:
            return _changepw_render("New password must be at least 6 characters.", False)
        if new != confirm:
            return _changepw_render("New passwords do not match.", False)
        h = generate_password_hash(new)
        try:
            with open(PASS_FILE, "w") as f:
                f.write(h)
            os.chmod(PASS_FILE, 0o600)
        except Exception as e:
            return _changepw_render(f"Could not save: {e}", False)
        users[DASHBOARD_USER] = h
        return _changepw_render("Password changed.", True)
    return _changepw_render()


# ====================== ROUTES: API (slot-level) =========================
@app.route("/api/overview")
@login_required
def overview():
    nodes = fetch_all_status()
    agg = {"total_nodes": len(NODES), "online": 0,
           "total_slots": 0, "running": 0, "idle": 0, "crashed": 0}
    for n in nodes:
        if n.get("online"):
            agg["online"] += 1
            agg["total_slots"] += n.get("max_instances", 0)
            s = n.get("summary", {})
            agg["running"] += s.get("running", 0)
            agg["idle"] += s.get("idle", 0)
            agg["crashed"] += s.get("crashed", 0)
    return jsonify({"agg": agg, "nodes": nodes,
                    "scripts": ["buyer", "buyer_gologin", "reader", "source", "nykaa", "eligibility", "card_generation"]})


def _node(i):
    return NODES[i] if 0 <= i < len(NODES) else None


@app.route("/api/node/<int:i>/slot/<int:slot>/start", methods=["POST"])
@login_required
def node_slot_start(i, slot):
    node = _node(i)
    if not node:
        return jsonify({"msg": "unknown node"}), 404
    body = request.get_json(silent=True) or {}
    ok, data = agent_call(node, f"/api/slot/{slot}/start", "POST",
                          {"script": body.get("script"), "total_of_type": body.get("total_of_type")})
    return jsonify({"msg": data.get("msg") if (ok and isinstance(data, dict)) else f"Failed: {data}"})


@app.route("/api/node/<int:i>/slot/<int:slot>/stop", methods=["POST"])
@login_required
def node_slot_stop(i, slot):
    node = _node(i)
    if not node:
        return jsonify({"msg": "unknown node"}), 404
    ok, data = agent_call(node, f"/api/slot/{slot}/stop", "POST")
    return jsonify({"msg": data.get("msg") if (ok and isinstance(data, dict)) else f"Failed: {data}"})


@app.route("/api/node/<int:i>/slot/<int:slot>/restart", methods=["POST"])
@login_required
def node_slot_restart(i, slot):
    node = _node(i)
    if not node:
        return jsonify({"msg": "unknown node"}), 404
    body = request.get_json(silent=True) or {}
    ok, data = agent_call(node, f"/api/slot/{slot}/restart", "POST",
                          {"script": body.get("script"), "total_of_type": body.get("total_of_type")})
    return jsonify({"msg": data.get("msg") if (ok and isinstance(data, dict)) else f"Failed: {data}"})


@app.route("/api/node/<int:i>/start_all", methods=["POST"])
@login_required
def node_start_all(i):
    node = _node(i)
    if not node:
        return jsonify({"msg": "unknown node"}), 404
    body = request.get_json(silent=True) or {}
    ok, data = agent_call(node, "/api/start_all", "POST",
                          {"assignments": body.get("assignments", [])})
    return jsonify({"msg": data.get("msg") if (ok and isinstance(data, dict)) else f"Failed: {data}"})


@app.route("/api/node/<int:i>/stop_all", methods=["POST"])
@login_required
def node_stop_all(i):
    node = _node(i)
    if not node:
        return jsonify({"msg": "unknown node"}), 404
    ok, data = agent_call(node, "/api/stop_all", "POST")
    return jsonify({"msg": data.get("msg") if (ok and isinstance(data, dict)) else f"Failed: {data}"})


@app.route("/api/node/<int:i>/target", methods=["GET", "POST"])
@login_required
def node_target(i):
    node = _node(i)
    if not node:
        return jsonify({"msg": "unknown node"}), 404
    if request.method == "GET":
        ok, data = agent_call(node, "/api/target")
        return jsonify(data if (ok and isinstance(data, dict)) else {"mode": "manual", "mix": {}})
    body = request.get_json(silent=True) or {}
    ok, data = agent_call(node, "/api/target", "POST",
                          {"mode": body.get("mode"), "mix": body.get("mix")})
    return jsonify({"msg": data.get("msg") if (ok and isinstance(data, dict)) else f"Failed: {data}"})


@app.route("/api/node/<int:i>/slot/<int:slot>/release", methods=["POST"])
@login_required
def node_slot_release(i, slot):
    node = _node(i)
    if not node:
        return jsonify({"msg": "unknown node"}), 404
    ok, data = agent_call(node, f"/api/slot/{slot}/release", "POST")
    return jsonify({"msg": data.get("msg") if (ok and isinstance(data, dict)) else f"Failed: {data}"})


@app.route("/api/target_all", methods=["POST"])
@login_required
def target_all():
    """Apply ONE plan (mode + mix) to EVERY server at once — so the operator never
    has to configure servers one by one."""
    body = request.get_json(silent=True) or {}
    mode = body.get("mode", "auto")
    mix = body.get("mix") or {}
    detail = []
    for node in NODES:
        # Per-server cap: each server has a different slot count (max_instances). The node
        # rejects (400) an auto mix whose total exceeds its slots. So scale the mix DOWN to
        # fit THIS server — small servers get fewer, big servers get more — instead of one
        # fixed mix that 400s on the smallest box.
        nmix = {k: int(v) for k, v in mix.items()}
        node_max = int(node.get("max_instances", 0) or 0)
        if mode == "auto" and node_max:
            total = sum(nmix.values())
            if total > node_max and total > 0:
                nmix = {k: int(v * node_max / total) for k, v in nmix.items()}
                leftover = node_max - sum(nmix.values())   # hand rounding remainder to the biggest job
                if leftover > 0 and nmix:
                    big = max(nmix, key=lambda k: int(mix.get(k, 0)))
                    nmix[big] = nmix.get(big, 0) + leftover
        ok, d = agent_call(node, "/api/target", "POST", {"mode": mode, "mix": nmix})
        detail.append({"node": node["name"], "ok": bool(ok),
                       "msg": (d.get("msg") if (ok and isinstance(d, dict)) else d)})
    okc = sum(1 for x in detail if x["ok"])
    return jsonify({"msg": f"Plan applied to {okc}/{len(NODES)} server(s)", "detail": detail})


@app.route("/api/source/batches", methods=["GET"])
@login_required
def source_batches():
    """Progress for every batch + the fleet-wide roll-up. This is the answer to
    'how many of my 500 are done' — counts come from the rows themselves, so they are
    exact regardless of how many servers/instances are chewing through them."""
    import db
    try:
        return jsonify(db.source_progress())
    except Exception as e:
        return jsonify({"error": str(e)[:200], "batches": [], "agg": {}}), 500


@app.route("/api/source/batches", methods=["POST"])
@login_required
def source_batch_create():
    """Submit "run <url> <count> times". Seeds `count` claimable rows; every source
    instance on every server draws from them, so the fleet splits the count itself."""
    import db
    body = request.get_json(silent=True) or {}
    try:
        out = db.create_source_batch(body.get("url"), body.get("count"),
                                     (body.get("note") or "").strip() or None)
    except ValueError as e:
        return jsonify({"msg": str(e)}), 400
    except Exception as e:
        return jsonify({"msg": f"error: {str(e)[:200]}"}), 500
    return jsonify({"msg": f"Batch #{out['batch_id']} created — {out['created']} runs queued",
                    **out})


@app.route("/api/source/batch/<int:bid>/status", methods=["POST"])
@login_required
def source_batch_status(bid):
    """active | stopped. Stopping makes the remaining rows unclaimable at once (claims
    filter on active batches) without losing what's already done — flip back to resume."""
    import db
    body = request.get_json(silent=True) or {}
    status = body.get("status", "stopped")
    try:
        n = db.set_source_batch_status(bid, status)
    except ValueError as e:
        return jsonify({"msg": str(e)}), 400
    except Exception as e:
        return jsonify({"msg": f"error: {str(e)[:200]}"}), 500
    return jsonify({"msg": f"Batch #{bid} {status}" if n else f"Batch #{bid} not found"})


@app.route("/api/nykaa/batches", methods=["GET"])
@login_required
def nykaa_batches():
    """Progress for every batch + the fleet-wide roll-up — 'how many of my N are done'.
    Counts come from the rows themselves, so they are exact however many boxes work."""
    import db
    try:
        return jsonify(db.nykaa_progress())
    except Exception as e:
        return jsonify({"error": str(e)[:200], "batches": [], "agg": {}}), 500


@app.route("/api/nykaa/batches", methods=["POST"])
@login_required
def nykaa_batch_create():
    """Submit "make N accounts". Seeds N claimable rows; every nykaa instance on every
    server draws from them, so the fleet splits the count itself."""
    import db
    body = request.get_json(silent=True) or {}
    try:
        out = db.create_nykaa_batch(body.get("count"),
                                    (body.get("note") or "").strip() or None)
    except ValueError as e:
        return jsonify({"msg": str(e)}), 400
    except Exception as e:
        return jsonify({"msg": f"error: {str(e)[:200]}"}), 500
    return jsonify({"msg": f"Batch #{out['batch_id']} created — {out['created']} accounts queued",
                    **out})


@app.route("/api/nykaa/batch/<int:bid>/status", methods=["POST"])
@login_required
def nykaa_batch_status(bid):
    """active | stopped. Stopping makes the remaining rows unclaimable at once without
    losing what is already done — flip back to resume."""
    import db
    body = request.get_json(silent=True) or {}
    try:
        n = db.set_nykaa_batch_status(bid, body.get("status", "stopped"))
    except ValueError as e:
        return jsonify({"msg": str(e)}), 400
    except Exception as e:
        return jsonify({"msg": f"error: {str(e)[:200]}"}), 500
    return jsonify({"msg": f"Batch #{bid} {body.get('status','stopped')}" if n
                           else f"Batch #{bid} not found"})


@app.route("/api/nykaa/accounts", methods=["GET"])
@login_required
def nykaa_accounts_list():
    """Created accounts, newest first. `?format=csv` downloads the lot — this replaced
    the Google Sheet, so there has to be a way to get the data OUT."""
    import db, io, csv
    try:
        limit = min(int(request.args.get("limit", 200)), 5000)
    except Exception:
        limit = 200
    try:
        offset = max(0, int(request.args.get("offset", 0)))
    except Exception:
        offset = 0
    try:
        if request.args.get("format") == "csv":
            data = db.nykaa_accounts(limit=5000, offset=0)
            buf = io.StringIO()
            w = csv.writer(buf)
            w.writerow(["id", "mobile", "name", "email", "session_file",
                        "provider", "ran_by", "created_at"])
            for a in data["accounts"]:
                w.writerow([a["id"], a["mobile"], a["name"], a["email"],
                            a["session_file"], a["provider"], a["ran_by"], a["created_at"]])
            return Response(buf.getvalue(), mimetype="text/csv", headers={
                "Content-Disposition": "attachment; filename=nykaa_accounts.csv"})
        return jsonify(db.nykaa_accounts(limit=limit, offset=offset))
    except Exception as e:
        return jsonify({"error": str(e)[:200], "accounts": [], "total": 0}), 500


@app.route("/api/nykaa/requeue_failed", methods=["POST"])
@login_required
def nykaa_requeue_failed():
    """'failed' rows back to 'pending' — for a run ruined by a broken box."""
    import db
    body = request.get_json(silent=True) or {}
    bid = body.get("batch_id")
    try:
        n = db.requeue_failed_nykaa(int(bid) if bid not in (None, "") else None)
    except Exception as e:
        return jsonify({"msg": f"error: {str(e)[:200]}"}), 500
    return jsonify({"msg": f"{n} failed account(s) queued again"})


@app.route("/api/nykaa/clear_stuck", methods=["POST"])
@login_required
def nykaa_clear_stuck():
    """Rows a killed instance left 'running' hold a piece of the count forever."""
    import db
    body = request.get_json(silent=True) or {}
    try:
        n = db.clear_stuck_nykaa(int(body.get("minutes") or 30))
    except Exception as e:
        return jsonify({"msg": f"error: {str(e)[:200]}"}), 500
    return jsonify({"msg": f"{n} stuck nykaa row(s) returned to pending"})


@app.route("/api/source/requeue_failed", methods=["POST"])
@login_required
def source_requeue_failed():
    """'failed' rows -> back to 'pending' so a run ruined by a broken box can be redone.

    Body {batch_id: n} for one batch, or {} for all. A batch that had already flipped
    to 'done' on failures alone is reopened, otherwise its rows would sit pending in an
    inactive batch and never be claimed."""
    import db
    body = request.get_json(silent=True) or {}
    bid = body.get("batch_id")
    try:
        n = db.requeue_failed_source(int(bid) if bid not in (None, "") else None)
    except Exception as e:
        return jsonify({"msg": f"error: {str(e)[:200]}"}), 500
    return jsonify({"msg": f"{n} failed visit(s) queued again"})


@app.route("/api/source/clear_stuck", methods=["POST"])
@login_required
def source_clear_stuck():
    """Rows a killed instance left 'running' hold a piece of the count forever, so the
    batch can never reach 100%. Return them to the pool."""
    import db
    body = request.get_json(silent=True) or {}
    try:
        n = db.clear_stuck_source(int(body.get("minutes") or 30))
    except Exception as e:
        return jsonify({"msg": f"error: {str(e)[:200]}"}), 500
    return jsonify({"msg": f"{n} stuck source row(s) returned to pending"})


@app.route("/api/node/<int:i>/card_otp", methods=["POST"])
@login_required
def node_card_otp(i):
    node = _node(i)
    if not node:
        return jsonify({"msg": "unknown node"}), 404
    body = request.get_json(silent=True) or {}
    ok, data = agent_call(node, "/api/card_otp", "POST", {"otp": body.get("otp", "")})
    return jsonify({"msg": data.get("msg") if (ok and isinstance(data, dict)) else f"Failed: {data}"})


@app.route("/api/node/<int:i>/slot/<int:slot>/logs")
@login_required
def node_slot_logs(i, slot):
    node = _node(i)
    if not node:
        return jsonify({"msg": "unknown node"}), 404
    lines = request.args.get("lines", "200")
    ok, data = agent_call(node, f"/api/slot/{slot}/logs?lines={lines}")
    if ok and isinstance(data, dict):
        return jsonify(data)
    return jsonify({"logs": f"Failed: {data}"}), 200


# ---- whole-server stop (used by "Stop all" global) ----------------------
@app.route("/api/stop_all", methods=["POST"])
@login_required
def stop_all_nodes():
    for node in NODES:
        agent_call(node, "/api/stop_all", "POST")
    return jsonify({"msg": f"Stop sent to {len(NODES)} servers"})


@app.route("/api/restart_all", methods=["POST"])
@login_required
def restart_all_nodes():
    """Restart every running bot on every server in place, so they re-read the freshly
    pushed config.json (e.g. a changed INSTANCES_PER_EMP) — fully from the dashboard,
    no terminal needed."""
    detail = broadcast("/api/restart_all", {})
    ok = sum(1 for d in detail if d["ok"])
    return jsonify({"msg": f"restart triggered on {ok}/{len(NODES)} server(s)",
                    "detail": detail})


# ---- emp_id -> instance map (buyer). Same map pushed to EVERY worker. ----
# ---- central config / credentials / settings (edit once → push to all) --------
@app.route("/api/config", methods=["GET"])
@login_required
def get_config():
    # Redact secret-valued keys — never ship credentials to the browser. A non-empty
    # secret comes back as the sentinel so the UI shows "set" without exposing it; the
    # POST handler treats an unchanged sentinel as "keep existing" (see set_config).
    cfg = dict(_read_json_file(MASTER_CONFIG, {}))
    for k in _SECRET_CONFIG_KEYS:
        if cfg.get(k):
            cfg[k] = _SECRET_SENTINEL
    return jsonify(cfg)


# Config keys whose values are secrets and must not be sent to the browser in cleartext.
_SECRET_CONFIG_KEYS = {"DB_PASSWORD", "PROXY_PASSWORD", "ACCOUNT_PASSWORD",
                       "CAPTCHA_API_KEY", "CAPSOLVER_API_KEY", "OTP_FETCH_TOKEN",
                       "HDFC_3DS_PIN", "GOOGLE_CREDENTIALS"}
_SECRET_SENTINEL = "CHANGE_ME_SECRET"   # shown in the UI as ••••••


@app.route("/api/config", methods=["POST"])
@login_required
def set_config():
    body = request.get_json(silent=True) or {}
    cfg = body.get("config", body)
    if not isinstance(cfg, dict):
        return jsonify({"msg": "config must be a JSON object"}), 400
    # Keep the current secret when the client sends back the unchanged sentinel (it
    # never received the real value), so saving other fields doesn't wipe credentials.
    current = _read_json_file(MASTER_CONFIG, {})
    for k in _SECRET_CONFIG_KEYS:
        if cfg.get(k) == _SECRET_SENTINEL:
            if current.get(k) is not None:
                cfg[k] = current[k]
            else:
                cfg.pop(k, None)
    try:
        _atomic_write_json(MASTER_CONFIG, cfg, secret=True)
    except Exception as e:
        return jsonify({"msg": f"save error: {e}"}), 500
    detail = broadcast("/api/config", {"config": cfg})
    pushed = sum(1 for d in detail if d["ok"])
    return jsonify({"msg": f"config saved + pushed to {pushed}/{len(NODES)} server(s)",
                    "detail": detail})


@app.route("/api/settings", methods=["GET"])
@login_required
def get_settings():
    return jsonify(_read_json_file(MASTER_SETTINGS, {}))


@app.route("/api/settings", methods=["POST"])
@login_required
def set_settings():
    body = request.get_json(silent=True) or {}
    s = body.get("settings", body)
    if not isinstance(s, dict):
        return jsonify({"msg": "settings must be a JSON object"}), 400
    try:
        _atomic_write_json(MASTER_SETTINGS, s, secret=True)
    except Exception as e:
        return jsonify({"msg": f"save error: {e}"}), 500
    detail = broadcast("/api/settings", {"settings": s})
    pushed = sum(1 for d in detail if d["ok"])
    return jsonify({"msg": f"settings saved + pushed to {pushed}/{len(NODES)} server(s)",
                    "detail": detail})


@app.route("/api/employees", methods=["GET"])
@login_required
def get_employees():
    """Master pool of employee IDs (added once, chosen per campaign). Stored in
    settings.json under EMPLOYEE_IDS; dashboard-only, not pushed to workers."""
    s = _read_json_file(MASTER_SETTINGS, {})
    return jsonify({"employees": s.get("EMPLOYEE_IDS", [])})


@app.route("/api/employees", methods=["POST"])
@login_required
def set_employees():
    body = request.get_json(silent=True) or {}
    emps = body.get("employees", [])
    if not isinstance(emps, list):
        return jsonify({"error": "employees must be a list"}), 400
    seen, clean = set(), []
    for e in emps:
        e = str(e).strip()
        if e and e not in seen and len(e) <= 64:
            seen.add(e)
            clean.append(e)
    s = dict(_read_json_file(MASTER_SETTINGS, {}))
    s["EMPLOYEE_IDS"] = clean
    try:
        _atomic_write_json(MASTER_SETTINGS, s, secret=True)
    except Exception as e:
        return jsonify({"error": f"save error: {e}"}), 500
    return jsonify({"ok": True, "employees": clean})


@app.route("/api/employees/upload", methods=["POST"])
@login_required
def upload_employees():
    """Bulk-add employee IDs from a .csv/.xlsx. Every non-empty cell becomes an ID
    (a header row like 'employee_id'/'emp'/'id' is skipped). Merged into the pool."""
    try:
        if "file" not in request.files:
            return jsonify({"error": "no file uploaded"}), 400
        rows = _parse_upload_raw(request.files["file"])
        tokens = [c for r in rows for c in r if c]
        # drop a header row whose first cell is an obvious label
        if tokens and tokens[0].lower() in ("employee_id", "employee id", "employee",
                                            "emp", "emp_id", "id", "employees"):
            tokens = tokens[1:]
        existing = list(_read_json_file(MASTER_SETTINGS, {}).get("EMPLOYEE_IDS", []))
        seen, clean = set(), []
        for e in existing + tokens:
            e = str(e).strip()
            if e and e not in seen and len(e) <= 64:
                seen.add(e)
                clean.append(e)
        s = dict(_read_json_file(MASTER_SETTINGS, {}))
        added = len(clean) - len(existing)
        s["EMPLOYEE_IDS"] = clean
        _atomic_write_json(MASTER_SETTINGS, s, secret=True)
        return jsonify({"ok": True, "employees": clean,
                        "message": f"{added} added, {len(clean)} total"})
    except UploadError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"[error] {request.path}: {e}", flush=True)
        return jsonify({"error": "server error"}), 500


# ---- Corporates (runtime corp switch: marcadeo / streakads / …) --------------
@app.route("/api/corporates", methods=["GET"])
@login_required
def api_corporates_list():
    import db
    try:
        return jsonify({"corporates": db.list_corporates()})
    except Exception as e:
        print(f"[error] {request.path}: {e}", flush=True)
        return jsonify({"error": str(e), "corporates": []}), 500


@app.route("/api/corporates", methods=["POST"])
@login_required
def api_corporates_add():
    import db
    body = request.get_json(silent=True) or {}
    try:
        r = db.add_corporate(body.get("corp_id"), body.get("label"), body.get("note"))
        # optional inline employees on create
        emps = body.get("employee_ids") or body.get("employees")
        if emps:
            r.update(db.add_corp_employees(r["corp_id"], emps))
        return jsonify({"ok": True, **r})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/corporates/<corp_id>/active", methods=["POST"])
@login_required
def api_corporate_active(corp_id):
    import db
    body = request.get_json(silent=True) or {}
    try:
        return jsonify({"ok": True, **db.set_corporate_active(corp_id, bool(body.get("active")))})
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/corporates/<corp_id>", methods=["DELETE"])
@login_required
def api_corporate_delete(corp_id):
    import db
    try:
        return jsonify({"ok": True, **db.delete_corporate(corp_id)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/corporates/<corp_id>/login", methods=["POST"])
@login_required
def api_corp_login(corp_id):
    """Store a corporate's card-generation portal login. Password blank = keep existing."""
    import db
    body = request.get_json(silent=True) or {}
    try:
        return jsonify({"ok": True, **db.set_corporate_login(
            corp_id, body.get("portal_username"), body.get("portal_password"))})
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/corporates/<corp_id>/employees", methods=["POST"])
@login_required
def api_corp_emps_add(corp_id):
    import db
    body = request.get_json(silent=True) or {}
    try:
        emps = body.get("employee_ids") or body.get("employees") or body.get("raw")
        return jsonify({"ok": True, **db.add_corp_employees(corp_id, emps)})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/corporates/<corp_id>/employees/upload", methods=["POST"])
@login_required
def api_corp_emps_upload(corp_id):
    """Bulk-add a corporate's employees from a .csv/.xlsx (every non-empty cell)."""
    import db
    try:
        if "file" not in request.files:
            return jsonify({"error": "no file uploaded"}), 400
        rows = _parse_upload_raw(request.files["file"])
        tokens = [c for r in rows for c in r if c]
        if tokens and tokens[0].lower() in ("employee_id", "employee id", "employee",
                                            "emp", "emp_id", "id", "employees"):
            tokens = tokens[1:]
        return jsonify({"ok": True, **db.add_corp_employees(corp_id, tokens)})
    except UploadError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/corporates/<corp_id>/employees/<emp_id>/active", methods=["POST"])
@login_required
def api_corp_emp_active(corp_id, emp_id):
    import db
    body = request.get_json(silent=True) or {}
    try:
        return jsonify({"ok": True, **db.set_corp_employee_active(corp_id, emp_id, bool(body.get("active")))})
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/corporates/<corp_id>/employees/<emp_id>", methods=["DELETE"])
@login_required
def api_corp_emp_delete(corp_id, emp_id):
    import db
    try:
        return jsonify({"ok": True, **db.delete_corp_employee(corp_id, emp_id)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/reader/clear_stuck", methods=["POST"])
@login_required
def api_reader_clear_stuck():
    """Free reader rows stuck 'running' (timed-out readers holding a slot)."""
    try:
        import db
        n = db.clear_stuck_reads(minutes=8)
        return jsonify({"ok": True, "msg": f"cleared {n} stuck reader row(s)"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/node/<int:i>/push_all", methods=["POST"])
@login_required
def node_push_all(i):
    """Bring ONE (e.g. freshly registered) node up to date with master config,
    credentials and settings."""
    node = _node(i)
    if not node:
        return jsonify({"msg": "unknown node"}), 404
    out = []
    cfg = _read_json_file(MASTER_CONFIG, None)
    if isinstance(cfg, dict):
        ok, d = agent_call(node, "/api/config", "POST", {"config": cfg})
        out.append(f"config: {'ok' if ok else d}")
    st = _read_json_file(MASTER_SETTINGS, None)
    if isinstance(st, dict):
        ok, d = agent_call(node, "/api/settings", "POST", {"settings": st})
        out.append(f"settings: {'ok' if ok else d}")
    return jsonify({"msg": f"pushed to {node['name']}", "detail": out})


# ---- node CRUD (register/edit/remove servers from the dashboard) --------------
_TOKEN_KEEP = "CHANGE_ME_TOKEN"          # PUT sentinel: keep the existing token


def _mask_token(t):
    t = t or ""
    return ("••••" + t[-4:]) if len(t) >= 4 else ("••••" if t else "")


@app.route("/api/nodes", methods=["GET"])
@login_required
def api_get_nodes():
    out = []
    for i, n in enumerate(NODES):
        out.append({"id": i, "name": n.get("name", ""), "base_url": n.get("base_url", ""),
                    "token_masked": _mask_token(n.get("token", "")),
                    "max_instances": n.get("max_instances", 0),
                    "instance_offset": n.get("instance_offset", 0),
                    "vnc_host": n.get("vnc_host", "")})
    return jsonify({"nodes": out, "sheet": SHEET_CFG})


@app.route("/api/nodes", methods=["POST"])
@login_required
def api_add_node():
    body = request.get_json(silent=True) or {}
    try:
        new_list = list(NODES) + [body]
        save_nodes(new_list, SHEET_CFG)
    except Exception as e:
        return jsonify({"msg": f"invalid node: {e}"}), 400
    # Push current master config/creds/settings to the new node (best effort).
    try:
        node_push_all(len(NODES) - 1)
    except Exception:
        pass
    return jsonify({"msg": f"added {body.get('name')}"})


@app.route("/api/nodes/<int:i>", methods=["PUT"])
@login_required
def api_edit_node(i):
    if not (0 <= i < len(NODES)):
        return jsonify({"msg": "unknown node"}), 404
    body = request.get_json(silent=True) or {}
    new_list = [dict(n) for n in NODES]
    # Keep existing token if the UI sent the sentinel (user didn't retype it).
    if body.get("token", _TOKEN_KEEP) == _TOKEN_KEEP:
        body["token"] = NODES[i].get("token", "")
    new_list[i] = body
    try:
        save_nodes(new_list, SHEET_CFG)
    except Exception as e:
        return jsonify({"msg": f"invalid node: {e}"}), 400
    return jsonify({"msg": f"updated {body.get('name')}"})


@app.route("/api/nodes/<int:i>", methods=["DELETE"])
@login_required
def api_delete_node(i):
    if not (0 <= i < len(NODES)):
        return jsonify({"msg": "unknown node"}), 404
    name = NODES[i].get("name", "")
    new_list = [dict(n) for j, n in enumerate(NODES) if j != i]
    try:
        save_nodes(new_list, SHEET_CFG)
    except Exception as e:
        return jsonify({"msg": f"error: {e}"}), 400
    return jsonify({"msg": f"removed {name}"})


@app.route("/api/nodes/<int:i>/health")
@login_required
def api_node_health(i):
    node = _node(i)
    if not node:
        return jsonify({"msg": "unknown node"}), 404
    ok, data = agent_call(node, "/api/health")
    if ok and isinstance(data, dict):
        return jsonify({"online": True, "health": data})
    return jsonify({"online": False, "error": data if isinstance(data, str) else "unreachable"})


@app.route("/api/task_stats")
@login_required
def api_task_stats():
    try:
        import db
        return jsonify({"counts": db.status_counts()})
    except Exception as e:
        return jsonify({"counts": {"error": str(e)[:160]}}), 400


@app.route("/api/otp_alerts")
@login_required
def api_otp_alerts():
    """Employees with repeated OTP failures (>= threshold) for the dashboard banner."""
    try:
        import db
        return jsonify({"alerts": db.get_otp_alerts(3)})
    except Exception as e:
        return jsonify({"alerts": [], "error": str(e)[:160]}), 200


@app.route("/api/alerts")
@login_required
def api_alerts():
    """Consolidated, severity-sorted alerts for the topbar notification bell — the
    same set the dashboard 'Needs attention' panel shows (OTP failures, dying
    employees, stuck instances, offline servers), but standalone and lightweight
    (no full /api/monitor snapshot). Each item carries an href to jump to."""
    import db

    def _safe(fn, default):
        try:
            return fn() or default
        except Exception:
            return default

    items = []
    try:
        # Ambiguous buys waiting for a human — each holds a card out of the pool. With
        # "Needs Review" off the sidebar, this is how the queue stays visible; drop it and
        # held cards leak silently. Warn (not critical) — the reader clears most on its own.
        _rev = _safe(lambda: db.needs_review_count(), 0)
        if _rev:
            items.append({"sev": "warn", "kind": "REVIEW",
                          "title": f"{_rev} buy(s) awaiting review",
                          "detail": "cards held until you Confirm or Reject",
                          "href": "/review"})
        for a in _safe(lambda: db.get_otp_alerts(3), []):
            items.append({"sev": "critical", "kind": "OTP",
                          "title": f"Emp {a.get('emp_id')}: OTP failed {a.get('consecutive_failures')}× in a row",
                          "detail": f"{a.get('total_failures')} total · last {a.get('last_failure','')}",
                          "href": "/review"})
        for e in _safe(lambda: db.employee_health(3), []):
            if e.get("flag") == "dying":
                items.append({"sev": "critical", "kind": "EMP",
                              "title": f"Emp {e.get('emp_id')} dying: {e.get('rate')}% success",
                              "detail": f"{e.get('otp_fails',0)} OTP fails · {e.get('declined',0)} declined · {e.get('pending',0)} pending",
                              "href": "/records"})
        for i in _safe(lambda: db.instance_status(), []):
            if i.get("active") and (i.get("step_secs") or 0) >= 300:
                _m = (i.get("step_secs") or 0) // 60
                items.append({"sev": "warn", "kind": "STUCK",
                              "title": f"Instance {i.get('id')} stuck {int(_m)}m at {i.get('current_step','?')}",
                              "detail": f"emp {i.get('current_emp','—')} · {(i.get('current_task','') or '')[:40]}",
                              "href": "/control"})
        for w in _safe(lambda: fetch_all_status(), []):
            if not w.get("online"):
                items.append({"sev": "critical", "kind": "SERVER",
                              "title": f"Server {w.get('name')} OFFLINE",
                              "detail": "agent unreachable", "href": "/servers"})
            # Card generator waiting for the portal OTP right now — most time-sensitive
            # alert (the OTP window is ~15 min). Deep-links to the OTP app.
            elif w.get("otp_wanted"):
                items.append({"sev": "critical", "kind": "OTP",
                              "title": f"Server {w.get('name')} — card generator needs an OTP",
                              "detail": "enter it in Card OTP before the window expires",
                              "href": "/otp"})
        _rank = {"critical": 0, "warn": 1, "info": 2}
        items.sort(key=lambda x: _rank.get(x["sev"], 3))
    except Exception as e:
        return jsonify({"count": 0, "items": [], "error": str(e)[:160]}), 200
    return jsonify({"count": len(items), "items": items})


@app.route("/api/retry_failed", methods=["POST"])
@login_required
def api_retry_failed():
    """Re-run failed buyer tasks with fresh cards. Optional {campaign_id} to scope it."""
    try:
        import db
        body = request.get_json(silent=True) or {}
        cid = body.get("campaign_id")
        r = db.requeue_failed_buys(campaign_id=int(cid) if cid else None)
        if not r["considered"]:
            return jsonify({"msg": "No failed buys to retry."})
        msg = f"Retrying {r['requeued']} failed buy(s)"
        if r["no_card"]:
            msg += f" — {r['no_card']} skipped (no card available, buy more first)"
        return jsonify({"msg": msg, **r})
    except Exception as e:
        return jsonify({"msg": f"Retry failed: {str(e)[:160]}"}), 400


@app.route("/api/retry_new_email", methods=["POST"])
@login_required
def api_retry_new_email():
    """Re-run failed/ineligible buys with a MUTATED email (reusing their own card). For
    'account exists' / 'existing GOLD user' cases that only succeed on a different email."""
    try:
        import db
        body = request.get_json(silent=True) or {}
        cid = body.get("campaign_id")
        r = db.requeue_with_email_mutation(campaign_id=int(cid) if cid else None)
        if not r["considered"]:
            return jsonify({"msg": "No failed / ineligible buys to retry."})
        msg = f"Retrying {r['requeued']} buy(s) with a new email"
        if r.get("no_email"):
            msg += f" — {r['no_email']} skipped (no email on file)"
        return jsonify({"msg": msg, **r})
    except Exception as e:
        return jsonify({"msg": f"Retry failed: {str(e)[:160]}"}), 400


@app.route("/api/reset_stale", methods=["POST"])
@login_required
def api_reset_stale():
    """Free buyer + reader rows stuck 'running' (crashed bots) so they re-run."""
    try:
        import db
        b = db.reset_stale_running(360)
        r = db.reset_stale_reads(1200)
        return jsonify({"msg": f"Reset {b} buyer + {r} reader stale rows"})
    except Exception as e:
        return jsonify({"msg": f"Reset error: {str(e)[:160]}"}), 400


# ====================== ROUTES: live monitor (DB-backed) =================
# Full analytics/monitoring snapshot for the in-dashboard "Analytics" view —
# the DB-backed equivalent of the standalone dashboard.py gather(). Everything
# below is guarded so the endpoint can never 500 even if Postgres is down.
def _monitor_server_stats(active_bots):
    """CPU / RAM / uptime + live bot count (psutil if available, else /proc).
    Mirrors dashboard.py get_server_stats(); never raises."""
    s = {"cpu": "—", "ram_used": "—", "ram_total": "—", "ram_pct": "—",
         "uptime": "—", "bots_alive": active_bots}
    try:
        import psutil
        s["cpu"] = round(psutil.cpu_percent(interval=0.0), 1)
        vm = psutil.virtual_memory()
        s["ram_used"] = round(vm.used / 1e9, 1)
        s["ram_total"] = round(vm.total / 1e9, 1)
        s["ram_pct"] = round(vm.percent, 1)
        up = int(_time.time() - psutil.boot_time())
        s["uptime"] = f"{up // 3600}h {(up % 3600) // 60}m"
    except Exception:
        try:
            with open("/proc/uptime") as f:
                up = int(float(f.read().split()[0]))
            s["uptime"] = f"{up // 3600}h {(up % 3600) // 60}m"
        except Exception:
            pass
        try:
            mem = {}
            with open("/proc/meminfo") as f:
                for ln in f:
                    p = ln.split(":")
                    if len(p) == 2:
                        mem[p[0]] = int(p[1].strip().split()[0])  # kB
            tot = mem.get("MemTotal", 0) / 1e6
            avail = mem.get("MemAvailable", 0) / 1e6
            s["ram_total"] = round(tot, 1)
            s["ram_used"] = round(tot - avail, 1)
            s["ram_pct"] = round((tot - avail) / tot * 100, 1) if tot else "—"
        except Exception:
            pass
        try:
            la = os.getloadavg()[0]
            s["cpu"] = round(la / (os.cpu_count() or 1) * 100, 1)
        except Exception:
            pass
    return s


def _monitor_gather(period="all"):
    """Assemble the full DB-backed monitoring snapshot. Mirrors dashboard.py
    gather(); every db call is guarded so the route never 500s. win_hours filters the
    failure panels to the last N hours (0 = all-time) for the dashboard time-window
    toggle."""
    import db

    try:
        c = db.status_counts() or {}
    except Exception as e:
        c = {"error": str(e)[:120]}
    db_error = c.get("error", "") if isinstance(c, dict) else ""

    def g(k):
        try:
            return int(c.get(k, 0) or 0)
        except Exception:
            return 0

    total_done = (g("completed") + g("failed") + g("declined")
                  + g("ineligible") + g("unconfirmed"))
    # Success rate = completed / SETTLED. It must NOT divide by `total` (that folds in
    # pending + running, crushing the rate to a meaningless ~30%). Denominator = every
    # settled outcome: completed + failed + declined + ineligible + unconfirmed. This EXACTLY
    # matches the per-campaign / records / Transactions-tab definition (completed / non-pending),
    # so the same rate shows everywhere the client looks — no tab-to-tab disagreement.
    _settled = (g("completed") + g("failed") + g("declined")
                + g("ineligible") + g("unconfirmed"))
    stats = {
        "running": g("running"), "success": g("completed"), "failed": g("failed"),
        "declined": g("declined"), "ineligible": g("ineligible"),
        "unconfirmed": g("unconfirmed"), "total_done": total_done,
        "pending": g("pending"), "total": g("total"),
        "rate": round(g("completed") / _settled * 100, 1) if _settled else 0.0,
    }

    try:
        instances = db.instance_status() or []
    except Exception:
        instances = []
    active = sum(1 for i in instances if i.get("active"))

    try:
        recent = db.recent_transactions(30) or []
    except Exception:
        recent = []

    try:
        emps_raw = db.emp_progress() or []
    except Exception:
        emps_raw = []
    emp_rows = []
    for e in emps_raw:
        try:
            t = int(e.get("total", 0) or 0)
            done = (int(e.get("completed", 0)) + int(e.get("failed", 0))
                    + int(e.get("declined", 0)) + int(e.get("ineligible", 0))
                    + int(e.get("unconfirmed", 0)))
            emp_rows.append({
                "emp": e.get("emp_id", "—"), "total": t, "done": done,
                "pct": round(done / t * 100, 1) if t else 0.0,
                "running": int(e.get("running", 0)), "success": int(e.get("completed", 0)),
                "failed": int(e.get("failed", 0)), "declined": int(e.get("declined", 0)),
                "inelig": int(e.get("ineligible", 0)), "unconf": int(e.get("unconfirmed", 0)),
                "pending": int(e.get("pending", 0)),
            })
        except Exception:
            continue
    emp_rows.sort(key=lambda x: -x["done"])

    try:
        otp_alerts = db.get_otp_alerts(3) or []
    except Exception:
        otp_alerts = []

    try:
        rp = db.read_progress() or {}
    except Exception:
        rp = {}
    if not isinstance(rp, dict):
        rp = {}
    reader = {"total": int(rp.get("total", 0) or 0), "done": int(rp.get("done", 0) or 0),
              "failed": int(rp.get("failed", 0) or 0), "pending": int(rp.get("pending", 0) or 0),
              "running": int(rp.get("running", 0) or 0), "retry": int(rp.get("retry", 0) or 0),
              "books": int(rp.get("books_read", 0) or 0),
              "txn_found": int(rp.get("txn_found", 0) or 0),
              "txn_notfound": int(rp.get("txn_notfound", 0) or 0)}
    reader["rate"] = round(reader["done"] / reader["total"] * 100, 1) if reader["total"] else 0.0

    # ---- new analytics panels (buyer + reader); each guarded so one bad query can't
    #      blank the whole dashboard. ----
    def _safe(fn, default):
        try:
            return fn() or default
        except Exception:
            return default

    _p = (period or "all")
    analytics = {
        "period":              _p,
        "fail_breakdown":      _safe(lambda: db.failure_breakdown(12, _p), []),
        "read_fail_breakdown": _safe(lambda: db.read_failure_breakdown(12, _p), []),
        "fail_by_stage":       _safe(lambda: db.failure_by_stage(_p), []),
        "load_dist":           _safe(lambda: db.load_distribution(1000), []),
        "throughput":          _safe(lambda: db.throughput_stats(), {}),
        "read_throughput":     _safe(lambda: db.read_throughput_stats(), {}),
        "proxy_health":        _safe(lambda: db.proxy_health(15), []),
        "card_bin_health":     _safe(lambda: db.card_bin_health(15), []),
        "card_bin_by_corp":    _safe(lambda: db.card_bin_by_corp(60), []),
        "cards_by_corp":       _safe(lambda: db.card_pool_by_corp(), []),
        "txns_by_corp":        _safe(lambda: db.transactions_by_corp(), []),
        "emp_health":          _safe(lambda: db.employee_health(3), []),
        "read_instances":      _safe(lambda: db.read_instance_status(), []),
        "funnel":              _safe(lambda: db.conversion_funnel(_p), []),
        "stage_reasons":       _safe(lambda: db.stage_reasons(_p), {}),
        "card_econ":           _safe(lambda: db.card_economics(), {}),
        "cooldown":            _safe(lambda: db.cooldown_status(), {}),
        "trend":               _safe(lambda: db.hourly_trend(24), []),
    }

    # Per-worker resources: pull live host stats from each node's /api/status. Include
    # instance_offset + max_instances so the Infra page can map each instance id to its
    # server (drill-down) by the range [offset, offset+max).
    def _recheck_slots(n):
        try:
            return sorted(int(s) for s, v in (n.get("slots") or {}).items()
                          if (v or {}).get("script") == "recheck" and (v or {}).get("status") == "running")
        except Exception:
            return []
    try:
        worker_nodes = fetch_all_status()
        workers = [{"name": n.get("name", "?"), "online": bool(n.get("online")),
                    "host": n.get("host", {}) or {},
                    "summary": n.get("summary", {}) or {},
                    "max_instances": n.get("max_instances", 0),
                    "instance_offset": n.get("instance_offset", 0),
                    "recheck_slots": _recheck_slots(n)}
                   for n in worker_nodes]
    except Exception:
        workers = []

    # ---- CONSOLIDATED ALERTS CENTER ---------------------------------------------------
    # One severity-sorted list the Home page shows so an operator sees everything that
    # needs attention in one place: OTP-dying employees, low-success employees, stuck
    # instances (>5m on a step), and offline servers.
    alerts = []
    try:
        for a in (otp_alerts or []):
            alerts.append({"sev": "critical", "kind": "OTP",
                           "title": f"Emp {a.get('emp_id')}: OTP failed {a.get('consecutive_failures')}× in a row",
                           "detail": f"{a.get('total_failures')} total · last {a.get('last_failure','')}"})
        for e in (analytics.get("emp_health") or []):
            if e.get("flag") == "dying":
                alerts.append({"sev": "critical", "kind": "EMP",
                               "title": f"Emp {e.get('emp_id')} dying: {e.get('rate')}% success",
                               "detail": f"{e.get('otp_fails',0)} OTP fails · {e.get('declined',0)} declined · {e.get('pending',0)} pending"})
        for i in (instances or []):
            if i.get("active") and (i.get("step_secs") or 0) >= 300:
                _m = (i.get("step_secs") or 0) // 60
                alerts.append({"sev": "warn", "kind": "STUCK",
                               "title": f"Instance {i.get('id')} stuck {int(_m)}m at {i.get('current_step','?')}",
                               "detail": f"emp {i.get('current_emp','—')} · {(i.get('current_task','') or '')[:40]}"})
        for w in workers:
            if not w.get("online"):
                alerts.append({"sev": "critical", "kind": "SERVER",
                               "title": f"Server {w.get('name')} OFFLINE",
                               "detail": "agent unreachable"})
        _sevrank = {"critical": 0, "warn": 1, "info": 2}
        alerts.sort(key=lambda x: _sevrank.get(x["sev"], 3))
    except Exception:
        alerts = []

    try:
        paused_state = db.system_state()
    except Exception:
        paused_state = {"paused": False, "note": None, "updated_at": None}

    return {
        "stats": stats, "instances": instances, "recent": recent, "emp_rows": emp_rows,
        "otp_alerts": otp_alerts, "reader": reader,
        "analytics": analytics, "workers": workers, "alerts": alerts,
        "system": paused_state,
        "server": _monitor_server_stats(active),
        "db_error": db_error,
        "now": now_ist().strftime("%Y-%m-%d %H:%M:%S"),
    }


@app.route("/api/monitor")
@login_required
def api_monitor():
    """Live DB-backed monitoring snapshot for the dashboard Analytics view.
    ?period=all|today|yesterday|1h|6h|24h|7d|30d filters the failure/funnel panels."""
    try:
        _ALLOWED = {"all","today","yesterday","1h","6h","24h","7d","30d"}
        _raw = (request.args.get("period") or request.args.get("win") or "all").strip()
        _p = _raw.lower()
        if _p.startswith("custom|"):
            _p = _raw                       # keep original case; db._win_clause validates it
        elif _p not in _ALLOWED:
            # back-compat: ?win=1|6 (numbers) -> 1h/6h
            _p = {"1":"1h","6":"6h","24":"24h"}.get(_p, "all")
        return jsonify(_monitor_gather(_p))
    except Exception as e:
        return jsonify({"db_error": str(e)[:160], "stats": {}, "instances": [],
                        "recent": [], "emp_rows": [], "otp_alerts": [],
                        "reader": {}, "server": {}, "analytics": {}, "alerts": [],
                        "system": {}, "workers": [],
                        "now": now_ist().strftime("%Y-%m-%d %H:%M:%S")}), 200


@app.route("/api/system/pause", methods=["GET", "POST"])
@login_required
def api_system_pause():
    """Global PAUSE/RESUME kill-switch. GET returns the current state. POST body
    {paused: true|false}. Every bot polls db.is_paused() before claiming, so this
    gracefully halts the whole fleet (current tasks finish, no new ones start) and
    resumes — no browsers killed, no orphaned rows."""
    import db
    if request.method == "GET":
        try:
            return jsonify(db.system_state())
        except Exception:
            return jsonify({"paused": False, "note": None, "updated_at": None})
    body = request.get_json(silent=True) or {}
    paused = bool(body.get("paused"))
    note = (body.get("note") or (f"paused via dashboard by {session.get('user','?')}"
                                 if paused else None))
    ok = db.set_paused(paused, note)
    if not ok:
        return jsonify({"ok": False, "msg": "DB write failed"}), 500
    return jsonify({"ok": True, "paused": paused})


@app.route("/api/system/reader_sync", methods=["POST"])
@login_required
def api_system_reader_sync():
    """STOP/START the reader (readfile) sheet↔DB sync. body {paused: true|false}.
    When stopped, the reader promoter pauses, so read_tasks is NOT
    re-filled from the sheet — use this before switching the reader sheet or clearing
    read_tasks (otherwise the daemon re-imports the old rows within seconds). The buyer
    Tasks sync is unaffected."""
    import db
    body = request.get_json(silent=True) or {}
    paused = bool(body.get("paused"))
    note = (f"reader sync stopped via dashboard by {session.get('user','?')}"
            if paused else f"reader sync resumed by {session.get('user','?')}")
    ok = db.set_reader_sync_paused(paused, note)
    if not ok:
        return jsonify({"ok": False, "msg": "DB write failed"}), 500
    return jsonify({"ok": True, "paused": paused})


def _hcol(hdr, name):
    try:
        return hdr.index(name)
    except ValueError:
        return -1


@app.route("/screen/<int:i>/<int:slot>")
@login_required
def screen(i, slot):
    node = _node(i)
    if not node:
        return Response("unknown node", status=404)
    ok, data = agent_call(node, f"/api/screen/{slot}")
    if ok and isinstance(data, (bytes, bytearray)):
        return Response(data, mimetype="image/png", headers={"Cache-Control": "no-store"})
    return Response("display not available", status=503)


# ====================== ROUTES: pages ====================================
@app.route("/")
@login_required
def home():
    return render_template("dashboard.html", user=DASHBOARD_USER)


@app.route("/settings")
@login_required
def settings_page():
    return render_template("settings.html", title="Settings", active="settings")


# ====================== campaign / cards / identities / review ======================
# Phase 5 pages, all on templates/_layout.html — one design system (REVAMP_PLAN §7).

@app.route("/campaign")
@login_required
def campaign_page():
    return render_template("campaign.html", title="Campaign", active="campaign")


@app.route("/cards")
@login_required
def cards_page():
    return render_template("cards.html", title="Card Pool", active="cards")


@app.route("/identities")
@login_required
def identities_page():
    return render_template("identities.html", title="Identities", active="identities")


@app.route("/review")
@login_required
def review_page():
    return render_template("review.html", title="Needs Review", active="review")


@app.route("/artifacts")
@login_required
def artifacts_page():
    return render_template("artifacts.html", title="Screenshots & Logs", active="artifacts")


@app.route("/records")
@login_required
def records_page():
    return render_template("records.html", title="Records", active="records")


# ---- workflow sections (client-facing 5-step layout) --------------------------
@app.route("/card-generation")
@login_required
def card_generation_page():
    return render_template("card_generation.html", title="Card Generation", active="cardgen")


@app.route("/otp")
@login_required
def otp_page():
    """Mobile OTP console: every running card-generation slot in one place — watch
    its screen and hand it the portal OTP (autofills into the bot). Add to phone
    home screen for an app-like OTP entry point."""
    return render_template("otp.html", title="Card OTP", active="otp")


@app.route("/source")
@login_required
def source_page():
    return render_template("source.html", title="Source", active="source")


@app.route("/nykaa")
@login_required
def nykaa_page():
    return render_template("nykaa.html", title="Nykaa", active="nykaa")


# Telegram OTP provider removed per request — no /telegram page or /api/telegram/* routes.


@app.route("/data-entry")
@login_required
def data_entry_page():
    return render_template("data_entry.html", title="Data Entry", active="dataentry")


@app.route("/subscription")
@login_required
def subscription_page():
    return render_template("subscription.html", title="Subscription", active="subscription")


@app.route("/read")
@login_required
def read_page():
    return render_template("read_report.html", title="Read", active="read")


@app.route("/final-report")
@login_required
def final_report_page():
    return render_template("final_report.html", title="Final report", active="final")


@app.route("/servers")
@login_required
def servers_page():
    return render_template("servers.html", title="Servers", active="servers")


@app.route("/corporates")
@login_required
def corporates_page():
    return render_template("corporates.html", title="Corporates", active="corporates")


@app.route("/control")
@login_required
def control_page():
    return render_template("control.html", title="Control", active="control")


# NOTE: the standalone /analytics page was removed by request — analysis now lives
# embedded in the dashboard and each process page, not on a separate page. The
# /api/analytics/* data endpoints below stay: the dashboard charts consume them.


@app.route("/api/analytics/daily")
@login_required
def api_analytics_daily():
    import db
    try:
        days = request.args.get("days", default=30, type=int)
        return jsonify({"rows": db.analytics_daily(days)})
    except Exception as e:
        print(f"[error] {request.path}: {e}", flush=True)
        return jsonify({"error": str(e), "rows": []}), 500


# ---- Google Sheet sync (ONE-WAY: DB -> Sheet, manual) ------------------------
_SHEET_TABS = {"final": "Final Report", "transactions": "Transactions",
               "reads": "Reads", "cards": "0000000000000000"}


def _sheet_dataset(kind, campaign_id):
    """Build one sheet tab as (title, [header...], [[row strings]...]) from the DB."""
    import db
    def s(v):
        return "" if v is None else str(v)
    if kind == "transactions":
        rows = db.list_transactions(campaign_id=campaign_id, limit=50000)
        hdr = ["ID", "Status", "Card", "Name", "Email", "Emp", "Txn ID", "Duration(s)", "When", "Error"]
        data = [[s(r.get("id")), s(r.get("status")), s(r.get("card_masked")), s(r.get("name")),
                 s(r.get("email")), s(r.get("emp_id")), s(r.get("transaction_id")), s(r.get("duration_sec")),
                 s(r.get("updated_at")), s(r.get("error"))] for r in rows]
        return _SHEET_TABS[kind], hdr, data
    if kind == "reads":
        rows = db.list_reads(campaign_id=campaign_id, limit=50000)
        hdr = ["Email", "Password", "Name", "Books", "Txn ID", "Bought", "Read", "Status"]
        data = [[s(r.get("email")), s(r.get("password")), s(r.get("name_used")), s(r.get("books_read")),
                 s(r.get("transaction_id")), s(r.get("transaction_at")), s(r.get("read_at")), s(r.get("status"))] for r in rows]
        return _SHEET_TABS[kind], hdr, data
    if kind == "cards":
        rows = db.list_cards(campaign_id=campaign_id, limit=50000)
        hdr = ["Card number", "CVV", "Expiry", "Status", "Max", "Tries", "Generated", "Error"]
        data = [[s(r.get("card_no")), s(r.get("cvv")), s(r.get("expiry")), s(r.get("status")),
                 s(r.get("max_amount")), s(r.get("attempts")), s(r.get("generated_at")), s(r.get("error"))] for r in rows]
        return _SHEET_TABS[kind], hdr, data
    if kind == "final":
        txns = db.list_transactions(campaign_id=campaign_id, limit=50000)
        reads = db.list_reads(campaign_id=campaign_id, limit=50000)
        read_by = {}
        for rd in reads:
            st = rd.get("source_task_id")
            if st is not None:
                read_by[st] = rd
        hdr = ["ID", "Account", "Name", "Emp", "Card", "Subscription", "Txn ID", "Bought",
               "Books", "Read", "Read at", "Password"]
        data = []
        def _real_txn(v):
            v = ("" if v is None else str(v)).strip()
            return "" if (not v or v.upper() == "NOT_FOUND") else v
        for t in txns:
            rd = read_by.get(t.get("id"), {})
            # Txn ID: buyer's own if captured, else the reader-scraped one (the confirmation).
            txn = _real_txn(t.get("transaction_id")) or _real_txn(rd.get("transaction_id"))
            data.append([s(t.get("id")), s(t.get("email")), s(t.get("name")), s(t.get("emp_id")),
                         s(t.get("card_masked")), s(t.get("status")), txn,
                         s(t.get("updated_at")), s(rd.get("books_read")), s(rd.get("status")),
                         s(rd.get("read_at")), s(rd.get("password"))])
        return _SHEET_TABS[kind], hdr, data
    raise ValueError("unknown tab: " + str(kind))


@app.route("/api/sheet/sync", methods=["POST"])
@login_required
def api_sheet_sync():
    body = request.get_json(silent=True) or {}
    try:
        cid = int(body.get("campaign_id"))
    except (TypeError, ValueError):
        return jsonify({"error": "pick a campaign first"}), 400
    tabs = [t for t in (body.get("tabs") or list(_SHEET_TABS)) if t in _SHEET_TABS]
    cfg = _read_json_file(MASTER_CONFIG, {})
    sid = (cfg.get("GOOGLE_SHEET_ID") or "").strip()
    creds = cfg.get("GOOGLE_CREDENTIALS")
    if not sid or not creds:
        return jsonify({"error": "Set GOOGLE_SHEET_ID and GOOGLE_CREDENTIALS in Settings first."}), 400
    try:
        import gspread
    except ImportError:
        return jsonify({"error": "gspread is not installed on the server — run: ./venv/bin/pip install gspread"}), 500
    try:
        if isinstance(creds, str):
            creds = json.loads(creds)
        gc = gspread.service_account_from_dict(creds)
        sh = gc.open_by_key(sid)
        synced = {}
        for kind in tabs:
            title, hdr, data = _sheet_dataset(kind, cid)
            try:
                ws = sh.worksheet(title)
            except gspread.WorksheetNotFound:
                ws = sh.add_worksheet(title=title, rows=max(2, len(data) + 10), cols=max(2, len(hdr)))
            ws.clear()
            ws.update(range_name="A1", values=[hdr] + data, value_input_option="RAW")
            synced[title] = len(data)
        total = sum(synced.values())
        return jsonify({"ok": True, "synced": synced,
                        "msg": f"Synced {total:,} rows → " + ", ".join(f"{k} ({v:,})" for k, v in synced.items())})
    except Exception as e:
        print(f"[error] {request.path}: {e}", flush=True)
        return jsonify({"error": f"sync failed: {e}"}), 500


@app.route("/api/cards/request", methods=["POST"])
@login_required
def api_cards_request():
    """Buy N cards for the active campaign (queues them for generation)."""
    import db
    body = request.get_json(silent=True) or {}
    try:
        n = int(body.get("n", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "n must be a number"}), 400
    if n <= 0 or n > 100000:
        return jsonify({"error": "enter a count between 1 and 100000"}), 400
    try:
        cid = body.get("campaign_id")
        corp = body.get("corp_id") or None
        made = db.request_cards(n, campaign_id=cid, corp_id=corp)
        tag = f" for {corp}" if corp else ""
        return jsonify({"ok": True, "requested": made, "message": f"Queued {made} card(s){tag} for generation"})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except psycopg2.Error as e:
        print(f"[db-reject] {request.path}: {e}", flush=True)
        return jsonify({"error": "invalid request"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def _cards_from_upload_rows(rows):
    """Turn raw uploaded rows (from _parse_upload_raw) into (card_no, expiry, cvv, max)
    tuples. Robust to layout: positional (card, expiry, cvv, max, …) when col0 is a card
    number, else scans the row (handles a leading Session-ID column). Header rows and
    non-card rows fall out because no 15–16 digit card number is found."""
    import re
    out = []
    for r in rows:
        cells = [("" if c is None else str(c)).strip() for c in r]
        if not cells:
            continue
        c0 = re.sub(r"\D", "", cells[0])
        if len(c0) in (15, 16):                       # positional: card, expiry, cvv, max
            card = c0
            expiry = cells[1] if len(cells) > 1 else ""
            cvv = re.sub(r"\D", "", cells[2]) if len(cells) > 2 else ""
            mx = cells[3] if len(cells) > 3 else ""
        else:                                         # scan (e.g. Session-ID in col0)
            card = expiry = cvv = mx = ""
            for c in cells:
                d = re.sub(r"\D", "", c)
                if not card and len(d) in (15, 16):
                    card = d
                elif not expiry and re.fullmatch(r"\d{1,2}/\d{2,4}", c):
                    expiry = c
                elif not cvv and re.fullmatch(r"\d{3,4}", c) and "." not in c:
                    cvv = d
                elif not mx and ("." in c or (d.isdigit() and 3 <= len(d) < 15)):
                    mx = c
        if len(card) in (15, 16):
            out.append((card, expiry, cvv, mx))
    return out


@app.route("/api/cards/import", methods=["POST"])
@login_required
def api_cards_import():
    """Import already-made real cards from a .csv/.xlsx straight into the pool (no portal
    generation). Fills the chosen corporate's pending 'requested' slots first, then adds any
    surplus as fresh 'unused' cards. Dedups on card number. Multipart: file + corp_id."""
    import db
    try:
        if "file" not in request.files:
            return jsonify({"error": "no file uploaded"}), 400
        corp = (request.form.get("corp_id") or "").strip() or None
        rows = _parse_upload_raw(request.files["file"])
        cards = _cards_from_upload_rows(rows)
        if not cards:
            return jsonify({"error": "no card numbers found in the file (need a 15–16 digit "
                                     "card number per row, plus expiry / cvv / max)"}), 400
        res = db.import_cards(cards, corp_id=corp)
        tag = f" for {corp}" if corp else ""
        msg = (f"Imported{tag}: filled {res['filled']} requested slot(s), "
               f"added {res['inserted']} new, skipped {res['skipped']} (dupes/invalid).")
        if res.get("slots_left"):
            msg += f" {res['slots_left']} requested slot(s) still empty."
        return jsonify({"ok": True, "message": msg, **res})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except UploadError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"[error] {request.path}: {e}", flush=True)
        return jsonify({"error": str(e)}), 500


@app.route("/api/cards/target", methods=["POST"])
@login_required
def api_cards_target():
    """"Make only N now" — set the OUTSTANDING card requests to exactly n (cancels the
    surplus 'requested', keeps anything already generating/made). Body {n, campaign_id?}."""
    import db
    body = request.get_json(silent=True) or {}
    try:
        n = int(body.get("n", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "n must be a number"}), 400
    if n < 0 or n > 100000:
        return jsonify({"error": "enter a count between 0 and 100000"}), 400
    try:
        out = db.set_card_target(n, campaign_id=body.get("campaign_id"))
        return jsonify({"ok": True, "outstanding": out, "message": f"Outstanding card requests set to {out}"})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except psycopg2.Error as e:
        print(f"[db-reject] {request.path}: {e}", flush=True)
        return jsonify({"error": "invalid request"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/campaign/<int:cid>/today_target", methods=["POST"])
@login_required
def api_campaign_today_target(cid):
    """Quick "only N today" control (Subscription page): set TODAY's transaction target
    for a campaign. The buyer auto-pauses once today's target is reached. Body {planned}."""
    import db
    body = request.get_json(silent=True) or {}
    try:
        planned = int(body.get("planned"))
    except (TypeError, ValueError):
        return jsonify({"error": "planned must be a number"}), 400
    try:
        db.set_today_target(cid, planned)
        return jsonify({"ok": True, "message": f"Today's target set to {planned:,}"})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except psycopg2.Error as e:
        print(f"[db-reject] {request.path}: {e}", flush=True)
        return jsonify({"error": "invalid request (rejected by the database)"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/campaign/<int:cid>/daily")
@login_required
def api_campaign_daily(cid):
    """Per-day transaction + read totals for one campaign (Subscription/Read reports)."""
    df, dt, err = _date_range_args()
    if err:
        return jsonify({"error": err, "rows": []}), 400
    try:
        import db
        return jsonify({"rows": db.campaign_daily(cid, date_from=df, date_to=dt)})
    except psycopg2.Error as e:
        print(f"[db-reject] {request.path}: {e}", flush=True)
        return jsonify({"error": "invalid request", "rows": []}), 400
    except Exception as e:
        return jsonify({"error": str(e), "rows": []}), 500


# Records browser: one endpoint per row-level datatable, all campaign-scopable.
# transactions/reads also accept an emp_id filter (used by the By-Campaign view).
_RECORDS = {
    "emails": ("list_emails", False),
    "cards": ("list_cards", False),
    "transactions": ("list_transactions", True),
    "reads": ("list_reads", True),
    "identities": ("list_identities", False),
}


@app.route("/api/records/campaigns")
@login_required
def api_records_campaigns():
    """Top level of the By-Campaign drill-down: campaigns + their aggregates."""
    try:
        import db
        return jsonify({"campaigns": db.campaign_records_summary()})
    except Exception as e:
        return jsonify({"error": str(e), "campaigns": []}), 500


@app.route("/api/records/campaign/<int:cid>/employees")
@login_required
def api_records_employees(cid):
    """Middle level: per-employee breakdown inside one campaign."""
    try:
        import db
        return jsonify({"rows": db.campaign_employee_breakdown(cid)})
    except psycopg2.Error as e:
        print(f"[db-reject] {request.path}: {e}", flush=True)
        return jsonify({"error": "invalid request", "rows": []}), 400
    except Exception as e:
        return jsonify({"error": str(e), "rows": []}), 500


_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _date_range_args():
    """Read & validate ?date_from=&date_to= (YYYY-MM-DD). Returns (df, dt, err)."""
    df = request.args.get("date_from") or None
    dt = request.args.get("date_to") or None
    for v in (df, dt):
        if v and not _DATE_RE.match(v):
            return None, None, "bad date (use YYYY-MM-DD)"
    return df, dt, None


@app.route("/api/records/campaign/<int:cid>/employee/<emp>/daily")
@login_required
def api_records_employee_daily(cid, emp):
    """Leaf level: per-day transaction + read totals for one employee. ?date_from=&date_to="""
    df, dt, err = _date_range_args()
    if err:
        return jsonify({"error": err, "rows": []}), 400
    try:
        import db
        return jsonify({"rows": db.campaign_employee_daily(cid, emp, date_from=df, date_to=dt)})
    except psycopg2.Error as e:
        print(f"[db-reject] {request.path}: {e}", flush=True)
        return jsonify({"error": "invalid request", "rows": []}), 400
    except Exception as e:
        return jsonify({"error": str(e), "rows": []}), 500


@app.route("/api/records/<kind>")
@login_required
def api_records(kind):
    """Row-level records for the /records datatables. ?campaign_id=&emp_id=&limit="""
    if kind not in _RECORDS:
        return jsonify({"error": "unknown record type", "rows": []}), 404
    import db
    fn_name, supports_emp = _RECORDS[kind]
    fn = getattr(db, fn_name)
    cid = request.args.get("campaign_id", type=int)
    emp = request.args.get("emp_id")
    df, dt, err = _date_range_args()
    if err:
        return jsonify({"error": err, "rows": []}), 400
    status = request.args.get("status") or None
    try:
        limit = min(max(request.args.get("limit", default=1000, type=int), 1), 5000)
    except (TypeError, ValueError):
        limit = 1000
    kw = dict(campaign_id=cid, limit=limit, date_from=df, date_to=dt, status=status)
    if supports_emp:
        kw["emp_id"] = emp
    try:
        rows = fn(**kw)
        # When we return exactly `limit` rows there are probably more behind them —
        # tell the UI so it can say "latest N" instead of implying this is everything.
        return jsonify({"rows": rows, "count": len(rows),
                        "capped": len(rows) >= limit, "limit": limit})
    except psycopg2.Error as e:
        print(f"[db-reject] {request.path}: {e}", flush=True)
        return jsonify({"error": "invalid request (rejected by the database)", "rows": []}), 400
    except Exception as e:
        return jsonify({"error": str(e), "rows": []}), 500


@app.route("/api/screenshots")
@login_required
def api_screenshots():
    """Categorised screenshots (local controller box + every node). ?category=&q=&kind="""
    shots = [dict(s, source="local") for s in _list_local_shots()]
    for n in NODES:                              # pull each node's list too (multi-server)
        ok, data = agent_call(n, "/api/screenshots")
        if ok and isinstance(data, dict):
            for s in data.get("shots", []):
                shots.append(dict(s, source=n["name"]))
    cat = (request.args.get("category") or "").strip()
    q = (request.args.get("q") or "").strip().lower()
    kind = (request.args.get("kind") or "").strip()
    if cat:
        shots = [s for s in shots if s["category"] == cat]
    if kind:
        shots = [s for s in shots if s.get("kind") == kind]
    if q:
        shots = [s for s in shots if q in s["email"].lower()]
    shots.sort(key=lambda x: x.get("mtime", 0), reverse=True)
    # category counts (before the q/kind filter would be ideal, but keep it simple)
    cats = {}
    for s in ([dict(x) for x in _list_local_shots()]):
        cats[s["category"]] = cats.get(s["category"], 0) + 1
    return jsonify({"shots": shots[:500], "total": len(shots), "categories": cats})


@app.route("/api/screenshots/file")
@login_required
def api_screenshot_file():
    """Serve one screenshot. ?rel=<relpath>[&source=<node name>]"""
    rel = request.args.get("rel", "")
    source = request.args.get("source", "local")
    # Local-first: if the file is on THIS host (controller / main-run reader), serve it —
    # this covers a proof whose proof_node isn't a registered worker (e.g. main). Only when
    # it's not local do we proxy to the named node's agent.
    full = _safe_rel(rel)
    if full and os.path.isfile(full):
        with open(full, "rb") as fh:
            return Response(fh.read(), mimetype="image/png", headers={"Cache-Control": "no-store"})
    if source and source != "local":
        node = next((n for n in NODES if n["name"] == source), None)
        if node:
            ok, data = agent_call(node, f"/api/screenshots/file?rel={rel}")
            if ok and isinstance(data, (bytes, bytearray)):
                return Response(data, mimetype="image/png", headers={"Cache-Control": "no-store"})
    return Response("not found", status=404)


@app.route("/api/screenshots/clean", methods=["POST"])
@login_required
def api_screenshots_clean():
    """Delete screenshots. Body: {category?, all?} — local + broadcast to nodes."""
    body = request.get_json(silent=True) or {}
    cat = (body.get("category") or "").strip()
    do_all = bool(body.get("all"))
    removed = 0
    for s in _list_local_shots():
        if do_all or (cat and s["category"] == cat):
            full = _safe_rel(s["rel"])
            if full and os.path.isfile(full):
                try:
                    os.remove(full); removed += 1
                except OSError:
                    pass
    node_removed = 0
    for n in NODES:
        ok, data = agent_call(n, "/api/screenshots/clean", "POST",
                              {"category": cat, "all": do_all})
        if ok and isinstance(data, dict):
            node_removed += int(data.get("removed", 0))
    return jsonify({"ok": True, "removed": removed + node_removed,
                    "message": f"cleaned {removed + node_removed} screenshot(s)"})


@app.route("/api/logs")
@login_required
def api_logs():
    """Bot logs. Local instance_logs/*.log + each node's slot logs. ?file=<name>&lines="""
    lines = min(2000, max(50, int(request.args.get("lines", 300) or 300)))
    fname = (request.args.get("file") or "").strip()
    # list available local log files
    local_files = []
    if os.path.isdir(LOGS_DIR):
        local_files = sorted(f for f in os.listdir(LOGS_DIR) if f.endswith(".log"))
    if not fname:
        return jsonify({"files": local_files})
    if fname not in local_files:              # whitelist — no path traversal
        return jsonify({"error": "unknown log file", "files": local_files}), 404
    path = os.path.join(LOGS_DIR, fname)
    try:
        with open(path, "r", errors="replace") as fh:
            tail = fh.readlines()[-lines:]
        return jsonify({"file": fname, "lines": lines, "text": "".join(tail) or "(empty)"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/campaign", methods=["GET"])
@login_required
def api_campaign():
    try:
        import db
        cid = request.args.get("id")
        cid = int(cid) if cid else None      # None => active campaign
        return jsonify({"campaign": db.campaign_overview(cid)})
    except (ValueError, TypeError):
        return jsonify({"error": "invalid campaign id"}), 400
    except Exception as e:
        return jsonify({"error": str(e), "campaign": None}), 500


@app.route("/api/campaigns", methods=["GET"])
@login_required
def api_campaigns():
    """All campaigns (active + past) for the history dropdown."""
    try:
        import db
        return jsonify({"campaigns": db.campaign_list()})
    except Exception as e:
        return jsonify({"error": str(e), "campaigns": []}), 500


@app.route("/api/campaign/close", methods=["POST"])
@login_required
def api_campaign_close():
    """Manually complete a campaign — it moves to history (status 'done'). Closes the
    campaign_id sent in the body, or the active one if none given."""
    try:
        import db
        body = request.get_json(silent=True) or {}
        cid = db.close_campaign(body.get("campaign_id"))
        if not cid:
            return jsonify({"error": "no active campaign to close"}), 400
        return jsonify({"ok": True, "message": "Campaign closed — moved to history"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/campaign/<int:cid>/export.csv", methods=["GET"])
@login_required
def api_campaign_export(cid):
    """Download a campaign report as CSV. ?cols=key1,key2,... (defaults to all)."""
    import csv, io, db
    if db.campaign_overview(cid) is None:      # unknown campaign -> 404, not a blank CSV
        return jsonify({"error": "no such campaign"}), 404
    cols = request.args.get("cols")
    cols = [c.strip() for c in cols.split(",")] if cols else None
    try:
        header, rows = db.export_campaign_rows(cid, "report", cols)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except psycopg2.Error as e:
        print(f"[db-reject] {request.path}: {e}", flush=True)
        return jsonify({"error": "invalid request (rejected by the database)"}), 400
    except Exception as e:
        print(f"[error] {request.path}: {e}", flush=True)
        return jsonify({"error": "server error"}), 500
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(header)
    w.writerows(rows)
    fname = f"campaign_{cid}_report.csv"
    return Response(buf.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": f'attachment; filename="{fname}"'})


@app.route("/api/campaign/export_columns")
@login_required
def api_campaign_export_columns():
    """Column metadata (key + label + group) so the picker can group the checkboxes."""
    import db
    return jsonify({"columns": db.EXPORT_COLUMN_META})


@app.route("/api/campaign", methods=["POST"])
@login_required
def api_campaign_create():
    try:
        import db
        d = request.get_json(force=True) or {}
        r = db.create_campaign(
            d.get("budget"), d.get("account_password"),
            buffer_days=d.get("buffer_days", 5),
            name=d.get("name") or "Campaign",
            email_alert_days=d.get("email_alert_days", 2),
            corp_id=d.get("corp_id"),
            employee_ids=d.get("employee_ids"),
            backup_employee_ids=d.get("backup_employee_ids"))
        msg = (f"Campaign set — {r['plan_days']}-day plan built. "
               f"Buy cards for it from the Cards page (per corporate).")
        if r["superseded"]:
            msg += " Previous campaign closed."
        return jsonify({"ok": True, "message": msg, **r})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except psycopg2.Error as e:
        print(f"[db-reject] {request.path}: {e}", flush=True)
        return jsonify({"error": "invalid request (rejected by the database)"}), 400
    except Exception as e:
        print(f"[error] {request.path}: {e}", flush=True)
        return jsonify({"error": "server error"}), 500


@app.route("/api/campaign/budget", methods=["POST"])
@login_required
def api_campaign_budget():
    try:
        import db
        d = request.get_json(force=True) or {}
        r = db.set_campaign_budget(d["campaign_id"], d["budget"])
        return jsonify({"ok": True, "message": f"Budget → {r['budget']:,} · pool {r['pool']}", **r})
    except (ValueError, KeyError, TypeError) as e:
        return jsonify({"error": str(e)}), 400
    except psycopg2.Error as e:
        print(f"[db-reject] {request.path}: {e}", flush=True)
        return jsonify({"error": "invalid request (rejected by the database)"}), 400
    except Exception as e:
        print(f"[error] {request.path}: {e}", flush=True)
        return jsonify({"error": "server error"}), 500


@app.route("/api/campaign/employees", methods=["POST"])
@login_required
def api_campaign_employees():
    try:
        import db
        d = request.get_json(force=True) or {}
        r = db.set_campaign_employees(
            d["campaign_id"], corp_id=d.get("corp_id"),
            employee_ids=d.get("employee_ids"),
            backup_employee_ids=d.get("backup_employee_ids"),
            account_password=d.get("account_password"))
        msg = (f"{len(r['employee_ids'])} employee(s), "
               f"{len(r['backup_employee_ids'])} backup(s)")
        if r.get("password_changed"):
            msg += " · password updated"
        return jsonify({"ok": True, "message": msg, **r})
    except (ValueError, KeyError, TypeError) as e:
        return jsonify({"error": str(e)}), 400
    except psycopg2.Error as e:
        print(f"[db-reject] {request.path}: {e}", flush=True)
        return jsonify({"error": "invalid request (rejected by the database)"}), 400
    except Exception as e:
        print(f"[error] {request.path}: {e}", flush=True)
        return jsonify({"error": "server error"}), 500


@app.route("/api/campaign/day", methods=["POST"])
@login_required
def api_campaign_day():
    try:
        import db
        d = request.get_json(force=True) or {}
        db.set_campaign_day(d["campaign_id"], d["day"], d["planned"])
        return jsonify({"ok": True})
    except (ValueError, KeyError, TypeError) as e:
        return jsonify({"error": str(e)}), 400
    except psycopg2.Error as e:
        print(f"[db-reject] {request.path}: {e}", flush=True)
        return jsonify({"error": "invalid request (rejected by the database)"}), 400
    except Exception as e:
        print(f"[error] {request.path}: {e}", flush=True)
        return jsonify({"error": "server error"}), 500


class UploadError(ValueError):
    """A caller/file problem (bad format, empty, wrong column) — maps to HTTP 400."""


def _parse_upload_raw(file_storage):
    """Read a .csv/.xlsx into a list of rows (each a list of stripped strings),
    dropping fully-empty rows. Raises UploadError on an unreadable/empty file."""
    name = (file_storage.filename or "").lower()
    try:
        if name.endswith(".xlsx"):
            import openpyxl
            wb = openpyxl.load_workbook(file_storage, read_only=True, data_only=True)
            try:
                ws = wb.active
                rows = [[("" if c is None else str(c)).strip() for c in row]
                        for row in ws.iter_rows(values_only=True)]
            finally:
                wb.close()          # read_only keeps the zip handle open until closed
        else:
            import csv, io
            text = file_storage.read().decode("utf-8-sig", errors="replace")
            rows = [[c.strip() for c in r] for r in csv.reader(io.StringIO(text))]
    except Exception as e:
        raise UploadError(f"could not read the file — is it a valid .csv or .xlsx? ({e})")
    rows = [r for r in rows if any(r)]
    if not rows:
        raise UploadError("the file is empty")
    return rows


def _parse_upload(file_storage, want):
    """Parse an uploaded .csv or .xlsx into rows of the requested columns.

    want='emails'  -> [email, ...]           (finds the email column by header, else
                                              scans EVERY column for an @-bearing cell)
    want='names'   -> ([first...], [last...]) (auto-detects First/Last columns)

    Raises UploadError (-> HTTP 400) on an unreadable/corrupt/empty file rather than
    letting an openpyxl/csv exception surface as a 500 with internal text.
    """
    rows = _parse_upload_raw(file_storage)
    header = [h.lower() for h in rows[0]]

    def col(*names):
        for i, h in enumerate(header):
            if h in names:
                return i
        return None

    if want == "emails":
        ci = col("email", "e-mail", "emails", "email_address")
        if ci is not None:
            body = rows[1:]
            return [r[ci] for r in body if ci < len(r) and "@" in r[ci]]
        # No email header: scan EVERY cell of EVERY row for an @ so emails in an
        # unexpected column aren't silently dropped. Include row 0 (no header).
        found = []
        for r in rows:
            for cell in r:
                if "@" in cell:
                    found.append(cell)
                    break
        return found

    fi = col("first_name", "first name", "first", "firstname")
    li = col("last_name", "last name", "last", "lastname")
    has_header = fi is not None or li is not None
    if has_header:
        # A single-column file headed ONLY "last_name" must load as last names, not
        # first — so don't default the missing side onto the present side's column.
        pass
    else:
        fi, li = 0, (1 if len(header) > 1 else 0)
    body = rows[1:] if has_header else rows
    firsts = ([r[fi] for r in body if fi is not None and fi < len(r) and r[fi]]
              if fi is not None else [])
    lasts = ([r[li] for r in body if li is not None and li < len(r) and r[li]]
             if li is not None and li != fi else [])
    if not firsts and not lasts:
        raise UploadError("no names found — expected First_Name / Last_Name columns")
    return firsts, lasts


@app.route("/api/campaign/upload_emails", methods=["POST"])
@login_required
def api_campaign_upload_emails():
    try:
        import db
        try:
            cid = int(request.form.get("campaign_id", ""))
        except (TypeError, ValueError):
            return jsonify({"error": "missing or invalid campaign_id"}), 400
        pw = request.form.get("password") or None
        if "file" not in request.files:
            return jsonify({"error": "no file uploaded"}), 400
        emails = _parse_upload(request.files["file"], "emails")
        if not emails:
            return jsonify({"error": "no email addresses found in the file"}), 400
        r = db.upload_emails(cid, emails, password=pw)
        return jsonify({"ok": True,
                        "message": f"{r['added']:,} added, {r['skipped']:,} already present", **r})
    except UploadError as e:
        return jsonify({"error": str(e)}), 400
    except psycopg2.Error as e:
        print(f"[db-reject] {request.path}: {e}", flush=True)
        return jsonify({"error": "invalid request (rejected by the database)"}), 400
    except Exception as e:
        print(f"[error] {request.path}: {e}", flush=True)
        return jsonify({"error": "server error"}), 500


@app.route("/api/campaign/upload_names", methods=["POST"])
@login_required
def api_campaign_upload_names():
    try:
        import db
        if "file" not in request.files:
            return jsonify({"error": "no file uploaded"}), 400
        firsts, lasts = _parse_upload(request.files["file"], "names")
        r = db.upload_names(firsts, lasts)
        return jsonify({"ok": True,
                        "message": (f"{r['first_added']:,} first + {r['last_added']:,} last added · "
                                    f"capacity now {r['capacity']:,}"), **r})
    except UploadError as e:
        return jsonify({"error": str(e)}), 400
    except psycopg2.Error as e:
        print(f"[db-reject] {request.path}: {e}", flush=True)
        return jsonify({"error": "invalid request (rejected by the database)"}), 400
    except Exception as e:
        print(f"[error] {request.path}: {e}", flush=True)
        return jsonify({"error": "server error"}), 500


@app.route("/api/campaign/generate_identities", methods=["POST"])
@login_required
def api_campaign_gen_identities():
    try:
        import db
        d = request.get_json(force=True) or {}
        r = db.generate_identities(d["campaign_id"], d.get("n", 1000))
        if r["no_emails"]:
            return jsonify({"error": "no active emails — upload an email list first"}), 400
        msg = f"{r['created']:,} identities generated"
        if r["exhausted"]:
            msg += " — name space exhausted, upload more first/last names"
        return jsonify({"ok": True, "message": msg, **r})
    except (ValueError, KeyError, TypeError) as e:
        return jsonify({"error": str(e)}), 400
    except psycopg2.Error as e:
        print(f"[db-reject] {request.path}: {e}", flush=True)
        return jsonify({"error": "invalid request (rejected by the database)"}), 400
    except Exception as e:
        print(f"[error] {request.path}: {e}", flush=True)
        return jsonify({"error": "server error"}), 500


@app.route("/api/cards")
@login_required
def api_cards():
    try:
        import db
        try:
            by_corp = db.card_pool_by_corp()
        except Exception:
            by_corp = []
        return jsonify({"pool": db.card_pool(), "by_corp": by_corp,
                        "bin_health": db.card_bin_health(15)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/identities")
@login_required
def api_identities():
    try:
        import db
        return jsonify(db.identity_pool())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/review")
@login_required
def api_review():
    try:
        import db
        return jsonify({"rows": db.needs_review(100), "count": db.needs_review_count()})
    except Exception as e:
        return jsonify({"error": str(e), "rows": [], "count": 0}), 500


@app.route("/api/review/<int:task_id>/<decision>", methods=["POST"])
@login_required
def api_review_resolve(task_id, decision):
    try:
        import db
        ok = db.resolve_review(task_id, decision)
        if not ok:
            # Someone else resolved it first — the status guard found nothing to update.
            return jsonify({"error": "already resolved by someone else"}), 409
        return jsonify({"ok": True})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except psycopg2.Error as e:
        print(f"[db-reject] {request.path}: {e}", flush=True)
        return jsonify({"error": "invalid request (rejected by the database)"}), 400
    except Exception as e:
        print(f"[error] {request.path}: {e}", flush=True)
        return jsonify({"error": "server error"}), 500


# ====================== auth pages ======================
# These were ~180 lines of inline HTML/CSS in this file implementing a SECOND design
# system ("Bot CRM" / Inter / --brand:#4f46e5) — so /login, /changepw and /empmap looked
# like a different product from every other page. They now render templates on the same
# tokens as the rest of the app (REVAMP_PLAN §7.2).
#
# Deleted with this block: CSS, HEAD, _topbar(), LEADS_HTML (dead — superseded by
# templates/leads.html but never removed), EMPMAP_HTML, CHANGEPW_HTML, _login_page(),
# _simple_page().

def _now_ist():
    return datetime.now().strftime("%d %b %Y, %H:%M")


def _login_render(nxt="/", msg=""):
    return render_template(
        "login.html",
        nxt=nxt, msg=msg, user=DASHBOARD_USER, now=_now_ist(),
        # Surfaced on the login page itself: a default password is worth flagging where
        # someone will actually see it, not only in a startup log nobody reads.
        # Warn while the session password is the generated one-time value —
        # i.e. nothing durable has been persisted to .controller_pass yet.
        default_pass_warning=_GENERATED_PASS and not os.path.exists(PASS_FILE),
    )


def _changepw_render(msg="", ok=False):
    return render_template("changepw.html", msg=msg, ok=ok, now=_now_ist())



# ====================== campaign automation (additive, opt-in) ==============
# Keeps a buffer of ready identities minted automatically so the operator never
# has to click "Generate identities": the pool is topped up from the uploaded
# name+email material on demand. Uses ONLY existing db functions; if it ever
# errors it just logs and retries — it can never block the bots.
#   AUTO_IDENTITIES=1        (default on)  — turn the topper on/off
#   AUTO_IDENTITY_BUFFER=300 (default)     — keep at least this many 'unused'
def _send_whatsapp(text):
    """Send a WhatsApp text via the Meta Cloud API. No-op (returns False) unless
    WA_TOKEN + WA_PHONE_ID + WA_TO are set — so it stays dormant until you add creds.
    (Set them in the controller's .env; WA_TO can be comma-separated for several admins.)"""
    tok = os.environ.get("WA_TOKEN"); pid = os.environ.get("WA_PHONE_ID"); to = os.environ.get("WA_TO")
    if not (tok and pid and to):
        return False
    ok = False
    for num in [t.strip() for t in to.split(",") if t.strip()]:
        try:
            import urllib.request
            body = json.dumps({"messaging_product": "whatsapp", "to": num,
                               "type": "text", "text": {"body": text[:1000]}}).encode()
            req = urllib.request.Request(f"https://graph.facebook.com/v20.0/{pid}/messages",
                data=body, headers={"Authorization": "Bearer " + tok, "Content-Type": "application/json"})
            urllib.request.urlopen(req, timeout=10).read()
            ok = True
        except Exception as e:
            print(f"[whatsapp] send failed: {e}", flush=True)
    return ok


_OTP_NOTIFIED = set()   # servers we've already alerted for the current OTP wait


def _campaign_automation_loop():
    import time as _t
    import db
    buffer = int(os.environ.get("AUTO_IDENTITY_BUFFER", "300") or 300)
    while True:
        try:
            if os.environ.get("AUTO_IDENTITIES", "1") == "1":
                pool = db.identity_pool() or {}
                unused = int(pool.get("unused", 0) or 0)
                emails = int(pool.get("emails_active", 0) or 0)
                exhausted = bool(pool.get("exhausted"))
                if unused < buffer and emails > 0 and not exhausted:
                    camps = db.campaign_list() or []
                    active = [c for c in camps if str(c.get("status", "")).lower() == "active"]
                    if active:
                        r = db.generate_identities(active[0]["id"], buffer - unused) or {}
                        if r.get("created"):
                            print(f"[auto-identities] minted {r['created']} "
                                  f"(unused {unused} < buffer {buffer})", flush=True)
        except Exception as e:
            print(f"[auto-identities] {e}", flush=True)

        # ---- OTP-needed WhatsApp alert (fires once per wait, when configured) ----
        try:
            base = (os.environ.get("PUBLIC_URL", "") or "").rstrip("/")
            for w in (fetch_all_status() or []):
                name = w.get("name")
                wanted = bool(w.get("otp_wanted"))
                if wanted and name not in _OTP_NOTIFIED:
                    _OTP_NOTIFIED.add(name)
                    _send_whatsapp(f"magzter-pro: card generator on {name} needs an OTP now. "
                                   f"Enter it here: {base}/otp")
                elif not wanted and name in _OTP_NOTIFIED:
                    _OTP_NOTIFIED.discard(name)
        except Exception as e:
            print(f"[otp-alert] {e}", flush=True)

        _t.sleep(60)


def _start_background():
    """Start additive background helpers once. Guarded so double-import (or a
    reloader) never starts two loops."""
    if getattr(_start_background, "_started", False):
        return
    _start_background._started = True
    if os.environ.get("AUTO_IDENTITIES", "1") == "1":
        import threading
        threading.Thread(target=_campaign_automation_loop, daemon=True).start()
        print("[auto-identities] topper started", flush=True)


# Start under both launch styles: `python controller.py` (below) and WSGI
# (gunicorn/uwsgi import the module, so start here too — the guard prevents dupes).
_start_background()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("CONTROLLER_PORT", 5050)), debug=False)
