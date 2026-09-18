#!/usr/bin/env python3
"""Magzter v3 runtime engine — runs on the MAIN / controller server.

Every tick it does the two things that turn a campaign into live bot work:

  1. generate_campaign_tasks()  — for the active campaign, create PENDING buyer tasks up
     to today's plan (campaign_days.planned), each pairing a reserved unused card + unused
     identity + an employee. A daily gate bounds card spend to the plan.
  2. promote_completed_reads()  — every completed purchase not yet handed to the reader
     becomes a read_task, so the readers get fed automatically.

The buyers/readers on the worker servers claim from the tables this fills (the claim path
JOINs the card number/CVV/email back on — see db._enrich_claimed). Respects the global
pause switch. Idempotent and crash-safe: every DB write commits per tick, and a crash just
resumes on restart.

Run as the `magzterv3-sync` systemd service (one per fleet, on the main box). Env:
  SYNC_INTERVAL  seconds between ticks (default 30)
"""
import os
import time

os.environ.setdefault("TZ", "Asia/Calcutta")
try:
    import time as _t
    _t.tzset()
except Exception:
    pass

from envload import load_env
load_env()

import db

INTERVAL = max(5, int(os.environ.get("SYNC_INTERVAL", "30")))


def _maintenance():
    """Crash-recovery + failover that MUST run every tick (regression: magzter-old did this
    in its sync cycle; it was dropped, which is the single biggest root cause of the fleet
    stalling — dead bots leave rows stuck 'running'/'reserved', which then (a) count as
    in-flight so generate_campaign_tasks mints nothing, (b) count toward the daily cap so the
    buyer stops claiming and slots idle, (c) keep reads/cards pinned so they pile up, and
    (d) keep 'stuck instance' alerts from ever clearing). Each helper is independently fail-
    safe and idempotent, so one failing must never block the others or the minting below."""
    for label, fn in (("buyer-stale", lambda: db.reset_stale_running()),
                      ("reader-stale", lambda: db.reset_stale_reads()),
                      ("card-stale", lambda: db.reset_stale_card_slots()),
                      ("cooldown", lambda: db.cooldown_and_reassign()),
                      ("corp-case", lambda: db.normalize_card_corp_ids())):
        try:
            n = fn()
            if n:
                print(f"[sync] {label}: recovered {n}", flush=True)
        except Exception as e:
            print(f"[sync] {label} error: {str(e)[:120]}", flush=True)


def tick():
    # Honour the fleet pause switch — when paused, stop feeding new work.
    try:
        if db.is_paused():
            return
    except Exception:
        pass  # if we can't read the flag, keep going rather than stall production

    _maintenance()                          # crash-recovery + dying-employee failover FIRST
    made = db.generate_campaign_tasks()
    promoted = db.promote_completed_reads()
    if made or promoted:
        print(f"[sync] generated {made} task(s), promoted {promoted} read(s)", flush=True)


def main():
    db.assert_db_ready()
    print(f"[sync] runtime engine up — every {INTERVAL}s (Ctrl+C to stop)", flush=True)
    while True:
        try:
            tick()
        except KeyboardInterrupt:
            print("[sync] stopped", flush=True)
            return
        except Exception as e:
            # never let one bad tick kill the loop
            print(f"[sync] tick error: {e}", flush=True)
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
