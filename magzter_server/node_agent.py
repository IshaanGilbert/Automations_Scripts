#!/usr/bin/env python3
"""
NODE AGENT — runs on EACH worker server. Slot-based dynamic script launcher.

The controller (controller.py) drives this over a token-protected JSON API.
Each "slot" (1..MAX_INSTANCES) is an independent Xvfb display (:99+slot) with its
own x11vnc + websockify for live view. Any of the three scripts can be assigned
to any slot, independently started/stopped/restarted.

Scripts (NOT modified by this agent):
    buyer        -> script.py              --instance <OFFSET+slot> --total-instances <GLOBAL_TOTAL>
    reader       -> read.py                --instance <slot>        --total-instances <total_of_type>

Run:  ./venv/bin/python3 node_agent.py        # port 8090
Config: agent_config.json (see agent_config.example.json)
"""

from flask import Flask, request, jsonify, Response
import subprocess, os, glob, json, time, threading, hmac, signal, shutil, re
# All timestamps/logs in IST (Asia/Calcutta), regardless of the server's clock.
os.environ["TZ"] = "Asia/Calcutta"
try: time.tzset()
except Exception: pass
from datetime import datetime
from functools import wraps

from envload import load_env
load_env()

# DB is used ONLY by the auto-scheduler to check whether there is pending work before
# it fills a slot. Import defensively: if db/psycopg2 is unavailable the agent must
# still serve its HTTP API — the scheduler then fails open (see _scheduler).
try:
    import db as _db
except Exception:
    _db = None

app = Flask(__name__)

# ---- config -------------------------------------------------------------
# Priority for every setting:  environment / .env  >  agent_config.json  >  default
DEFAULTS = {
    "NODE_NAME": "node-1",
    "AGENT_TOKEN": "CHANGE_ME_TOKEN",
    # Default BASE = the folder node_agent.py lives in (buyer.py / read.py / venv are
    # all siblings here). Deriving it from __file__ means the agent launches bots from
    # ITS OWN install dir regardless of name — so magzter-pro never falls back to the
    # old /var/www/html/magzter path. Override with BASE=... in .env only if needed.
    "BASE": os.path.dirname(os.path.abspath(__file__)),
    "MAX_INSTANCES": 4,
    "INSTANCE_OFFSET": 0,
    "GLOBAL_TOTAL": 0,
}


def _load_cfg():
    cfg = dict(DEFAULTS)
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agent_config.json")
    try:
        with open(path) as f:
            cfg.update(json.loads(f.read().strip()))
    except Exception:
        pass
    return cfg


CFG = _load_cfg()


def _get(key, cast=str):
    val = os.environ.get(key, CFG.get(key))
    return cast(val)


NODE_NAME = _get("NODE_NAME")
# Ensure spawned bots inherit NODE_NAME even when it came from agent_config.json (not the
# environment) — read.py stamps it as proof_node on a "no order id" screenshot so the
# dashboard knows which server holds the proof image.
os.environ["NODE_NAME"] = str(NODE_NAME)
AGENT_TOKEN = str(_get("AGENT_TOKEN"))
BASE = _get("BASE")
MAX_INSTANCES = _get("MAX_INSTANCES", int)
INSTANCE_OFFSET = _get("INSTANCE_OFFSET", int)
GLOBAL_TOTAL = _get("GLOBAL_TOTAL", int) or MAX_INSTANCES

if AGENT_TOKEN == DEFAULTS["AGENT_TOKEN"]:
    print("⚠️  AGENT_TOKEN is the default — set a strong AGENT_TOKEN in .env before production!", flush=True)

# ---- script registry (hardcoded) ----------------------------------------
SCRIPTS = {
    "buyer":           {"file": "buyer.py",               "uses_global_id": True},
    # HDFC variant: same flow as buyer, but handles the HDFC static-password 3DS page
    # (PIN from config HDFC_3DS_PIN) instead of OTP. ICICI buyer.py is untouched.
    "buyer_hdfc":      {"file": "buyer_hdfc.py",          "uses_global_id": True},
    "buyer_gologin":   {"file": "buyer_gologin.py",       "uses_global_id": True},
    "reader":          {"file": "read.py",                "uses_global_id": False},
    # nykaa: account creator. Same launch shape as source — parallel slots, cross-server
    # global instance ids (which also pick its Chrome debug port, so slots on one box
    # never drive each other's browser). Work-gated on the `nykaa` pool.
    "nykaa":           {"file": "nykaa.py",               "uses_global_id": True},
    # NOTE: `recheck` and `eligibility` used to be registered here. Neither script
    # exists in this repo, so starting either job failed at launch. Removed rather
    # than written — ambiguous outcomes are resolved by a human in the dashboard's
    # Needs Review queue instead (REVAMP_PLAN §6.4).
    # card_generation: one login session, finishes and exits -> run once, never >1.
    "card_generation": {"file": "card_generation.py",     "uses_global_id": False, "no_args": True,
                        "singleton": True, "run_once": True},
}

# Which DB work-pool each script draws from — the auto-scheduler consults db.scheduler_pending()
# and refuses to fill a slot whose pool is empty (no campaign / zero pending rows). The three
# buyer variants all claim from `tasks`; reader from `read_tasks`; card_generation from `cards`.
SCRIPT_WORK = {
    "buyer": "buyer", "buyer_hdfc": "buyer", "buyer_gologin": "buyer",
    "reader": "reader", "card_generation": "0000000000000000", "source": "source",
    "nykaa": "nykaa",
}

# ---- slot state ----------------------------------------------------------
def _blank_slot():
    return {"script": None, "pid": None, "status": "idle",
            "started_at": None, "global_id": None}


SLOT_STATE = {s: _blank_slot() for s in range(1, MAX_INSTANCES + 1)}
SLOT_PGID = {}                      # slot -> process-group id (for clean kills)
# ...and the same map ON DISK. THE memory leak: a bot's chrome/Xvfb children live in the
# bot's process GROUP, and killing the group is the only thing that reliably takes them
# all down. That group id was in-memory only, so after `systemctl restart` the map was
# empty and _kill_slot fell back to pkill-by-args — which kills the python and ORPHANS
# every chrome it started. Those orphans hold their RAM until the box is rebooted, which
# is how 10 slots end up eating far more memory than 10 browsers should.
PGID_FILE = f"{BASE}/slot_pgids.json"
SLOT_PROC = {}                      # slot -> Popen object (to read exit code)
SLOT_TOTAL = {}                     # slot -> total_of_type (to relaunch readers correctly)
SLOT_RESTARTS = {}                  # slot -> [recent auto-restart epochs] (crash-loop guard)
_lock = threading.RLock()

# Auto-restart a slot when its script CRASHES (non-zero exit, incl. script.py's
# os._exit(2) stuck-watchdog). Guarded against crash loops: at most
# AUTO_RESTART_MAX restarts within AUTO_RESTART_WINDOW seconds, then give up so a
# permanently-broken slot (bad creds, etc.) doesn't respawn forever.
AUTO_RESTART = True
AUTO_RESTART_WINDOW = 300
AUTO_RESTART_MAX = 5

# ---- auto-assign scheduler (per-node target mix) -------------------------
# TARGET.mode "manual" => scheduler inert (operator drives slots). "auto" => the
# scheduler keeps idle/finished slots filled up to TARGET.mix. Crash-restart stays
# in _watchdog; the scheduler only fills genuinely-free slots.
TARGET_FILE = f"{BASE}/target.json"
TARGET = {"mode": "manual", "mix": {}, "updated_at": None}
MANUAL_SLOTS = set()                # slots the operator started/stopped (scheduler skips)
SLOT_LAST_LAUNCH = {}              # slot -> epoch of last scheduler launch (relaunch cooldown)
SCHED_INTERVAL = 15
RELAUNCH_COOLDOWN = 60            # don't re-run a 'done' reader/eligibility too fast


def _load_target():
    global TARGET
    try:
        with open(TARGET_FILE) as f:
            t = json.load(f)
        TARGET = {"mode": t.get("mode", "manual"),
                  "mix": {k: int(v) for k, v in (t.get("mix") or {}).items() if k in SCRIPTS},
                  "updated_at": t.get("updated_at")}
    except Exception:
        TARGET = {"mode": "manual", "mix": {}, "updated_at": None}


# ---- auth ----------------------------------------------------------------
def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        tok = request.headers.get("X-Agent-Token", "")
        if not tok:
            auth = request.headers.get("Authorization", "")
            if auth.startswith("Bearer "):
                tok = auth[7:]
        if not hmac.compare_digest(str(tok), AGENT_TOKEN):
            return jsonify({"error": "unauthorized"}), 401
        return f(*args, **kwargs)
    return wrapper


# ---- process helpers -----------------------------------------------------
def _cpu_count():
    try:
        return os.cpu_count() or 0
    except Exception:
        return 0


def _host_stats():
    """This WORKER's live CPU/RAM/disk/uptime, so the controller dashboard can show
    per-server resources (not just the controller box). psutil if present, else /proc
    fallbacks; never raises."""
    s = {"cpu": None, "ram_used": None, "ram_total": None, "ram_pct": None,
         "disk_pct": None, "uptime": None, "cpus": _cpu_count()}
    try:
        import psutil
        s["cpu"] = round(psutil.cpu_percent(interval=0.0), 1)
        vm = psutil.virtual_memory()
        s["ram_used"] = round(vm.used / 1e9, 1)
        s["ram_total"] = round(vm.total / 1e9, 1)
        s["ram_pct"] = round(vm.percent, 1)
        s["disk_pct"] = round(psutil.disk_usage("/").percent, 1)
        up = int(time.time() - psutil.boot_time())
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
            s["ram_pct"] = round((tot - avail) / tot * 100, 1) if tot else None
        except Exception:
            pass
        try:
            la = os.getloadavg()[0]
            s["cpu"] = round(la / (os.cpu_count() or 1) * 100, 1)
        except Exception:
            pass
        try:
            st = os.statvfs("/")
            used = (st.f_blocks - st.f_bfree) / st.f_blocks * 100 if st.f_blocks else None
            s["disk_pct"] = round(used, 1) if used is not None else None
        except Exception:
            pass
    return s


def _alive(pid):
    if not pid:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True          # exists but owned by root — still alive
    return True


def _run(cmd, timeout=15):
    try:
        subprocess.run(cmd, shell=True, capture_output=True, timeout=timeout)
    except Exception:
        pass


def _atomic_write_json(path, data, secret=False):
    """Validate `data` is JSON-serializable, back up the existing file, then write
    atomically (temp + os.replace). secret=True => chmod 600 (creds/config)."""
    text = json.dumps(data, indent=2)        # raises TypeError if not serializable
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


def _read_json_file(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default


def _save_pgids():
    """Persist what each slot is running, so a restarted agent can ADOPT it.

    The unit is KillMode=process on purpose — restarting the agent must not kill a
    buyer mid-payment. But the agent used to keep the slot->pgid map in memory only, so
    after a restart it could neither track nor properly kill the survivors: the
    arg-pattern fallback killed the python and orphaned its chrome. Persisting the
    script and pgid is what lets _boot_adopt() pick the running bots back up instead.
    """
    try:
        _atomic_write_json(PGID_FILE, {
            str(slot): {"pgid": pg,
                        "script": (SLOT_STATE.get(slot) or {}).get("script"),
                        "started_at": (SLOT_STATE.get(slot) or {}).get("started_at"),
                        "global_id": (SLOT_STATE.get(slot) or {}).get("global_id"),
                        "total": SLOT_TOTAL.get(slot)}
            for slot, pg in SLOT_PGID.items()})
    except Exception as e:
        print(f"⚠️  could not save {PGID_FILE}: {e}", flush=True)


def _load_pgids():
    """slot -> {pgid, script, started_at, global_id, total}. Tolerates the older
    flat {slot: pgid} format so an upgrade in place doesn't lose the map."""
    data = _read_json_file(PGID_FILE, {}) or {}
    out = {}
    for k, v in data.items():
        try:
            slot = int(k)
        except Exception:
            continue
        if isinstance(v, dict):
            try:
                out[slot] = dict(v, pgid=int(v.get("pgid")))
            except Exception:
                continue
        else:
            try:
                out[slot] = {"pgid": int(v), "script": None,
                             "started_at": None, "global_id": None, "total": None}
            except Exception:
                continue
    return out


def _kill_slot(slot):
    """Kill the script + its Xvfb/x11vnc/websockify for THIS slot only."""
    # Say WHO asked. A display dying mid-run is always this function, but there are four
    # callers (relaunch, /slot/stop, /stop_all, boot sweep) and the logs never said which
    # — which is why a slot being torn down under a running bot took so long to pin down.
    try:
        import traceback as _tb
        _caller = [f.name for f in _tb.extract_stack()[:-1]][-1]
    except Exception:
        _caller = "?"
    print(f"🔪 _kill_slot({slot}) called by {_caller}", flush=True)

    display = 99 + slot
    vnc = 5900 + slot
    web = 6080 + slot

    # 1) script process group (covers no-arg scripts that can't be matched by args)
    pg = SLOT_PGID.pop(slot, None)
    if pg is None:
        # In-memory map is empty after an agent restart — fall back to the on-disk copy
        # so the previous run's chrome children are killed with their group instead of
        # being orphaned by the arg-pattern kills below.
        pg = (_load_pgids().get(slot) or {}).get("pgid")
    if pg:
        _run(f"sudo kill -TERM -- -{pg} 2>/dev/null")
        time.sleep(0.5)
        _run(f"sudo kill -KILL -- -{pg} 2>/dev/null")

    # 2) arg-pattern fallbacks for the slot's known script types. These matter when the
    #    process-group kill can't fire — e.g. after a node_agent restart/reboot the
    #    in-memory SLOT_PGID is empty, so an old bot from before the restart would survive
    #    and the relaunch would DOUBLE it. Match the ACTUAL buyer file names (the buyer
    #    was renamed script.py -> buyer.py; the stale "script.py" pattern matched nothing,
    #    which is exactly what caused the 24->48 duplication).
    gid = INSTANCE_OFFSET + slot
    _run(f'sudo pkill -f "script.py --instance {gid} " 2>/dev/null')
    _run(f'sudo pkill -f "buyer.py --instance {gid} " 2>/dev/null')
    _run(f'sudo pkill -f "buyer_hdfc.py --instance {gid} " 2>/dev/null')
    _run(f'sudo pkill -f "buyer_gologin.py --instance {gid} " 2>/dev/null')
    _run(f'sudo pkill -f "source.py --instance {gid} " 2>/dev/null')
    _run(f'sudo pkill -f "nykaa.py --instance {gid} " 2>/dev/null')
    _run(f'sudo pkill -f "read.py --instance {slot} " 2>/dev/null')
    # no-arg scripts: covered by the process-group kill above; arg-pattern fallback
    # would match every slot, so we rely on the pgid kill for those.

    # NOTE: there used to be a "kill everything whose environ has DISPLAY=:<display>"
    # sweep here, meant to catch chrome orphaned by a dead parent. It was removed: that
    # set includes the slot's RUNNING bot and its browser, so any call to _kill_slot —
    # including the ordinary one at the top of _launch_slot — could tear down a healthy
    # account mid-flight. magzter-v2 never had it and never had this problem. Orphaned
    # browsers are handled by the process-GROUP kill above, which is what the persisted
    # pgid exists for.

    # 3) infra for this display/ports
    _run(f'sudo pkill -f "DISPLAY=:{display} openbox" 2>/dev/null')
    _run(f'sudo pkill -f "Xvfb :{display} " 2>/dev/null')
    _run(f'sudo pkill -f "rfbport {vnc}" 2>/dev/null')
    _run(f'sudo pkill -f "localhost:{vnc}" 2>/dev/null')
    _save_pgids()


def _launch_infra(slot):
    display = 99 + slot
    vnc = 5900 + slot
    web = 6080 + slot
    # Clear any stale X lock/socket left by a previous crash — otherwise Xvfb
    # refuses to start on this display and the bot launches against a dead
    # DISPLAY, crashing the browser at 0.0s. (pkill in _kill_slot doesn't remove
    # these.)
    _run(f'sudo rm -f /tmp/.X{display}-lock /tmp/.X11-unix/X{display} 2>/dev/null')
    # Xvfb's output went to DEVNULL, so when a display died mid-run there was nothing
    # anywhere saying why — the bot just reported "browser has been closed" and the VNC
    # said "Reconnecting". Keep it: this file is the only place an X server crash, a
    # signal, or a "server already active" clash ever shows up.
    # SEPARATE files per component. Sharing one meant x11vnc's `-o` TRUNCATED the file
    # and wiped everything Xvfb had written — which is exactly the output needed to
    # explain why a display dies mid-run.
    os.makedirs(f"{BASE}/instance_logs", exist_ok=True)
    infra_log = open(f"{BASE}/instance_logs/xvfb_{slot}.log", "a")
    infra_log.write(f"\n===== {datetime.now():%Y-%m-%d %H:%M:%S} — Xvfb up for slot "
                    f"{slot} (display :{display}) =====\n")
    infra_log.flush()
    # -noreset : by default an X server RESETS when its last client disconnects, and a
    #            reset throws every remaining client off with an XIO error. On these
    #            slots the clients are chrome + x11vnc (+ openbox when installed), so a
    #            browser that exits between accounts could take the whole display with
    #            it — x11vnc logged exactly that ("caught XIO error"), the VNC view went
    #            dead, and the NEXT account's chrome launched against a display that was
    #            no longer there. Nothing was killing anything; X was doing what X does.
    # -s 0     : disable the screen-saver. X blanks an idle screen after 10 minutes, and
    #            the OTP waits leave it idle for 7-12 — which is why the VNC preview kept
    #            showing a black screen while the bot was actually fine.
    subprocess.Popen(["sudo", "Xvfb", f":{display}", "-screen", "0", "1440x900x24",
                       "-ac", "-nolisten", "tcp", "-noreset", "-s", "0"],
                      stdout=infra_log, stderr=infra_log)
    time.sleep(1)
    # A window manager on the slot's display. Without one, X has nothing to hand input
    # focus to: over VNC the browser window cannot be focused, typing goes nowhere, and
    # windows behave as if minimised. Also stops Chrome coming up as an unmanaged,
    # oddly-sized window on a bare Xvfb. Optional — if no WM is installed the slot still
    # runs, you just cannot drive it by hand.
    _run(f'command -v openbox >/dev/null 2>&1 && sudo DISPLAY=:{display} openbox '
         f'>>{BASE}/instance_logs/openbox_{slot}.log 2>&1 & ')
    time.sleep(0.5)
    # A previous x11vnc/websockify still holding this slot's port makes the new one die
    # at birth with "ListenOnTCPPort: Address already in use" -> the VNC view is simply
    # blank while the bot runs fine, which reads like a bot failure and is not one.
    # _kill_slot clears these too, but infra can be (re)launched when a stale one exists.
    _run(f'sudo pkill -f "rfbport {vnc}" 2>/dev/null')
    _run(f'sudo pkill -f "localhost:{vnc}" 2>/dev/null')
    time.sleep(0.5)
    _run(f'command -v x11vnc >/dev/null 2>&1 && sudo x11vnc -display :{display} '
         f'-forever -shared -nopw -rfbport {vnc} -noxdamage -bg '
         f'-o {BASE}/instance_logs/x11vnc_{slot}.log >/dev/null 2>&1')
    subprocess.Popen(
        f'command -v websockify >/dev/null 2>&1 && {{ NOVNC_WEB=/usr/share/novnc; '
        f'[ -d "$NOVNC_WEB" ] || NOVNC_WEB=/usr/share/webapps/novnc; '
        f'sudo websockify --web="$NOVNC_WEB" {web} localhost:{vnc} >/dev/null 2>&1; }}',
        shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _launch_slot(slot, script_key, total_of_type=None):
    if script_key not in SCRIPTS:
        raise ValueError(f"unknown script '{script_key}'")
    info = SCRIPTS[script_key]
    display = 99 + slot
    log_file = f"{BASE}/instance_logs/{script_key}_{slot}.log"

    _kill_slot(slot)
    time.sleep(1)

    os.makedirs(f"{BASE}/instance_logs", exist_ok=True)
    _launch_infra(slot)

    python = f"{BASE}/venv/bin/python3"
    script = f"{BASE}/{info['file']}"
    cmd = ["sudo", "PYTHONUNBUFFERED=1", f"DISPLAY=:{display}", python, "-u", script]

    gid = None
    if info.get("no_args"):
        pass
    elif info.get("uses_global_id"):
        gid = INSTANCE_OFFSET + slot
        cmd += ["--instance", str(gid), "--total-instances", str(GLOBAL_TOTAL)]
    else:
        cmd += ["--instance", str(slot), "--total-instances", str(total_of_type or 1)]

    # APPEND, not truncate. Opening "w" wiped the previous run's output the moment the
    # slot relaunched — so the log of a bot that had just died was gone before anyone
    # could read it, which is exactly when it is needed. Rotate at 20 MB so appending
    # cannot fill the disk; one .1 generation back is enough to cover a crash+restart.
    try:
        if os.path.exists(log_file) and os.path.getsize(log_file) > 20 * 1024 * 1024:
            os.replace(log_file, log_file + ".1")
    except Exception:
        pass
    lf = open(log_file, "a")
    lf.write(f"\n===== {datetime.now():%Y-%m-%d %H:%M:%S} — {script_key} start, slot "
             f"{slot} (display :{display}) =====\n")
    lf.flush()
    # cwd=BASE so every script's relative config.json / settings.json /
    # config/settings reads resolve against the project dir.
    proc = subprocess.Popen(cmd, stdout=lf, stderr=lf, preexec_fn=os.setsid, cwd=BASE)
    # Buyer also writes the legacy instance_<slot>.log path some tools expect.
    if script_key == "buyer":
        try:
            os.makedirs(f"{BASE}/instance_logs", exist_ok=True)
            open(f"{BASE}/instance_logs/instance_{slot}.log", "a").close()
        except Exception:
            pass

    SLOT_PGID[slot] = proc.pid          # setsid => pgid == pid
    _save_pgids()                       # survives an agent restart — see PGID_FILE
    SLOT_PROC[slot] = proc              # keep handle to read its exit code later
    SLOT_TOTAL[slot] = total_of_type    # remembered so the watchdog can relaunch it
    SLOT_STATE[slot] = {
        "script": script_key, "pid": proc.pid, "status": "running",
        "started_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "global_id": gid,
    }
    return SLOT_STATE[slot]


# ---- watchdog ------------------------------------------------------------
def _watchdog():
    while True:
        time.sleep(10)
        with _lock:
            for slot, st in SLOT_STATE.items():
                pid = st.get("pid")
                if not pid:
                    continue
                proc = SLOT_PROC.get(slot)
                # Determine if the process ended, and with what exit code.
                if proc is not None:
                    rc = proc.poll()          # None = still running
                    ended = rc is not None
                else:
                    rc = None                 # agent restarted; exit code unknown
                    ended = not _alive(pid)
                if not ended:
                    continue

                if st["status"] == "stopping":
                    SLOT_STATE[slot] = _blank_slot()        # we stopped it
                    SLOT_PROC.pop(slot, None)
                elif rc not in (None, 0):
                    # Real crash (non-zero exit, incl. script.py's os._exit(2)
                    # stuck-watchdog). Auto-restart it, guarded against crash loops.
                    SLOT_PROC.pop(slot, None)
                    script_key = st.get("script")
                    now = time.time()
                    hist = [t for t in SLOT_RESTARTS.get(slot, [])
                            if now - t < AUTO_RESTART_WINDOW]
                    if AUTO_RESTART and script_key and len(hist) < AUTO_RESTART_MAX:
                        hist.append(now)
                        SLOT_RESTARTS[slot] = hist
                        try:
                            _launch_slot(slot, script_key, SLOT_TOTAL.get(slot))
                            print(f"♻️  slot {slot} crashed (rc={rc}) — auto-restarted "
                                  f"[{len(hist)}/{AUTO_RESTART_MAX} in "
                                  f"{AUTO_RESTART_WINDOW // 60}m]", flush=True)
                        except Exception as e:
                            SLOT_STATE[slot]["status"] = "crashed"
                            SLOT_STATE[slot]["pid"] = None
                            print(f"❌ slot {slot} auto-restart failed: {e}", flush=True)
                    else:
                        st["status"] = "crashed"
                        st["pid"] = None
                        if script_key and len(hist) >= AUTO_RESTART_MAX:
                            print(f"⛔ slot {slot} crashed {len(hist)}x in "
                                  f"{AUTO_RESTART_WINDOW // 60}m — giving up; restart it "
                                  f"manually from the dashboard", flush=True)
                else:
                    # Clean exit (rc==0) — script finished its batch normally
                    # (e.g. reader: "no pending rows left"). NOT a crash.
                    st["status"] = "done"
                    st["pid"] = None
                    SLOT_PROC.pop(slot, None)


# ---- scheduler: keep slots filled to TARGET.mix (auto mode) --------------
def _scheduler_plan(pending=None):
    """Compute which free slots to fill (skips MANUAL_SLOTS). Returns a list of
    (slot, script, total). Caller must hold _lock. Crash-restart stays in the
    watchdog; this only fills genuinely-free slots up to TARGET.mix.

    `pending` is a {work_kind: claimable_count} dict from db.scheduler_pending()
    (fetched by _scheduler OUTSIDE the lock so a slow/retrying DB can't stall the
    status endpoint). WORK-AWARE: a script is only launched if its DB work-pool has
    claimable rows — so no bot runs when there is no campaign / zero pending tasks.
    `pending is None` => DB unavailable => fail open (launch as before)."""
    if TARGET.get("mode") != "auto":
        return []
    mix = TARGET.get("mix", {})

    counts = {k: 0 for k in SCRIPTS}
    free_slots = []
    now = time.time()
    for slot in range(1, MAX_INSTANCES + 1):
        if slot in MANUAL_SLOTS:
            continue
        st = SLOT_STATE[slot]
        sk, status = st.get("script"), st.get("status")
        if status == "running":
            counts[sk] = counts.get(sk, 0) + 1
        elif status == "crashed":
            counts[sk] = counts.get(sk, 0) + 1              # degraded but occupies intent
        elif status == "done" and sk and SCRIPTS.get(sk, {}).get("run_once"):
            counts[sk] = counts.get(sk, 0) + 1              # finished singleton: satisfied
        elif status == "done" and (now - SLOT_LAST_LAUNCH.get(slot, 0)) < RELAUNCH_COOLDOWN:
            counts[sk] = counts.get(sk, 0) + 1              # cooling down, don't reassign yet
        else:
            free_slots.append(slot)

    # WORK-AWARE GUARD: a script is only launchable if its DB pool has claimable rows.
    # `pending is None` (DB down) => fail open. Unknown work-kind => allow.
    def _has_work(k):
        if pending is None:
            return True
        wk = SCRIPT_WORK.get(k)
        return not (wk in pending and pending[wk] <= 0)

    if not mix:
        # STRICT PRIORITY (user rule): subscription is #1. While ANY buy work is left, EVERY
        # free slot buys — no slot sits idle, and reads do NOT start until buys are exhausted.
        # Only when there is no buy work does a free slot read; only when there are no reads
        # either does it generate cards. So the fleet is never idle while work of any kind
        # remains, and buying always comes first.
        plan = []
        cg = counts.get("card_generation", 0)
        for slot in free_slots:
            if _has_work("buyer"):
                plan.append((slot, "buyer", 1))
            elif "reader" in SCRIPTS and _has_work("reader"):
                plan.append((slot, "reader", 1))
            elif "card_generation" in SCRIPTS and _has_work("card_generation") and cg == 0:
                plan.append((slot, "card_generation", 1)); cg = 1
            else:
                break
        return plan

    # PRIORITY (user rule): purchase is #1. Fill the operator's mix targets in this order —
    # buyer variants first, then reader, then card generation — so subscription slots are
    # always allocated before anything else.
    PRIORITY = ["buyer", "buyer_hdfc", "buyer_gologin", "reader", "card_generation", "nykaa"]
    deficits = []
    for k in PRIORITY:
        want = mix.get(k, 0)
        if not want or k not in SCRIPTS or not _has_work(k):
            continue
        want = min(want, 1) if SCRIPTS[k].get("singleton") else want
        deficits += [k] * max(0, want - counts.get(k, 0))

    plan = []
    fi = 0
    for slot in free_slots:
        if fi >= len(deficits):
            break
        sk = deficits[fi]; fi += 1
        plan.append((slot, sk, mix.get(sk, 1)))

    # SPARE-CAPACITY CASCADE (user rule: "buyer first; jo slot idle bache wo auto read pe").
    # Every slot still free AFTER the buyer/mix targets are met auto-fills with the highest-
    # priority job that still has claimable work — reader, then card generation — EVEN IF it
    # is not in the operator's mix. So the fleet never sits idle while thousands of reads wait,
    # and buyer keeps its priority allocation above. Set OFF with AUTO_CASCADE=0.
    if os.environ.get("AUTO_CASCADE", "1") == "1":
        cg_placed = counts.get("card_generation", 0) + sum(1 for p in plan if p[1] == "card_generation")
        for slot in free_slots[len(plan):]:
            if "reader" in SCRIPTS and _has_work("reader"):
                pick = "reader"                                   # reader: unlimited, soak up spare
            elif "card_generation" in SCRIPTS and _has_work("card_generation") and cg_placed == 0:
                pick = "card_generation"; cg_placed = 1           # run-once singleton: at most one
            else:
                break
            plan.append((slot, pick, mix.get(pick, 1)))
    return plan


def _scheduler():
    while True:
        time.sleep(SCHED_INTERVAL)
        # Fetch claimable-work counts BEFORE taking _lock: db._conn() can retry/block for
        # up to ~30s on a DB outage, and _lock is what the non-blocking /api/status shares.
        # On any failure pending=None => scheduler falls back to work-agnostic filling.
        pending = None
        if _db is not None and TARGET.get("mode") == "auto":
            try:
                pending = _db.scheduler_pending()
            except Exception as e:
                print(f"scheduler: pending-work check failed, filling blind: {e}", flush=True)
        with _lock:
            for slot, sk, total in _scheduler_plan(pending):
                try:
                    SLOT_RESTARTS.pop(slot, None)
                    _launch_slot(slot, sk, total)
                    SLOT_LAST_LAUNCH[slot] = time.time()
                    print(f"🧭 scheduler: slot {slot} → {sk} (auto-fill)", flush=True)
                except Exception as e:
                    print(f"scheduler launch slot {slot} {sk} failed: {e}", flush=True)


# ---- log helper ----------------------------------------------------------
def _slot_logs(slot, lines=200):
    st = SLOT_STATE.get(slot, {})
    candidates = []
    if st.get("script"):
        candidates.append(f"{BASE}/instance_logs/{st['script']}_{slot}.log")
    candidates += [f"{BASE}/instance_logs/buyer_{slot}.log",
                   f"{BASE}/instance_logs/reader_{slot}.log",
                   f"{BASE}/instance_logs/instance_{slot}.log"]
    for path in candidates:
        try:
            with open(path) as f:
                return path, "\n".join(f.read().split("\n")[-lines:])
        except Exception:
            continue
    return None, ""


# ====================== API ==============================================
@app.route("/api/health")
@token_required
def health():
    return jsonify({"ok": True, "node": NODE_NAME, "cpus": _cpu_count(),
                    "max_instances": MAX_INSTANCES, "offset": INSTANCE_OFFSET,
                    "global_total": GLOBAL_TOTAL})


_STATUS_SLOTS_CACHE = {}

@app.route("/api/status")
@token_required
def status():
    # NON-BLOCKING on purpose. The launcher (_scheduler / start_all) holds _lock for many
    # seconds while it spawns Xvfb + VNC + browser for each slot. If we block on _lock
    # here, the controller's status poll (read timeout 10s) times out and flaps this
    # server "offline" every launch cycle. So take the lock only briefly; if it's busy
    # mid-launch, serve the last good snapshot — the server stays "online".
    global _STATUS_SLOTS_CACHE
    got = _lock.acquire(timeout=1.5)
    try:
        if got:
            slots = {s: dict(v) for s, v in SLOT_STATE.items()}
            _STATUS_SLOTS_CACHE = slots
        else:
            slots = _STATUS_SLOTS_CACHE or {}
    finally:
        if got:
            _lock.release()
    summary = {"running": 0, "idle": 0, "crashed": 0}
    for v in slots.values():
        summary[v["status"]] = summary.get(v["status"], 0) + 1
    # Card generation waits for the portal OTP; the bot drops card_otp_wanted.txt while
    # waiting so the dashboard / OTP app / WhatsApp can alert and collect it. Surface it
    # node-level + on the running card slot so the UI knows EXACTLY when an OTP is needed.
    try:
        otp_wanted = os.path.exists(f"{BASE}/card_otp_wanted.txt")
    except Exception:
        otp_wanted = False
    if otp_wanted:
        for v in slots.values():
            if v.get("status") == "running" and "card" in str(v.get("script") or "").lower():
                v["otp_wanted"] = True
    return jsonify({"node": NODE_NAME, "cpus": _cpu_count(),
                    "max_instances": MAX_INSTANCES, "offset": INSTANCE_OFFSET,
                    "global_total": GLOBAL_TOTAL, "slots": slots, "summary": summary,
                    "otp_wanted": otp_wanted,
                    "target": TARGET, "manual_slots": sorted(MANUAL_SLOTS),
                    "scripts": list(SCRIPTS), "host": _host_stats()})


def _valid_slot(slot):
    return 1 <= slot <= MAX_INSTANCES


@app.route("/api/slot/<int:slot>/start", methods=["POST"])
@token_required
def slot_start(slot):
    if not _valid_slot(slot):
        return jsonify({"msg": f"slot must be 1..{MAX_INSTANCES}"}), 400
    body = request.get_json(silent=True) or {}
    script_key = body.get("script")
    if script_key not in SCRIPTS:
        return jsonify({"msg": f"script must be one of {list(SCRIPTS)}"}), 400
    total = body.get("total_of_type")
    with _lock:
        SLOT_RESTARTS.pop(slot, None)        # manual start => fresh crash-loop budget
        MANUAL_SLOTS.add(slot)               # operator-pinned: scheduler won't touch it
        try:
            st = _launch_slot(slot, script_key, total)
        except Exception as e:
            return jsonify({"msg": f"launch error: {e}"}), 500
    return jsonify({"msg": f"slot {slot} → {script_key} started on {NODE_NAME}", "slot": st})


@app.route("/api/slot/<int:slot>/stop", methods=["POST"])
@token_required
def slot_stop(slot):
    if not _valid_slot(slot):
        return jsonify({"msg": f"slot must be 1..{MAX_INSTANCES}"}), 400
    with _lock:
        SLOT_STATE[slot]["status"] = "stopping"
        _kill_slot(slot)
        SLOT_STATE[slot] = _blank_slot()
        SLOT_RESTARTS.pop(slot, None)        # manual stop => clear crash-loop history
        MANUAL_SLOTS.add(slot)               # stays idle until "Return to auto" (release)
    return jsonify({"msg": f"slot {slot} stopped on {NODE_NAME}"})


@app.route("/api/slot/<int:slot>/restart", methods=["POST"])
@token_required
def slot_restart(slot):
    if not _valid_slot(slot):
        return jsonify({"msg": f"slot must be 1..{MAX_INSTANCES}"}), 400
    body = request.get_json(silent=True) or {}
    script_key = body.get("script") or SLOT_STATE[slot].get("script")
    if script_key not in SCRIPTS:
        return jsonify({"msg": "no script to restart on this slot"}), 400
    with _lock:
        SLOT_RESTARTS.pop(slot, None)        # manual restart => fresh crash-loop budget
        MANUAL_SLOTS.add(slot)               # operator-pinned
        try:
            st = _launch_slot(slot, script_key, body.get("total_of_type"))
        except Exception as e:
            return jsonify({"msg": f"launch error: {e}"}), 500
    return jsonify({"msg": f"slot {slot} restarted ({script_key}) on {NODE_NAME}", "slot": st})


@app.route("/api/slot/<int:slot>/release", methods=["POST"])
@token_required
def slot_release(slot):
    """Hand a slot back to the auto-scheduler (undo manual pin)."""
    if not _valid_slot(slot):
        return jsonify({"msg": f"slot must be 1..{MAX_INSTANCES}"}), 400
    with _lock:
        MANUAL_SLOTS.discard(slot)
    return jsonify({"msg": f"slot {slot} released to auto on {NODE_NAME}"})


@app.route("/api/target", methods=["GET"])
@token_required
def get_target():
    return jsonify(TARGET)


@app.route("/api/target", methods=["POST"])
@token_required
def set_target():
    body = request.get_json(silent=True) or {}
    mode = body.get("mode", TARGET.get("mode", "manual"))
    if mode not in ("manual", "auto"):
        return jsonify({"msg": "mode must be manual|auto"}), 400
    mix = {}
    for k, v in (body.get("mix") or {}).items():
        if k in SCRIPTS:
            try:
                mix[k] = max(0, int(v))
            except Exception:
                pass
    for k, info in SCRIPTS.items():          # cap singletons at 1
        if info.get("singleton") and mix.get(k, 0) > 1:
            mix[k] = 1
    # Only the AUTO scheduler consumes the mix, so only enforce the slot cap then.
    # Switching to MANUAL must never 400 on mix size (the scheduler goes inert and the
    # mix is irrelevant) — otherwise a mix left over from a higher MAX_INSTANCES blocks
    # the manual toggle on a node with fewer slots.
    if mode == "auto" and sum(mix.values()) > MAX_INSTANCES:
        return jsonify({"msg": f"mix total {sum(mix.values())} exceeds {MAX_INSTANCES} slots"}), 400
    with _lock:
        TARGET.update({"mode": mode, "mix": mix,
                       "updated_at": datetime.now().astimezone().isoformat(timespec="seconds")})
        try:
            _atomic_write_json(TARGET_FILE, TARGET)
        except Exception as e:
            return jsonify({"msg": f"save error: {e}"}), 500
    return jsonify({"msg": f"target set ({mode}) on {NODE_NAME}", "target": TARGET})


@app.route("/api/start_all", methods=["POST"])
@token_required
def start_all():
    body = request.get_json(silent=True) or {}
    assignments = body.get("assignments", [])
    done = []
    with _lock:
        for a in assignments:
            try:
                slot = int(a.get("slot"))
                script_key = a.get("script")
            except Exception:
                continue
            if not _valid_slot(slot) or script_key not in SCRIPTS:
                continue
            try:
                _launch_slot(slot, script_key, a.get("total_of_type"))
                done.append({"slot": slot, "script": script_key})
            except Exception:
                pass
            time.sleep(2)        # stagger launches so Xvfb/browsers don't thrash
    return jsonify({"msg": f"started {len(done)} slot(s) on {NODE_NAME}", "started": done})


@app.route("/api/stop_all", methods=["POST"])
@token_required
def stop_all():
    with _lock:
        for slot in range(1, MAX_INSTANCES + 1):
            SLOT_STATE[slot]["status"] = "stopping"
            _kill_slot(slot)
            SLOT_STATE[slot] = _blank_slot()
    return jsonify({"msg": f"all slots stopped on {NODE_NAME}"})


@app.route("/api/restart_all", methods=["POST"])
@token_required
def restart_all():
    """Relaunch every slot that currently has a script, IN PLACE — each bot re-reads
    config.json on launch (cwd=BASE), so this applies a changed config (e.g. a new
    INSTANCES_PER_EMP) without the operator touching the terminal. Idle slots skipped."""
    done = []
    with _lock:
        for slot in range(1, MAX_INSTANCES + 1):
            script_key = SLOT_STATE[slot].get("script")
            if script_key not in SCRIPTS:
                continue
            SLOT_RESTARTS.pop(slot, None)        # fresh crash-loop budget
            try:
                _launch_slot(slot, script_key, SLOT_TOTAL.get(slot))
                done.append({"slot": slot, "script": script_key})
            except Exception:
                pass
            time.sleep(2)                         # stagger so Xvfb/browsers don't thrash
    return jsonify({"msg": f"restarted {len(done)} slot(s) on {NODE_NAME}", "restarted": done})


@app.route("/api/slot/<int:slot>/logs")
@token_required
def slot_logs(slot):
    if not _valid_slot(slot):
        return jsonify({"msg": "bad slot"}), 400
    try:
        n = max(1, min(2000, int(request.args.get("lines", 200))))
    except Exception:
        n = 200
    path, text = _slot_logs(slot, n)
    return jsonify({"slot": slot, "file": path, "logs": text or "No logs yet…"})


# ---- pushed config / credentials / settings (dashboard is source of truth) ----
CONFIG_FILE_PATH      = f"{BASE}/config.json"
SETTINGS_FILE_PATH    = f"{BASE}/settings.json"
CREDENTIALS_FILE_PATH = f"{BASE}/credentials.json"


@app.route("/api/config", methods=["GET"])
@token_required
def get_config():
    return jsonify(_read_json_file(CONFIG_FILE_PATH, {}))


@app.route("/api/config", methods=["POST"])
@token_required
def set_config():
    body = request.get_json(silent=True) or {}
    cfg = body.get("config", body)
    if not isinstance(cfg, dict):
        return jsonify({"msg": "config must be a JSON object"}), 400
    try:
        _atomic_write_json(CONFIG_FILE_PATH, cfg, secret=True)
        return jsonify({"msg": f"config saved on {NODE_NAME} ({len(cfg)} keys)"})
    except Exception as e:
        return jsonify({"msg": f"save error: {e}"}), 500


@app.route("/api/credentials", methods=["GET"])
@token_required
def get_credentials():
    # NEVER return the private key — only whether it's present + the service account.
    data = _read_json_file(CREDENTIALS_FILE_PATH, {})
    return jsonify({"present": bool(data.get("private_key")),
                    "client_email": data.get("client_email", ""),
                    "project_id": data.get("project_id", "")})


@app.route("/api/credentials", methods=["POST"])
@token_required
def set_credentials():
    body = request.get_json(silent=True) or {}
    creds = body.get("credentials", body)
    if not isinstance(creds, dict):
        return jsonify({"msg": "credentials must be a JSON object"}), 400
    if creds.get("type") != "service_account" or not creds.get("private_key") \
            or not creds.get("client_email"):
        return jsonify({"msg": "not a valid service-account JSON "
                               "(need type=service_account, private_key, client_email)"}), 400
    try:
        _atomic_write_json(CREDENTIALS_FILE_PATH, creds, secret=True)
        return jsonify({"msg": f"credentials saved on {NODE_NAME} "
                               f"({creds.get('client_email')})"})
    except Exception as e:
        return jsonify({"msg": f"save error: {e}"}), 500


@app.route("/api/settings", methods=["GET"])
@token_required
def get_settings():
    return jsonify(_read_json_file(SETTINGS_FILE_PATH, {}))


@app.route("/api/settings", methods=["POST"])
@token_required
def set_settings():
    body = request.get_json(silent=True) or {}
    s = body.get("settings", body)
    if not isinstance(s, dict):
        return jsonify({"msg": "settings must be a JSON object"}), 400
    try:
        _atomic_write_json(SETTINGS_FILE_PATH, s, secret=True)
        return jsonify({"msg": f"settings saved on {NODE_NAME} ({len(s)} section(s))"})
    except Exception as e:
        return jsonify({"msg": f"save error: {e}"}), 500


@app.route("/api/card_otp", methods=["POST"])
@token_required
def set_card_otp():
    """Deliver an OTP to a running card_generation job (it polls BASE/card_otp.txt)."""
    body = request.get_json(silent=True) or {}
    otp = re.sub(r"\D", "", str(body.get("otp", "")))
    if len(otp) < 4:
        return jsonify({"msg": "otp must be 4-8 digits"}), 400
    try:
        with open(f"{BASE}/card_otp.txt", "w") as f:
            f.write(otp)
        return jsonify({"msg": f"otp delivered on {NODE_NAME}"})
    except Exception as e:
        return jsonify({"msg": f"write error: {e}"}), 500


# ── live-screen cache (CPU saver) ─────────────────────────────────────────────
# The dashboard polls one /screen per visible slot every few seconds — up to hundreds
# on one node. Each capture used to spawn an `import` (ImageMagick, PNG) subprocess:
# heavy CPU (full X grab + PNG encode + fork/exec), which starved the agent exactly when
# servers were starting (browsers already pinning the CPU) → the controller then saw
# "HTTPConnectionPool … Max retries exceeded". Fix: capture at most once per slot per TTL
# and serve every other request the cached frame; collapse concurrent polls onto ONE
# capture via a per-slot lock; and encode JPEG (far lighter than PNG). A 2s-stale live
# thumbnail is invisible to the eye but cuts screenshot CPU by ~90%.
_SCR_TTL = float(os.environ.get("SCREEN_CACHE_TTL", "2.0"))
_scr_cache = {}                        # slot -> (ts, bytes, mime)
_scr_locks = {}
_scr_locks_guard = threading.Lock()


def _scr_lock(slot):
    with _scr_locks_guard:
        lk = _scr_locks.get(slot)
        if lk is None:
            lk = _scr_locks[slot] = threading.Lock()
        return lk


def _capture_display(disp):
    # JPEG first (cheap); scrot PNG only as a fallback when ImageMagick is absent.
    for cmd, mime in ((f"DISPLAY=:{disp} import -window root -quality 60 jpg:-", "image/jpeg"),
                      (f"DISPLAY=:{disp} scrot -o -q 60 /dev/stdout 2>/dev/null", "image/png")):
        try:
            r = subprocess.run(cmd, shell=True, capture_output=True, timeout=15)
            if r.stdout and len(r.stdout) > 100:
                return r.stdout, mime
        except Exception:
            pass
    return None, None


@app.route("/api/screen/<int:slot>")
@token_required
def screen(slot):
    now = time.time()
    c = _scr_cache.get(slot)
    if c and now - c[0] < _SCR_TTL:                      # fresh enough — no capture
        return Response(c[1], mimetype=c[2], headers={"Cache-Control": "no-store"})
    lk = _scr_lock(slot)
    if lk.acquire(timeout=15):                           # one capture at a time per slot
        try:
            c = _scr_cache.get(slot)                     # re-check: another thread may have just refreshed
            if c and time.time() - c[0] < _SCR_TTL:
                return Response(c[1], mimetype=c[2], headers={"Cache-Control": "no-store"})
            data, mime = _capture_display(99 + slot)
            if data:
                _scr_cache[slot] = (time.time(), data, mime)
                return Response(data, mimetype=mime, headers={"Cache-Control": "no-store"})
        finally:
            lk.release()
    c = _scr_cache.get(slot)                             # capture failed / lock busy → serve last good frame
    if c:
        return Response(c[1], mimetype=c[2], headers={"Cache-Control": "no-store"})
    return Response("display not available", status=503)


# ---- saved screenshots (buyer/reader) — listed/served/cleaned for the dashboard ----
_SHOTS_DIR = f"{BASE}/screenshots"
_SHOT_CATS = [
    ("EMAILFILL_FAIL_", "Email fill failed"), ("EMAILDEBUG_", "Email debug"),
    ("CARD_BTN_MISSING_", "Card button missing"), ("PAYMENT_MISSING_", "Payment form missing"),
    ("CORP_SUBMIT_FAIL_", "Corporate submit failed"), ("CORP_MISSING_", "Corporate form missing"),
    ("CONFIRMDEBUG_", "Confirmation debug"), ("captcha_", "Captcha (reader)"),
]


def _shot_classify(f):
    for pref, cat in _SHOT_CATS:
        if f.startswith(pref):
            return cat, f[len(pref):].rsplit(".", 1)[0]
    return "Final / success", f.rsplit(".", 1)[0]


def _shot_safe(rel):
    full = os.path.normpath(os.path.join(_SHOTS_DIR, rel))
    base = os.path.abspath(_SHOTS_DIR)
    return full if (full == base or full.startswith(base + os.sep)) else None


@app.route("/api/screenshots")
@token_required
def agent_screenshots():
    out = []
    if os.path.isdir(_SHOTS_DIR):
        for root, _d, files in os.walk(_SHOTS_DIR):
            for f in files:
                if not f.lower().endswith((".png", ".jpg", ".jpeg")):
                    continue
                full = os.path.join(root, f)
                rel = os.path.relpath(full, _SHOTS_DIR)
                cat, email = _shot_classify(f)
                try:
                    st = os.stat(full)
                except OSError:
                    continue
                out.append({"name": f, "rel": rel, "category": cat, "email": email,
                            "kind": "reader" if "instance" in rel or cat.startswith("Captcha") else "buyer",
                            "size": st.st_size, "mtime": int(st.st_mtime)})
    out.sort(key=lambda x: x["mtime"], reverse=True)
    return jsonify({"shots": out[:500]})


@app.route("/api/screenshots/file")
@token_required
def agent_screenshot_file():
    full = _shot_safe(request.args.get("rel", ""))
    if not full or not os.path.isfile(full):
        return Response("not found", status=404)
    with open(full, "rb") as fh:
        return Response(fh.read(), mimetype="image/png", headers={"Cache-Control": "no-store"})


@app.route("/api/screenshots/clean", methods=["POST"])
@token_required
def agent_screenshots_clean():
    body = request.get_json(silent=True) or {}
    cat = (body.get("category") or "").strip()
    do_all = bool(body.get("all"))
    removed = 0
    if os.path.isdir(_SHOTS_DIR):
        for root, _d, files in os.walk(_SHOTS_DIR):
            for f in files:
                if not f.lower().endswith((".png", ".jpg", ".jpeg")):
                    continue
                fcat, _ = _shot_classify(f)
                if do_all or (cat and fcat == cat):
                    try:
                        os.remove(os.path.join(root, f)); removed += 1
                    except OSError:
                        pass
    return jsonify({"removed": removed})


def _boot_adopt():
    """Pick the previous run's bots back up instead of killing them.

    The unit is KillMode=process, so `systemctl restart magzterv3-agent` deliberately
    leaves running bots alone — a buyer must not be cut off mid-payment by a deploy.
    What was missing is that the agent forgot them: their slots read 'idle', so the
    scheduler would launch a second bot into a busy slot, and the arg-pattern kill that
    prevented that doubling killed only the python and orphaned its chrome. Those
    orphans are the RAM that never comes back.

    So: anything still alive is ADOPTED (slot marked running, pgid restored, so a later
    stop kills the whole group including chrome). Only slots whose process is actually
    gone get swept for leftovers.
    """
    saved = _load_pgids()
    adopted, swept = [], []
    for slot in range(1, MAX_INSTANCES + 1):
        info = saved.get(slot) or {}
        pg = info.get("pgid")
        script = info.get("script")
        if pg and script in SCRIPTS and _alive(pg):
            SLOT_PGID[slot] = pg
            SLOT_TOTAL[slot] = info.get("total")
            SLOT_STATE[slot] = {
                "script": script, "pid": pg, "status": "running",
                "started_at": info.get("started_at"),
                "global_id": info.get("global_id"),
            }
            # SLOT_PROC stays None: the watchdog's `proc is None` branch falls back to
            # _alive(pid), so an adopted bot is still monitored — just without an exit
            # code, which only means a crash is reported as 'crashed' not auto-restarted.
            adopted.append(f"{slot}:{script}")
        elif pg or info:
            # Its process is gone but its chrome/Xvfb may not be. This is the orphan
            # case — clean the slot so the RAM comes back before it is reused.
            try:
                _kill_slot(slot)
                swept.append(str(slot))
            except Exception as e:
                print(f"⚠️  boot sweep slot {slot}: {e}", flush=True)

    if adopted:
        print(f"♻️  adopted {len(adopted)} running slot(s) from the previous agent: "
              f"{', '.join(adopted)}", flush=True)
    if swept:
        print(f"🧹 swept {len(swept)} dead slot(s) (orphaned browsers/displays): "
              f"{', '.join(swept)}", flush=True)
    if not adopted and not swept:
        print("♻️  nothing to adopt — starting clean", flush=True)
    _save_pgids()


if __name__ == "__main__":
    _load_target()
    _boot_adopt()
    threading.Thread(target=_watchdog, daemon=True).start()
    threading.Thread(target=_scheduler, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("AGENT_PORT", 8090)), debug=False)
