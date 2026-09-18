#!/usr/bin/env python3
"""
nykaa.py — Nykaa account creator, fleet edition (no GUI).

The desktop build asked "kitne account banane hain?" in a tkinter box and every copy
did its own N. This version takes its workload from the shared DB queue instead, the
same way source.py does:

    dashboard  ->  Nykaa page: count  ->  N rows in nykaa_tasks
    every slot ->  claim one row, create one account, mark it done/failed
    queue dry  ->  claim returns None -> exit(0) -> slot goes idle

So "500 accounts" is 500 rows the whole fleet chews through together, and the Nykaa
page shows exactly how many of the 500 are finished.

Launched by node_agent.py as:
    sudo DISPLAY=:{99+slot} venv/bin/python3 -u nykaa.py \
         --instance {INSTANCE_OFFSET+slot} --total-instances {GLOBAL_TOTAL}

Standalone (one-off, no queue):
    python3 nykaa.py --count 5

EXIT CODES MATTER: 0 = clean finish (slot goes idle). Non-zero = the watchdog treats
it as a crash and relaunches. A failed *account* is NOT a crash — it is recorded as a
failed row and the loop moves on.
"""

import os
import sys
import json
import time
import signal
import asyncio
import argparse
import threading
from datetime import datetime

# Chrome kyun mara — iska jawab sirf yahan se milta hai. Playwright ka driver is flag pe
# browser ka apna stderr aur uska exit line print karta hai:
#     <process did exit: exitCode=..., signal=...>
#     X connection to :100 broken (explicit kill or server shutdown)
# Iske bina "Target page, context or browser has been closed" ke aage kuch nahi dikhta —
# na exit code, na signal, na X ka message. Chrome ka --log-file in dono ko nahi pakadta.
# Shor thoda badhta hai, isliye NYKAA_PW_DEBUG=0 se band kiya ja sakta hai.
if str(os.environ.get("NYKAA_PW_DEBUG", "1")).lower() not in ("0", "false", "no", "off"):
    os.environ.setdefault("DEBUG", "pw:browser*")

os.environ.setdefault("TZ", "Asia/Calcutta")
try:
    time.tzset()
except Exception:
    pass

# ---- frozen-aware base folder ----
if getattr(sys, "frozen", False):
    BASE = os.path.dirname(sys.executable)
else:
    BASE = os.path.dirname(os.path.abspath(__file__))

# BASE in sys.path for BOTH cases. It used to be set only in the non-frozen branch,
# so the .py run found nykaa_* and the .exe did not — an exe's own folder is not on
# sys.path. That was the "kuch systems pe khulta hi nahi" bug.
if BASE not in sys.path:
    sys.path.insert(0, BASE)

CRASH_LOG = os.path.join(BASE, "crash.log")


def _peek_instance():
    """Read --instance straight off argv, BEFORE the nykaa modules are imported.

    nykaa_login fixes its Chrome debug port and profile dir at IMPORT time from
    NYKAA_INSTANCE. Setting that env inside main() was too late — the module had
    already picked instance 0 / port 9222, so every slot on a box would have driven the
    same browser.
    """
    argv = sys.argv
    for i, a in enumerate(argv):
        if a == "--instance" and i + 1 < len(argv):
            try:
                return max(1, int(argv[i + 1]))
            except ValueError:
                return 1
        if a.startswith("--instance="):
            try:
                return max(1, int(a.split("=", 1)[1]))
            except ValueError:
                return 1
    return 1


os.environ.setdefault("NYKAA_INSTANCE", str(_peek_instance()))


def _fatal(title, exc):
    """Say WHY before dying. A silent exit is the one thing that wastes an afternoon."""
    import traceback
    detail = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    try:
        with open(CRASH_LOG, "a", encoding="utf-8") as f:
            f.write(f"\n===== {datetime.now():%Y-%m-%d %H:%M:%S} — {title} =====\n{detail}")
    except Exception:
        pass
    try:
        sys.stderr.write(f"\n[FATAL] {title}: {exc}\n{detail}\n")
    except Exception:
        pass


# Guarded: these used to be bare module-level imports, so a missing module killed the
# process before anything could report it.
try:
    from envload import load_env
    load_env()
    import db
except Exception as _e:
    _fatal("Startup — db/envload", _e)
    sys.exit(1)

try:
    import nykaa_login as nk
    import nykaa_multi_otp_flow as core
except Exception as _e:
    _fatal("Startup — nykaa modules", _e)
    sys.exit(1)

# =====================================================================
#  CONFIG
#  Runtime knobs live in the dashboard, not here:
#    how many accounts  ->  Nykaa page (per run)
#    headless / chrome  ->  NYKAA_HEADLESS / CHROME_PATH env (see nykaa_login.py)
# =====================================================================
IDLE_POLLS    = 3      # this many empty claims in a row -> exit(0)
IDLE_SLEEP    = 10     # seconds to wait on an empty queue
INFRA_GIVEUP  = 3      # this many browser-launch failures -> stop, queue untouched
# Hard cap on ONE account. Must comfortably exceed everything the flow waits for, or
# the cancellation closes a perfectly healthy browser mid-signin and the failure looks
# like a crash. The waits it has to clear:
#     mobile OTP  30s x 24 = 12 min   (nykaa_smsindia_flow.OTP_*)
#     email OTP   10s x 42 =  7 min   (EMAIL_OTP_*)
#     page loads / form / address     ~3 min
# 600s was SHORTER than the mobile-OTP wait alone.
# 3600 = comfortably more than the 22 min those waits can add up to, PLUS the browser's
# own (now generous) page timeouts. This is a runaway guard, not a deadline: no healthy
# account should ever reach it, and one that does gives its queue row BACK.
ACCOUNT_TIMEOUT = int(os.environ.get("NYKAA_ACCOUNT_TIMEOUT", 3600))   # 60 min
def _nykaa_setting(key, default):
    """settings.json -> nykaa.<key>, dashboard se set hota hai. Launch par padha jaata
    hai, to badalne ke baad slot restart karna kaafi hai."""
    try:
        from settings_util import load_settings
        v = (load_settings("nykaa") or {}).get(key)
        return default if v in (None, "") else type(default)(v)
    except Exception:
        return default


# Lagataar itne fail hone par slot ruk jaata hai. Dashboard se badla ja sakta hai:
# Settings -> Nykaa -> "Stop after N failures in a row".
MAX_CONSEC_FAIL = _nykaa_setting("max_consec_fail", 8)

INSTANCE_ID = 1        # set in main() from --instance

LOG_JSON = os.path.join(BASE, "log.json")
_log_lock = threading.Lock()
_log_records = []


# InfraError lives in nykaa_login so the flows and this runner share one type.
InfraError = nk.InfraError


def _persist_log(msg):
    line = str(msg).rstrip("\n")
    if not line.strip():
        return
    rec = {"ts": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "msg": line}
    with _log_lock:
        _log_records.append(rec)
        try:
            with open(_log_path(), "w", encoding="utf-8") as f:
                json.dump(_log_records[-500:], f, ensure_ascii=False, indent=2)
        except Exception:
            pass


def _log_path():
    """Per-instance log file. One shared log.json read-modify-written on every line
    races and corrupts once several slots run on one box. The DB is the real record;
    this is just a local tail."""
    d = os.path.join(BASE, "nykaa_logs")
    try:
        os.makedirs(d, exist_ok=True)
    except Exception:
        return LOG_JSON
    return os.path.join(d, f"instance{INSTANCE_ID}.json")


class _Tee:
    """stdout -> console AND log.json."""
    def __init__(self, orig):
        self.orig = orig
        self._buf = ""

    def write(self, s):
        try:
            if self.orig:
                self.orig.write(s)
        except Exception:
            pass
        self._buf += s
        while "\n" in self._buf:
            line, self._buf = self._buf.split("\n", 1)
            _persist_log(line)

    def flush(self):
        try:
            if self.orig:
                self.orig.flush()
        except Exception:
            pass


# ---------------- one account ----------------
async def create_one():
    """Create a single account. Returns (ok, detail).

    Raises InfraError when the BROWSER could not be started — that is the box's fault,
    not this account's, and the caller must put the row back rather than spend it.
    """
    # The browser is launched by Playwright inside create_single_account now (see
    # nykaa_login.launch_browser) — no more spawning Chrome on a fixed debug port and
    # connecting over CDP. A launch failure surfaces as nk.InfraError.
    sem = asyncio.Semaphore(1)
    ok = await core.create_single_account(sem)
    return bool(ok), None


# ---------------- runner ----------------
async def run_fleet(count=None):
    """Pull work until the queue is dry (or until `count` is done in standalone mode).

    `count` set  -> standalone: no DB queue, just make N accounts (the old behaviour).
    `count` None -> fleet mode: claim from nykaa_tasks like every other bot.
    """
    print(f"🚀 START | instance: {INSTANCE_ID} | mode: "
          f"{'standalone x' + str(count) if count else 'queue'}")

    # Balance check once at startup — cheap, and a dead SMS provider is worth knowing
    # before burning through rows.
    try:
        resp = await core.sms_api("getBalance")
        print(f"[SMS] getBalance -> {resp}")
        if any(x in str(resp) for x in ("NO_BALANCE", "BAD_KEY", "ERROR")):
            print("[WARN] SMS provider problem — fallback provider se try hoga.")
    except Exception as e:
        print(f"[SMS] balance check error: {e}")

    ok_n = fail_n = 0
    empty = infra = consec_fail = 0
    stop = {"flag": False, "abort": None}

    def _stop(signum, _frame):
        print(f"\n[SIGNAL] {signum} — current account ke baad rukenge.")
        stop["flag"] = True

    for s in (signal.SIGTERM, signal.SIGINT):
        try:
            signal.signal(s, _stop)
        except Exception:
            pass

    while True:
        if stop["flag"]:
            print("[STOP] rok diya gaya.")
            break
        if count is not None and ok_n >= count:
            break

        # ---- get a unit of work ----
        task = None
        if count is None:
            try:
                paused = await asyncio.to_thread(db.is_paused)
            except Exception:
                paused = False
            if paused:
                print("   fleet paused — waiting")
                await asyncio.sleep(15)
                continue

            try:
                task = await asyncio.to_thread(db.claim_nykaa_task, INSTANCE_ID)
            except Exception as e:
                print(f"   claim failed ({str(e)[:80]}) — retrying")
                await asyncio.sleep(10)
                continue

            if not task:
                empty += 1
                if empty >= IDLE_POLLS:
                    print("   queue empty — exiting")
                    break
                await asyncio.sleep(IDLE_SLEEP)
                continue
            empty = 0

        label = f"task {task['id']}" if task else f"{ok_n + 1}/{count}"
        print(f"\n===== ACCOUNT {label} =====")

        t0 = time.time()
        try:
            ok, detail = await asyncio.wait_for(create_one(), timeout=ACCOUNT_TIMEOUT)
            err = None
        except asyncio.TimeoutError:
            # A timeout is the CLOCK's verdict, not the account's — nothing proved this
            # row is bad. Give it back like a box failure does, so the batch count stays
            # honest instead of being spent on a run that simply took too long.
            print(f"[ERR] timeout >{ACCOUNT_TIMEOUT}s — task queue me wapas")
            if task:
                try:
                    await asyncio.to_thread(db.release_nykaa_task, task["id"])
                    print(f"   task {task['id']} queue me wapas (kharch nahi hua)")
                except Exception as e2:
                    print(f"   release failed: {str(e2)[:120]}")
            consec_fail += 1
            if consec_fail >= MAX_CONSEC_FAIL:
                print(f"   lagataar {consec_fail} fail — ruk rahe hain.")
                break
            await asyncio.sleep(5)
            continue
        except InfraError as e:
            # BOX broken: give the row back untouched and get out. Burning the queue at
            # machine speed with zero accounts made is the worst thing this loop can do.
            print(f"🛑 BOX PROBLEM (not the account): {e}")
            if task:
                try:
                    await asyncio.to_thread(db.release_nykaa_task, task["id"])
                    print(f"   task {task['id']} queue me wapas (kharch nahi hua)")
                except Exception as e2:
                    print(f"   release failed: {str(e2)[:120]}")
            infra += 1
            if infra >= INFRA_GIVEUP:
                stop["abort"] = str(e)
                print(f"   {infra} box failures — ruk rahe hain. FIX THE BOX: {e}")
                break
            await asyncio.sleep(5)
            continue
        except Exception as e:
            ok, detail, err = False, None, str(e)[:200]
            print(f"[ERR] {err}")
            if "balance" in err.lower():
                stop["flag"] = True
                print("[STOP] Balance khatam.")
        infra = 0

        # ---- record it ----
        if ok:
            ok_n += 1
            consec_fail = 0
            print(f"[OK] {ok_n} account ban gaye.")
        else:
            fail_n += 1
            consec_fail += 1
            print(f"[FAIL] (lagataar fail: {consec_fail})")

        if task:
            try:
                await asyncio.to_thread(
                    db.finish_nykaa_task, task["id"], ok,
                    json.dumps(detail)[:500] if detail else None,
                    err, round(time.time() - t0, 1))
            except Exception as e:
                # Row stays 'running'; the Nykaa page's "Clear stuck rows" returns it.
                print(f"   finish failed for task {task['id']}: {str(e)[:120]}")

        if not ok:
            if consec_fail >= MAX_CONSEC_FAIL:
                print(f"[WARN] {consec_fail} lagataar fail — 30s wait.")
                await asyncio.sleep(30)
                consec_fail = 0
            else:
                await asyncio.sleep(3)

    if stop["abort"]:
        print(f"\n🛑 EXIT(3) | instance {INSTANCE_ID} | box is broken, queue untouched "
              f"| {stop['abort']}")
        return 3
    print(f"\n🎊 EXIT | instance {INSTANCE_ID} | {ok_n} ok, {fail_n} failed")
    return 0


def main():
    global INSTANCE_ID

    ap = argparse.ArgumentParser(description="Nykaa account creator (fleet edition)")
    # node_agent.py always passes these two.
    ap.add_argument("--instance", type=int, default=1, help="global instance id (OFFSET+slot)")
    ap.add_argument("--total-instances", type=int, default=1,
                    help="fleet size; informational — work is split by the DB queue")
    ap.add_argument("--count", type=int,
                    help="standalone: make N accounts and exit, ignoring the DB queue")
    args = ap.parse_args()

    INSTANCE_ID = max(1, args.instance)
    # NYKAA_INSTANCE was already set from argv before the imports (see _peek_instance);
    # nykaa_login has its port/profile from it. Just report what it settled on.
    print(f"⚙️  instance {INSTANCE_ID} | engine {getattr(core, '_ENGINE', '?')} | "
          f"chrome {os.path.basename(nk.CHROME_PATH)} | headless {nk.HEADLESS}")
    # Kis instance par kaunsa provider chalega — dashboard ki setting yahan dikh jaati
    # hai, taaki fleet me har slot ka plan log se hi pata chal jaye.
    print(f"📮 providers {getattr(core, 'PROVIDER_PLAN', '?')} | "
          f"fallback {getattr(core, 'PROVIDER_FALLBACK', '?')} | "
          f"stop after {MAX_CONSEC_FAIL} fails")

    sys.stdout = _Tee(sys.__stdout__)
    sys.stderr = _Tee(sys.__stderr__)

    if args.count is not None and args.count <= 0:
        ap.error("--count must be >= 1")

    return asyncio.run(run_fleet(args.count))


if __name__ == "__main__":
    try:
        sys.exit(main() or 0)
    except SystemExit:
        raise
    except Exception as e:
        _fatal("Fatal", e)
        sys.exit(1)
