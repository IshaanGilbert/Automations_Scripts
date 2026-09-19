#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Postgres store for the whole system — quotas, cards, identities, transactions,
reader work.

Postgres is the ONLY source of truth. There is no Google Sheet anywhere in this
system: no import, no writeback, no gspread, no service-account credentials.

  admin sets a quota   ->  quotas
  cards quota          ->  cards (slots, filled by card_generation.py)
  names + emails       ->  identities (first x last, drawn as a quota needs them)
  buyer claims         ->  a card + an identity  ->  tasks
  completed task       ->  read_tasks (the reader's work)

Group-claiming is atomic via FOR UPDATE SKIP LOCKED, so any number of instances
across any number of servers can claim concurrently without racing.

Connection comes from (first match wins):
  1. env DATABASE_URL                 e.g. postgresql://user:CHANGE_ME_PASSWORD@10.0.0.5:5432/magzter
  2. env PGHOST/PGPORT/PGDATABASE/PGUSER/PGPASSWORD
  3. config.json keys: DATABASE_URL, or DB_HOST/DB_PORT/DB_NAME/DB_USER/DB_PASSWORD
"""

import os, json, time, re, random

try:
    import psycopg2
    import psycopg2.extras
except Exception:                       # surfaced clearly when first used
    psycopg2 = None

# Resolve config.json NEXT TO db.py, not relative to the current working directory.
# Otherwise running from any other CWD (e.g. systemd/supervisor with a different
# WorkingDirectory) silently
# loses the DB_* settings -> "No DB connection configured".
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

# Canonical status values stored in the DB (the dashboard maps these to the
# emoji labels the sheet/humans expect on writeback).
ST_PENDING     = "pending"
ST_RUNNING     = "running"
ST_COMPLETED   = "completed"
ST_FAILED      = "failed"
ST_DECLINED    = "declined"
ST_INELIGIBLE  = "ineligible"
ST_UNCONFIRMED = "unconfirmed"
ST_DONE        = "done"          # reader (read.py) finished an account successfully
ST_RETRY       = "retry"         # reader hit a TRANSIENT failure (slow page / session
                                 # expired) — NOT a real "no transaction"; auto-retried

# How many rows a buyer instance grabs per claim. SMALL on purpose: a crash/restart then
# orphans at most this many 'running' rows (instead of a huge ceil(pending/ipe) slice that
# piled up hundreds of stale rows), and work spreads across more instances.
CLAIM_BATCH = 3

# Task fields the bot consumes (mirrors the old sheet task dict).
_TASK_COLS = ("card_no", "month", "cvv", "email", "corp_id", "emp_id",
              "first_name", "last_name")


def _load_config():
    # Don't swallow the reason silently — a missing file or invalid JSON here shows up
    # downstream as the misleading "No DB connection configured", so surface it.
    if not os.path.exists(CONFIG_FILE):
        print(f"⚠️ db.py: config.json NOT FOUND at {CONFIG_FILE}", flush=True)
        return {}
    try:
        with open(CONFIG_FILE) as f:
            return json.loads(f.read().strip())
    except PermissionError:
        # config.json is often root-owned 0600 (the agent rewrites it as root on every
        # "Save & push"), so a non-root reader (manual init_schema, or a service running
        # as ubuntu) gets EACCES. Fall back to a passwordless `sudo cat` so a file-perm
        # blip never takes the whole DB layer down again.
        try:
            import subprocess
            out = subprocess.run(["sudo", "-n", "cat", CONFIG_FILE],
                                 capture_output=True, timeout=10)
            if out.returncode == 0 and out.stdout:
                return json.loads(out.stdout.decode("utf-8", "ignore").strip())
            print("⚠️ db.py: config.json permission denied; sudo fallback also failed "
                  f"(rc={out.returncode}) — run: sudo chown $USER {CONFIG_FILE}", flush=True)
        except Exception as e:
            print(f"⚠️ db.py: config.json sudo-read failed: {e}", flush=True)
        return {}
    except Exception as e:
        print(f"⚠️ db.py: config.json at {CONFIG_FILE} failed to parse: {e}", flush=True)
        return {}


def _dsn():
    """Resolve a libpq DSN / connection string from env or config.json."""
    if os.environ.get("DATABASE_URL"):
        return os.environ["DATABASE_URL"]
    if os.environ.get("PGHOST"):
        return ""  # libpq reads PG* env vars itself when dsn is empty
    cfg = _load_config()
    if cfg.get("DATABASE_URL"):
        return cfg["DATABASE_URL"]
    host = (cfg.get("DB_HOST") or "").strip()
    name = cfg.get("DB_NAME"); user = cfg.get("DB_USER"); pwd = cfg.get("DB_PASSWORD")
    # The config is GLOBAL (same DB_HOST pushed to every box), but the controller —
    # where Postgres is local — usually can't reach its own PUBLIC IP (NAT hairpin).
    # So on that box drop a marker file `.db_local` next to db.py and we force
    # 127.0.0.1 there, while workers keep using the public DB_HOST from config.
    if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".db_local")):
        host = "127.0.0.1"
    # If any DB_* key is set, build a DSN. Missing host defaults to 127.0.0.1 so a
    # single-server setup works even if DB_HOST was left blank (multi-server still
    # needs the controller's LAN IP here).
    if host or name or user or pwd:
        host = host or "127.0.0.1"
        port = cfg.get("DB_PORT", 5432)
        name = name or "magzter"
        user = user or "magzter"
        pwd  = pwd  or ""
        return f"host={host} port={port} dbname={name} user={user} password={pwd}"
    raise RuntimeError(
        "No DB connection configured. Set DATABASE_URL (env or config.json) or "
        "DB_HOST/DB_NAME/DB_USER/DB_PASSWORD in config.json.")


def _conn():
    if psycopg2 is None:
        raise RuntimeError("psycopg2 not installed — run: pip install psycopg2-binary")
    last = None
    for attempt in range(5):
        try:
            c = psycopg2.connect(_dsn(), connect_timeout=10)
            c.autocommit = False
            # Return all TIMESTAMPTZ values in IST so the dashboard shows IST, not UTC.
            try:
                with c.cursor() as _cur:
                    _cur.execute("SET TIME ZONE 'Asia/Kolkata'")
                c.commit()
            except Exception:
                try: c.rollback()
                except Exception: pass
            return c
        except Exception as e:
            last = e
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"DB connect failed after retries: {last}")


def _to_task(r):
    """Row dict -> the task dict shape the buyer expects (plus DB ids).

    NOTE: card_no/month/cvv/email/first_name/last_name were moved OFF the tasks table
    to cards/identities by migration 003. The campaign claim path that JOINs them back
    in is part of the runtime engine (not built yet), so those come via .get() here —
    a claim query without the JOIN yields None rather than a KeyError. Once the engine
    lands, the claim SELECT must JOIN cards+identities and alias these columns.
    """
    g = r.get if hasattr(r, "get") else (lambda k, d=None: d)
    return {
        "task_id":   r["id"],
        # `row` was the Google Sheet row number. Sheets is gone; the task id is
        # the identity. Kept under the same key so the bots' log lines still work.
        "row":       r["id"],
        "card_no":   g("card_no"),
        "month":     g("month"),
        "cvv":       g("cvv"),
        "email":     g("email"),
        "updated_email":  r.get("updated_email") if hasattr(r, "get") else None,
        "email_attempts": (r.get("email_attempts") if hasattr(r, "get") else 0) or 0,
        "password":  r.get("password") if hasattr(r, "get") else None,
        "corp_id":   g("corp_id"),
        "emp_id":    g("emp_id"),
        "first_name": g("first_name"),
        "last_name":  g("last_name"),
    }


def _enrich_claimed(conn, rows):
    """The runtime-engine claim JOIN: attach the real card number/CVV/expiry, the
    account email, and the buyer's first/last name onto freshly-claimed task rows.

    Migration 003 moved these OFF `tasks` onto cards/identities/emails; the claim
    itself is a bare `UPDATE tasks ... RETURNING *`, so we backfill the joined columns
    here by task id. `updated_email` (email-mutation retries) wins over the canonical
    address, matching _to_task's precedence. Missing pieces stay None (a task with no
    card/identity claimed yet just won't transact) rather than raising."""
    if not rows:
        return rows
    ids = [r["id"] for r in rows]
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("""
            SELECT t.id,
                   c.card_no, c.cvv, c.expiry AS month,
                   i.first_name, i.last_name,
                   COALESCE(t.updated_email, e.email) AS email
              FROM tasks t
              LEFT JOIN cards      c ON c.id = t.card_id
              LEFT JOIN identities i ON i.id = t.identity_id
              LEFT JOIN emails     e ON e.id = i.email_id
             WHERE t.id = ANY(%s)
        """, (ids,))
        extra = {row["id"]: row for row in cur.fetchall()}
    for r in rows:
        ex = extra.get(r["id"])
        if ex:
            for k in ("card_no", "cvv", "month", "first_name", "last_name", "email"):
                r[k] = ex.get(k)
    return rows


def generate_campaign_tasks():
    """RUNTIME ENGINE — top up today's PENDING tasks for the active campaign to its
    daily plan, each pairing a reserved unused card + unused identity + an employee.

    Daily gate: never let (settled today + in-flight) exceed campaign_days.planned for
    CURRENT_DATE, so daily card spend is bounded to the plan. Card+identity are reserved
    (unused->reserved) so no other tick re-uses them; the unique indexes on
    tasks.card_id / tasks.identity_id are the hard backstop. Returns #created.
    """
    # CARRY-OVER first: reconcile past days to what they actually delivered and roll any
    # shortfall onto today/future, so today's plan reflects the TRUE remaining budget.
    try:
        replan_forward()
    except Exception:
        pass
    conn = _conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT id, corp_id, employee_ids
                  FROM campaigns WHERE status='active' ORDER BY id LIMIT 1
            """)
            camp = cur.fetchone()
            if not camp:
                return 0
            cid = camp["id"]
            # EMPLOYEE POOL — runtime corporate switch. If any corporate is configured,
            # the pool is the union of every ACTIVE employee of every ACTIVE corporate,
            # each employee carrying its OWN corp_id (both corps active => both run; one
            # active => only that one). If the corporates table is empty, fall back to the
            # campaign's own corp_id + employee_ids (unchanged single-corp behaviour).
            # ACTIVE corporates OVERRIDE the campaign's employee list — but only when at least
            # one is actually set up (active corp + active emp). If none are, fall back to the
            # campaign's own corp_id + employee_ids, so an empty/all-off corporates table can
            # NEVER stall buys (regression fix: it used to return 0 and stop minting).
            pool = _active_corp_pool(cur)              # [(corp_id, emp_id), ...]
            if not pool:
                pool = [(camp["corp_id"], e) for e in (camp["employee_ids"] or [])]
            if not pool:
                return 0
            cur.execute("SELECT planned FROM campaign_days WHERE campaign_id=%s AND day=CURRENT_DATE", (cid,))
            row = cur.fetchone()
            today_plan = int(row["planned"]) if row and row["planned"] else 0
            if today_plan <= 0:
                return 0
            cur.execute("""
                SELECT count(*) AS n FROM tasks
                 WHERE campaign_id=%s
                   AND status IN ('completed','failed','declined','ineligible','unconfirmed')
                   AND updated_at::date = CURRENT_DATE
            """, (cid,))
            settled_today = int(cur.fetchone()["n"])
            cur.execute("SELECT count(*) AS n FROM tasks WHERE campaign_id=%s AND status IN ('pending','running')", (cid,))
            inflight = int(cur.fetchone()["n"])
            need = today_plan - settled_today - inflight
            if need <= 0:
                return 0
            created = 0
            for _ in range(need):
                # claim one unused card for this campaign (reserve it)
                cur.execute("""
                    UPDATE cards SET status='reserved', updated_at=now()
                     WHERE id = (SELECT id FROM cards
                                  WHERE campaign_id=%s AND status='unused'
                                  ORDER BY id FOR UPDATE SKIP LOCKED LIMIT 1)
                 RETURNING id
                """, (cid,))
                cr = cur.fetchone()
                if not cr:
                    break                                    # no unused cards left
                card_id = cr["id"]
                # claim one unused identity (reserve it)
                cur.execute("""
                    UPDATE identities SET status='reserved'
                     WHERE id = (SELECT id FROM identities
                                  WHERE campaign_id=%s AND status='unused'
                                  ORDER BY id FOR UPDATE SKIP LOCKED LIMIT 1)
                 RETURNING id
                """, (cid,))
                ir = cur.fetchone()
                if not ir:
                    cur.execute("UPDATE cards SET status='unused' WHERE id=%s", (card_id,))
                    break                                    # no unused identities left
                corp_id, emp = pool[(settled_today + inflight + created) % len(pool)]
                # Snapshot the ACTUAL email onto the task (not just the identity_id FK) so a
                # buyer record survives even if its email/identity row is later deleted.
                cur.execute("""
                    INSERT INTO tasks (campaign_id, corp_id, emp_id, card_id, identity_id, status, email)
                    SELECT %s,%s,%s,%s,%s,'pending', e.email
                      FROM identities i JOIN emails e ON e.id = i.email_id
                     WHERE i.id = %s
                """, (cid, corp_id, emp, card_id, ir["id"], ir["id"]))
                created += 1
            conn.commit()
            return created
    finally:
        conn.close()


def request_cards(n, campaign_id=None, corp_id=None):
    """Queue n new cards for generation (status='requested') on the active campaign
    (or a specified one). `corp_id` tags the slots so the generator uses THAT corporate's
    portal login and every resulting card is stamped with its source corporate (else the
    slots stay corp-less and use the global Settings login). The card_generation bots then
    fill them to 'unused'. Returns the number requested. Raises ValueError if no campaign."""
    n = max(0, int(n))
    if not n:
        return 0
    corp_id = (str(corp_id).strip() or None) if corp_id else None
    conn = _conn()
    try:
        with conn.cursor() as cur:
            if campaign_id:
                cur.execute("SELECT id FROM campaigns WHERE id=%s", (int(campaign_id),))
            else:
                cur.execute("SELECT id FROM campaigns WHERE status='active' ORDER BY id LIMIT 1")
            row = cur.fetchone()
            if not row:
                raise ValueError("no active campaign — create one before buying cards")
            cid = row[0]
            if corp_id is not None:
                # Match case-INsensitively and adopt the corporate's exact casing, so a card
                # tagged 'streakads' and a corporate 'STREAKADS' never split into two.
                cur.execute("SELECT corp_id, active FROM corporates WHERE lower(corp_id)=lower(%s) LIMIT 1", (corp_id,))
                r = cur.fetchone()
                if not r:
                    raise ValueError("no such corporate")
                corp_id = r[0]                      # canonical casing from corporates
                if not r[1]:
                    raise ValueError("that corporate is turned off — activate it first")
            cur.execute("INSERT INTO cards (campaign_id, corp_id, status) "
                        "SELECT %s, %s, 'requested' FROM generate_series(1, %s)", (cid, corp_id, n))
            conn.commit()
            return n
    finally:
        conn.close()


def import_cards(cards, campaign_id=None, corp_id=None):
    """Import ALREADY-MADE real cards into the pool (ready to use — no portal generation).
    `cards` = iterable of (card_no, expiry, cvv, max_amount).

    FILL FIRST (user rule): if the corp already has EMPTY 'requested' slots, the numbers go
    INTO those slots (status -> 'unused') instead of creating brand-new rows — so importing
    fills the pending requests rather than piling up duplicates. Only once its requested slots
    are used up does a surplus card become a fresh 'unused' row. Dedups on the global card_no
    unique index (a number already in the pool anywhere is skipped), so re-importing is safe.
    corp_id tags them. Returns {'filled': f, 'inserted': i, 'skipped': s, 'slots_left': n}."""
    import re as _re
    corp_id = (str(corp_id).strip() or None) if corp_id else None
    conn = _conn()
    try:
        with conn.cursor() as cur:
            if campaign_id:
                cur.execute("SELECT id FROM campaigns WHERE id=%s", (int(campaign_id),))
            else:
                cur.execute("SELECT id FROM campaigns WHERE status='active' ORDER BY id LIMIT 1")
            row = cur.fetchone()
            if not row:
                raise ValueError("no active campaign — create one first")
            cid = row[0]
            # corp_id is just a TAG for imported cards — accept any value (don't require a
            # corporates row / table, so import works regardless of the corporates feature).
            # But if a corporate matches case-INsensitively, adopt its exact casing so an
            # import tagged 'streakads' lands under the configured 'STREAKADS', not beside it.
            if corp_id is not None:
                cur.execute("SELECT corp_id FROM corporates WHERE lower(corp_id)=lower(%s) LIMIT 1", (corp_id,))
                _cr = cur.fetchone()
                if _cr:
                    corp_id = _cr[0]
            # dedup against every card number already in the pool
            cur.execute("SELECT card_no FROM cards WHERE card_no IS NOT NULL")
            existing = {r[0] for r in cur.fetchall()}
            # empty 'requested' slots for THIS corp (fill these first), oldest first
            if corp_id is not None:
                cur.execute("""SELECT id FROM cards
                                WHERE campaign_id=%s AND corp_id=%s AND status='requested'
                                  AND card_no IS NULL ORDER BY id""", (cid, corp_id))
            else:
                cur.execute("""SELECT id FROM cards
                                WHERE campaign_id=%s AND corp_id IS NULL AND status='requested'
                                  AND card_no IS NULL ORDER BY id""", (cid,))
            slots = [r[0] for r in cur.fetchall()]
            filled = inserted = skipped = 0
            si = 0
            for c in cards:
                cn = _re.sub(r"\D", "", str((c[0] if len(c) > 0 else "") or ""))
                if len(cn) not in (15, 16) or cn in existing:
                    skipped += 1
                    continue
                existing.add(cn)
                ex = str((c[1] if len(c) > 1 else "") or "").strip()
                cv = _re.sub(r"\D", "", str((c[2] if len(c) > 2 else "") or ""))
                mx = c[3] if len(c) > 3 else None
                try:
                    mx = float(mx) if mx not in (None, "") else None
                except Exception:
                    mx = None
                if si < len(slots):                       # fill an existing requested slot
                    cur.execute("""UPDATE cards SET card_no=%s, expiry=%s, cvv=%s, max_amount=%s,
                                         status='unused', generated_at=now(), updated_at=now()
                                   WHERE id=%s AND status='requested'""",
                                (cn, ex, cv, mx, slots[si]))
                    si += 1
                    filled += 1
                else:                                     # no slot left — fresh unused card
                    cur.execute("""
                        INSERT INTO cards (campaign_id, corp_id, card_no, expiry, cvv,
                                           max_amount, status, generated_at)
                        VALUES (%s,%s,%s,%s,%s,%s,'unused', now())
                        ON CONFLICT (card_no) WHERE card_no IS NOT NULL DO NOTHING
                    """, (cid, corp_id, cn, ex, cv, mx))
                    inserted += cur.rowcount
        conn.commit()
        return {"filled": filled, "inserted": inserted, "skipped": skipped,
                "slots_left": max(0, len(slots) - si)}
    finally:
        conn.close()


def set_card_target(n, campaign_id=None):
    """Set the number of OUTSTANDING card requests to exactly `n` — the "make only N
    now" control. Adds 'requested' rows if short; cancels surplus 'requested' rows
    (newest first) if over. NEVER touches cards already generating / unused / used, so
    work in progress and cards already made are always safe. Returns the new count.
    """
    n = max(0, int(n))
    conn = _conn()
    try:
        with conn.cursor() as cur:
            if campaign_id:
                cur.execute("SELECT id FROM campaigns WHERE id=%s", (int(campaign_id),))
            else:
                cur.execute("SELECT id FROM campaigns WHERE status='active' ORDER BY id LIMIT 1")
            row = cur.fetchone()
            if not row:
                raise ValueError("no active campaign")
            cid = row[0]
            cur.execute("SELECT count(*) FROM cards WHERE campaign_id=%s AND status='requested'", (cid,))
            outstanding = int(cur.fetchone()[0])
            if n > outstanding:
                cur.execute("INSERT INTO cards (campaign_id, status) "
                            "SELECT %s, 'requested' FROM generate_series(1, %s)", (cid, n - outstanding))
            elif n < outstanding:
                cur.execute("""
                    DELETE FROM cards WHERE id IN (
                        SELECT id FROM cards WHERE campaign_id=%s AND status='requested'
                        ORDER BY id DESC LIMIT %s)
                """, (cid, outstanding - n))
            conn.commit()
            return n
    finally:
        conn.close()


def analytics_daily(days=30):
    """Fleet-wide per-day totals for the Analytics volume trend — one row per day for
    the last `days` days (gaps filled with 0): completed / failed buyer txns + reads,
    plus the per-day success rate. Used by /api/analytics/daily."""
    try:
        n = max(1, min(int(days), 120))
    except (TypeError, ValueError):
        n = 30
    conn = _conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT to_char(d, 'YYYY-MM-DD') AS iso,
                  (SELECT count(*) FROM tasks t
                     WHERE t.updated_at::date = d AND t.status = 'completed') AS completed,
                  (SELECT count(*) FROM tasks t
                     WHERE t.updated_at::date = d
                       AND t.status IN ('failed','declined','ineligible')) AS failed,
                  (SELECT count(*) FROM read_tasks r
                     WHERE COALESCE(r.read_at, r.updated_at)::date = d
                       AND r.status = 'done') AS reads
                  FROM generate_series(CURRENT_DATE - (%s - 1) * interval '1 day',
                                       CURRENT_DATE, interval '1 day') d
                 ORDER BY d
            """, [n])
            out = []
            for r in cur.fetchall():
                comp, fail = int(r["completed"]), int(r["failed"])
                out.append({"date": r["iso"], "completed": comp, "failed": fail,
                            "reads": int(r["reads"]),
                            "rate": round(comp / (comp + fail) * 100, 1) if (comp + fail) else 0.0})
            return out
    finally:
        conn.close()


def campaign_daily(campaign_id, date_from=None, date_to=None):
    """Per-DAY transaction + read totals for a whole campaign (the Subscription and Read
    reports). One row per day: txns / completed / failed / reads / books."""
    cid = int(campaign_id)
    tx_f, tx_p = _extra("t.updated_at", None, date_from, date_to, None)
    rd_f, rd_p = _extra("COALESCE(r.read_at, r.updated_at)", None, date_from, date_to, None)
    conn = _conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            days = {}
            cur.execute(f"""
                SELECT to_char(date_trunc('day', t.updated_at),'YYYY-MM-DD') AS iso,
                       count(*) FILTER (WHERE t.status <> 'pending') AS txns,
                       count(*) FILTER (WHERE t.status = 'completed') AS completed,
                       count(*) FILTER (WHERE t.status IN ('failed','declined','ineligible')) AS failed
                  FROM tasks t
                 WHERE t.campaign_id = %s AND t.updated_at IS NOT NULL{tx_f}
                 GROUP BY 1
            """, [cid] + tx_p)
            for r in cur.fetchall():
                days[r["iso"]] = {"iso": r["iso"], "txns": int(r["txns"]),
                                  "completed": int(r["completed"]), "failed": int(r["failed"]),
                                  "reads_done": 0, "books": 0}
            cur.execute(f"""
                SELECT to_char(date_trunc('day', COALESCE(r.read_at, r.updated_at)),'YYYY-MM-DD') AS iso,
                       count(*) FILTER (WHERE r.status='done') AS reads_done,
                       COALESCE(sum(r.books_read),0) AS books
                  FROM read_tasks r JOIN tasks t ON t.id = r.source_task_id
                 WHERE t.campaign_id = %s{rd_f}
                 GROUP BY 1
            """, [cid] + rd_p)
            for r in cur.fetchall():
                d = days.setdefault(r["iso"], {"iso": r["iso"], "txns": 0, "completed": 0,
                                               "failed": 0, "reads_done": 0, "books": 0})
                d["reads_done"] = int(r["reads_done"] or 0)
                d["books"] = int(r["books"] or 0)
            out = sorted(days.values(), key=lambda x: x["iso"], reverse=True)
            for d in out:
                d["date"] = _fmt_day(d["iso"])
                d["success_rate"] = round(d["completed"] / d["txns"] * 100, 1) if d["txns"] else 0.0
            return out
    finally:
        conn.close()


def promote_completed_reads():
    """RUNTIME ENGINE — every completed purchase not yet handed to the reader becomes a
    read_task (email + the campaign account password + name). Idempotent via
    uq_read_source (ON CONFLICT source_task_id). Returns #promoted."""
    # User rule: hand UNCONFIRMED buys to the reader too — an unconfirmed purchase is
    # often a real one whose thank-you page just never loaded, so reading it both uses
    # the account and confirms it. Set PROMOTE_UNCONFIRMED=0 to promote only 'completed'.
    statuses = ['completed']
    if os.environ.get("PROMOTE_UNCONFIRMED", "1") == "1":
        statuses.append(ST_UNCONFIRMED)
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                WITH picked AS (
                    SELECT t.id, i.first_name, i.last_name, i.email_id, t.updated_email,
                           t.campaign_id, t.transaction_id, t.updated_at
                      FROM tasks t JOIN identities i ON i.id = t.identity_id
                     WHERE t.status = ANY(%s) AND t.read_request = FALSE
                     ORDER BY t.id
                ), ins AS (
                    INSERT INTO read_tasks (email, password, name_used, source_task_id,
                                            status, transaction_id, transaction_at)
                    SELECT COALESCE(p.updated_email, e.email), q.account_password,
                           p.first_name || ' ' || p.last_name, p.id, 'pending',
                           p.transaction_id, p.updated_at
                      FROM picked p
                      JOIN emails    e ON e.id = p.email_id
                      JOIN campaigns q ON q.id = p.campaign_id
                    ON CONFLICT (source_task_id) DO NOTHING
                    RETURNING source_task_id
                )
                UPDATE tasks SET read_request = TRUE
                 WHERE id IN (SELECT source_task_id FROM ins)
            """, (statuses,))
            n = cur.rowcount
            conn.commit()
            return n
    finally:
        conn.close()


# ================= SCHEMA =================
#
# The schema is owned by ALEMBIC, not by this file.
#
#   schema.py           — SQLAlchemy Core metadata, the single source of truth
#   migrations/         — versioned, reversible migrations
#   alembic upgrade head — the deploy step (was: init_schema() on every boot)
#
# init_schema() used to live here: one CREATE TABLE IF NOT EXISTS blob plus eight
# ALTER TABLE ... ADD COLUMN IF NOT EXISTS backfills, with no version history and no
# way back. It was deleted in Phase 1 — see docs/REVAMP_PLAN.md §3.0.
#
# To change the schema: edit schema.py, run `alembic revision --autogenerate -m "..."`,
# review the generated migration, then `alembic upgrade head`.


def assert_db_ready():
    """Verify the DB is reachable AND migrated. Raises on either failure.

    This replaces init_schema(). Every caller of init_schema() was really doing a
    reachability check — the bots wrap it in `except: sys.exit(1)` with the message
    "DB not reachable" (buyer.py:2147, read.py:1062). They never needed the tables
    created; they needed to know the DB was there before starting a browser.

    So this keeps that contract (connect, raise if you can't) and adds the check the
    old code could not make: that the schema has actually been migrated. Under
    init_schema() a bot would happily start against a half-built schema and fail
    later, mid-transaction. Now it fails at startup with a message that says what to
    do about it.
    """
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT to_regclass('public.tasks'), to_regclass('public.alembic_version')")
            tasks_tbl, version_tbl = cur.fetchone()
            if tasks_tbl is None or version_tbl is None:
                raise RuntimeError(
                    "database is reachable but not migrated (no `tasks`/`alembic_version` "
                    "table) — run `alembic upgrade head`. See docs/REVAMP_PLAN.md §3.0."
                )
    finally:
        conn.close()


def init_schema():
    """Removed — the schema is managed by alembic. Use assert_db_ready().

    Deliberately raises rather than aliasing assert_db_ready(): this function used to
    CREATE tables, and a caller that still believes that is a caller whose deploy
    never runs `alembic upgrade head`. Failing loudly here surfaces that on the first
    boot instead of leaving the fleet running against whatever schema happens to exist.
    """
    raise RuntimeError(
        "db.init_schema() has been removed — the schema is managed by alembic.\n"
        "  - bots/services: call db.assert_db_ready() instead\n"
        "  - deploy:        run `alembic upgrade head`\n"
        "See docs/REVAMP_PLAN.md §3.0."
    )


# ================= QUOTAS / CARDS / IDENTITIES (read side) =================
#
# Read-only helpers backing the Quotas / Card Pool / Identities / Needs Review
# pages. The WRITE side (pre-provisioning, generation, the claim gate) is Phase 3
# — see docs/REVAMP_PLAN.md §5, §6.
#
# NOTE ON ERROR HANDLING: these deliberately do NOT wrap everything in
# `except Exception: return []`. That idiom is what hid two permanently-broken
# dashboard panels (proxy_health, card_bin_health — REVAMP_PLAN §3.6) for an
# unknown length of time. A broken query here should be loud.


# ---------------------------------------------------------------------------
# CAMPAIGNS — monthly budget + daily plan (spec: Budget-Based Campaign Planning)
# ---------------------------------------------------------------------------

def _compute_plan(budget, start_date, end_date, buffer_days):
    """Spread `budget` across the working days, leaving `buffer_days` slack at the end.

    Working days = calendar days from start..end MINUS the buffer. Budget is split as
    evenly as possible over the working window (early days), so the plan finishes ~4-5
    days before month-end and those tail days are catch-up capacity if a day is missed.

    Returns [(date, planned)] for EVERY calendar day start..end — buffer days get 0.
    Pure function; the DB clock decides start/end, this just divides.
    """
    total_days = (end_date - start_date).days + 1
    working = max(1, total_days - int(buffer_days))
    working = min(working, total_days)                 # buffer can't exceed the window
    base, extra = divmod(int(budget), working)         # first `extra` days get +1
    out = []
    d = start_date
    for i in range(total_days):
        planned = (base + 1) if i < extra else (base if i < working else 0)
        out.append((d, planned))
        d = d + _one_day()
    return out


def _one_day():
    import datetime as _dt
    return _dt.timedelta(days=1)


def _rebalance(cur, campaign_id):
    """Redistribute the un-pinned, still-future budget so the plan sums to `budget`.

    Pinned days and past days are fixed points; whatever budget they don't account for
    is spread evenly over the remaining un-pinned days from today onward. This is what
    keeps the monthly total intact after an admin edits one day (chosen: auto-rebalance).
    """
    cur.execute("SELECT budget FROM campaigns WHERE id=%s", (campaign_id,))
    budget = int(cur.fetchone()[0])

    # Everything already committed: pinned days (any date) + past un-pinned days.
    cur.execute("""
        SELECT COALESCE(sum(planned), 0) FROM campaign_days
         WHERE campaign_id=%s AND (pinned = TRUE OR day < CURRENT_DATE)
    """, (campaign_id,))
    fixed = int(cur.fetchone()[0])

    cur.execute("""
        SELECT id FROM campaign_days
         WHERE campaign_id=%s AND pinned = FALSE AND day >= CURRENT_DATE
         ORDER BY day
    """, (campaign_id,))
    free_ids = [r[0] for r in cur.fetchall()]
    if not free_ids:
        return
    remaining = max(0, budget - fixed)
    base, extra = divmod(remaining, len(free_ids))
    for i, cid in enumerate(free_ids):
        cur.execute("UPDATE campaign_days SET planned=%s WHERE id=%s",
                    ((base + 1) if i < extra else base, cid))


def replan_forward():
    """CARRY-OVER (user rule): a day that fell short must not lose its budget. Pin every PAST
    day to the number it ACTUALLY delivered (completed + unconfirmed), then rebalance the true
    remaining budget across today + future days — so a shortfall rolls forward and the month
    always catches up, instead of the budget silently under-delivering because past days
    'reserved' buys that never happened. Idempotent; safe to run on every generate tick / at
    day rollover. Pinned future days (e.g. an operator's "complete the rest") are respected."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM campaigns WHERE status='active' ORDER BY id LIMIT 1")
            row = cur.fetchone()
            if not row:
                return False
            cid = row[0]
            cur.execute("""
                UPDATE campaign_days d
                   SET planned = COALESCE((
                           SELECT count(*) FROM tasks t
                            WHERE t.campaign_id = d.campaign_id
                              AND t.status IN (%s, %s)
                              AND t.updated_at::date = d.day), 0),
                       pinned = TRUE
                 WHERE d.campaign_id = %s AND d.day < CURRENT_DATE
            """, (ST_COMPLETED, ST_UNCONFIRMED, cid))
            _rebalance(cur, cid)
        conn.commit()
        return True
    except Exception as e:
        print(f"⚠️ replan_forward failed: {e}", flush=True)
        return False
    finally:
        conn.close()


def _clean_emp_list(xs):
    """Normalise an employee-id list: strip, uppercase, dedupe, drop blanks."""
    out, seen = [], set()
    for x in (xs or []):
        x = str(x or "").strip().upper()
        if x and x not in seen:
            seen.add(x)
            out.append(x)
    return out


def create_campaign(budget, account_password, buffer_days=5, name=None,
                    email_alert_days=2, corp_id=None, employee_ids=None,
                    backup_employee_ids=None):
    """Start a monthly campaign: compute the daily plan AND pre-provision the cards.

    - Retires any currently-active campaign (uq_campaign_active enforces one at a time).
    - Plan runs today..month-end with a buffer (spec: 4-5 day margin).
    - Pre-provisions `budget` card slots at status='requested' (§5.1) — cards can NEVER
      exceed the budget because that is the only place slots are created.
    - Records which employees this campaign runs on + their backups.

    Returns {campaign_id, provisioned, plan_days}.
    """
    budget = int(budget)
    if budget < 1:
        raise ValueError("budget must be >= 1")
    if not (account_password or "").strip():
        raise ValueError("account_password is required")
    buffer_days = max(0, int(buffer_days))
    emps = _clean_emp_list(employee_ids)
    backups = _clean_emp_list(backup_employee_ids)
    # A backup that is also a primary is meaningless — drop the overlap from backups.
    backups = [b for b in backups if b not in set(emps)]
    corp_id = (str(corp_id).strip() or None) if corp_id else None

    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE campaigns SET status='done' WHERE status='active'")
            superseded = cur.rowcount

            # Start today, end month-end — computed on the DB clock (IST), not the caller's.
            cur.execute("""
                INSERT INTO campaigns (name, budget, buffer_days, start_date, end_date,
                                       status, account_password, email_alert_days,
                                       corp_id, employee_ids, backup_employee_ids)
                VALUES (%s, %s, %s, CURRENT_DATE,
                        (date_trunc('month', CURRENT_DATE) + interval '1 month'
                         - interval '1 day')::date,
                        'active', %s, %s, %s, %s, %s)
             RETURNING id, start_date, end_date
            """, (name or "Campaign", budget, buffer_days,
                  account_password.strip(), max(0, int(email_alert_days)),
                  corp_id, emps, backups))
            cid, start_date, end_date = cur.fetchone()

            for day, planned in _compute_plan(budget, start_date, end_date, buffer_days):
                cur.execute(
                    "INSERT INTO campaign_days (campaign_id, day, planned) VALUES (%s,%s,%s)",
                    (cid, day, planned))

            # NOTE (user rule): cards are NO LONGER auto-provisioned here. Nothing is made
            # until the operator explicitly asks for it via "Buy cards" (request_cards) /
            # "Make only N now" (set_card_target) — and there, per corporate. `budget` stays
            # the campaign cap; it just isn't pre-filled. Until cards exist the buyer engine
            # has nothing to reserve, so no buys run either — exactly the desired behaviour.
            provisioned = cur.rowcount
        conn.commit()
        return {"campaign_id": cid, "provisioned": provisioned,
                "plan_days": (end_date - start_date).days + 1, "superseded": superseded}
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def set_campaign_budget(campaign_id, budget):
    """Admin raised/lowered the monthly budget. Recompute the plan, adjust the card pool.

    - Un-pinned future days rebalance to the new total; pinned/past days stay.
    - Card slots grow (INSERT more 'requested') or shrink (delete only still-'requested'
      ones — never a card that has a number or is in use). So the pool tracks the budget
      without ever exceeding it or destroying real cards.
    """
    budget = int(budget)
    if budget < 1:
        raise ValueError("budget must be >= 1")
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE campaigns SET budget=%s WHERE id=%s AND status='active'",
                        (budget, campaign_id))
            if cur.rowcount == 0:
                raise ValueError("no active campaign with that id")

            cur.execute("SELECT count(*) FROM cards WHERE campaign_id=%s", (campaign_id,))
            have = int(cur.fetchone()[0])
            # Cards already committed (anything past 'requested') can't be un-made, so
            # they are the FLOOR the pool can shrink to. Comparing budget against the
            # total (`have`) was the bug: it deleted every 'requested' slot yet left the
            # committed cards above budget.
            cur.execute("""
                SELECT count(*) FROM cards
                 WHERE campaign_id=%s AND status <> 'requested'
            """, (campaign_id,))
            committed = int(cur.fetchone()[0])
            delta = budget - have
            if delta > 0:
                cur.execute("INSERT INTO cards (campaign_id, status) "
                            "SELECT %s, 'requested' FROM generate_series(1, %s)",
                            (campaign_id, delta))
                pool_change = f"+{delta} requested slots"
            elif delta < 0:
                # Shrink toward budget, but never below what's already committed, and
                # only ever delete empty 'requested' slots — real/used cards stay.
                to_remove = min(-delta, max(0, have - committed))
                cur.execute("""
                    DELETE FROM cards WHERE id IN (
                        SELECT id FROM cards
                         WHERE campaign_id=%s AND status='requested'
                         ORDER BY id DESC LIMIT %s)
                """, (campaign_id, to_remove))
                removed = cur.rowcount
                if budget < committed:
                    pool_change = (f"-{removed} requested slots (floored at {committed} "
                                   f"already-used cards — can't shrink below that)")
                else:
                    pool_change = f"-{removed} requested slots"
            else:
                pool_change = "unchanged"

            # A budget change RE-PLANS the future: clear per-day pins on today-onward so
            # _rebalance can spread the whole new budget across them. Without this, pinned
            # days stay fixed and the plan sum diverges from the budget (e.g. one pinned
            # day of 60 with a new budget of 20, or all days pinned at 1 with budget 500).
            # Past days stay as-is; if they alone exceed the new budget, the plan floors
            # there — same principle as the card floor above.
            cur.execute("""
                UPDATE campaign_days SET pinned = FALSE
                 WHERE campaign_id = %s AND day >= CURRENT_DATE
            """, (campaign_id,))
            _rebalance(cur, campaign_id)
        conn.commit()
        return {"budget": budget, "pool": pool_change}
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def set_campaign_employees(campaign_id, corp_id=None, employee_ids=None,
                           backup_employee_ids=None, account_password=None):
    """Update which employees the active campaign runs on + backups + (optional) the
    constant account password.

    account_password: only updated when a non-empty value is given, so leaving the
    field blank keeps the current password (no accidental wipe).
    """
    emps = _clean_emp_list(employee_ids)
    backups = [b for b in _clean_emp_list(backup_employee_ids) if b not in set(emps)]
    pw = (account_password or "").strip() or None
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE campaigns
                   SET corp_id=%s, employee_ids=%s, backup_employee_ids=%s,
                       account_password = COALESCE(%s, account_password)
                 WHERE id=%s AND status='active'
            """, ((str(corp_id).strip() or None) if corp_id else None,
                  emps, backups, pw, campaign_id))
            if cur.rowcount == 0:
                raise ValueError("no active campaign with that id")
        conn.commit()
        return {"corp_id": corp_id, "employee_ids": emps,
                "backup_employee_ids": backups, "password_changed": pw is not None}
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ================= CORPORATES (runtime corp switch) =================
# Multiple corporates, each with its own employees, each independently active. The
# runtime engine (generate_campaign_tasks) mints tasks across the ACTIVE employees of
# every ACTIVE corporate. See migration 0012.

def _corporates_configured(cur):
    """True if ANY corporate row exists — i.e. the operator manages corps here (so the
    engine uses the corp pool rather than the campaign's single corp_id). If the corporates
    table isn't there yet (migration 0012 not applied), behave as 'not configured' so the
    engine safely falls back to the campaign's own corp_id instead of crashing."""
    try:
        cur.execute("SELECT to_regclass('corporates') AS t")
        if cur.fetchone()["t"] is None:
            return False
        cur.execute("SELECT EXISTS(SELECT 1 FROM corporates) AS e")
        return bool(cur.fetchone()["e"])
    except Exception:
        return False


def _active_corp_pool(cur):
    """[(corp_id, emp_id)] for every ACTIVE employee of every ACTIVE corporate, stable
    order. Empty => nothing configured active (engine then mints nothing)."""
    cur.execute("""
        SELECT ce.corp_id, ce.emp_id
          FROM corp_employees ce
          JOIN corporates c ON c.corp_id = ce.corp_id
         WHERE c.active AND ce.active
         ORDER BY ce.corp_id, ce.emp_id
    """)
    return [(r["corp_id"], r["emp_id"]) for r in cur.fetchall()]


def _release_pending_tasks(cur, where_sql, params):
    """A corp/employee just went inactive (or was deleted): drop its still-PENDING,
    never-run tasks and free the card+identity they had reserved back to 'unused' so the
    resources aren't stranded. Running/finished tasks are never touched. Returns #freed."""
    cur.execute(f"""UPDATE cards SET status='unused', updated_at=now()
                     WHERE id IN (SELECT card_id FROM tasks
                                   WHERE status='pending' AND {where_sql})
                       AND status='reserved'""", params)
    cur.execute(f"""UPDATE identities SET status='unused'
                     WHERE id IN (SELECT identity_id FROM tasks
                                   WHERE status='pending' AND {where_sql})
                       AND status='reserved'""", params)
    cur.execute(f"DELETE FROM tasks WHERE status='pending' AND {where_sql}", params)
    return cur.rowcount


def list_corporates():
    """Every corporate with its employees — for the Corp manager UI. Each corp:
    {corp_id, label, active, note, employees:[{emp_id, active}], emp_total, emp_active}."""
    conn = _conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""SELECT corp_id, label, active, note,
                                  portal_username,
                                  (portal_password IS NOT NULL AND portal_password <> '') AS has_password
                             FROM corporates ORDER BY corp_id""")
            corps = [dict(r) for r in cur.fetchall()]
            cur.execute("""SELECT corp_id, emp_id, active FROM corp_employees
                            ORDER BY corp_id, emp_id""")
            by = {}
            for r in cur.fetchall():
                by.setdefault(r["corp_id"], []).append({"emp_id": r["emp_id"], "active": r["active"]})
            for c in corps:
                emps = by.get(c["corp_id"], [])
                c["employees"] = emps
                c["emp_total"] = len(emps)
                c["emp_active"] = sum(1 for e in emps if e["active"])
            return corps
    finally:
        conn.close()


def add_corporate(corp_id, label=None, note=None):
    """Create a corporate. Idempotent-ish: updates label/note if it already exists."""
    corp_id = (str(corp_id or "").strip())
    if not corp_id:
        raise ValueError("corp_id required")
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""INSERT INTO corporates (corp_id, label, note) VALUES (%s,%s,%s)
                           ON CONFLICT (corp_id) DO UPDATE
                             SET label = COALESCE(EXCLUDED.label, corporates.label),
                                 note  = COALESCE(EXCLUDED.note,  corporates.note)""",
                        (corp_id, (label or "").strip() or None, (note or "").strip() or None))
        conn.commit()
        return {"corp_id": corp_id}
    finally:
        conn.close()


def set_corporate_login(corp_id, portal_username=None, portal_password=None):
    """Store a corporate's MasterCard-portal login (used by card_generation.py for that
    corp's card slots). Username is set when provided; password is only overwritten when a
    non-empty value is given (blank = keep existing, so the UI never needs to re-type it)."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            uname = (portal_username or "").strip()
            pw = (portal_password or "").strip() or None      # None => keep existing
            cur.execute("""
                UPDATE corporates
                   SET portal_username = %s,
                       portal_password = COALESCE(%s, portal_password)
                 WHERE corp_id = %s
            """, (uname or None, pw, str(corp_id)))
            if cur.rowcount == 0:
                raise ValueError("no such corporate")
        conn.commit()
        return {"corp_id": corp_id, "portal_username": uname or None,
                "password_changed": pw is not None}
    finally:
        conn.close()


def set_corporate_active(corp_id, active):
    """Toggle a corporate on/off. Turning OFF also releases its pending (never-run)
    tasks so an inactive corp stops running immediately. Returns {active, released}."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE corporates SET active=%s WHERE corp_id=%s",
                        (bool(active), str(corp_id)))
            if cur.rowcount == 0:
                raise ValueError("no such corporate")
            released = 0
            if not active:
                released = _release_pending_tasks(cur, "corp_id=%s", (str(corp_id),))
        conn.commit()
        return {"active": bool(active), "released": released}
    finally:
        conn.close()


def delete_corporate(corp_id):
    """Delete a corporate (its employees cascade) and release its pending tasks."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            released = _release_pending_tasks(cur, "corp_id=%s", (str(corp_id),))
            cur.execute("DELETE FROM corporates WHERE corp_id=%s", (str(corp_id),))
        conn.commit()
        return {"released": released}
    finally:
        conn.close()


def add_corp_employees(corp_id, emp_ids):
    """Bulk-add employees to a corporate. Accepts a list or a raw newline/comma string.
    Ignores duplicates. Returns {added, skipped}."""
    corp_id = str(corp_id or "").strip()
    if isinstance(emp_ids, str):
        import re as _re
        emp_ids = [p for p in _re.split(r"[,\s]+", emp_ids) if p]
    emps = []
    seen = set()
    for e in (emp_ids or []):
        e = str(e).strip()
        if e and e not in seen:
            seen.add(e); emps.append(e)
    if not corp_id:
        raise ValueError("corp_id required")
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM corporates WHERE corp_id=%s", (corp_id,))
            if not cur.fetchone():
                raise ValueError("no such corporate")
            added = 0
            for e in emps:
                cur.execute("""INSERT INTO corp_employees (corp_id, emp_id) VALUES (%s,%s)
                               ON CONFLICT (corp_id, emp_id) DO NOTHING""", (corp_id, e))
                added += cur.rowcount
        conn.commit()
        return {"added": added, "skipped": len(emps) - added}
    finally:
        conn.close()


def set_corp_employee_active(corp_id, emp_id, active):
    """Toggle one employee. Turning OFF releases that employee's pending tasks."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE corp_employees SET active=%s WHERE corp_id=%s AND emp_id=%s",
                        (bool(active), str(corp_id), str(emp_id)))
            if cur.rowcount == 0:
                raise ValueError("no such employee")
            released = 0
            if not active:
                released = _release_pending_tasks(cur, "corp_id=%s AND emp_id=%s",
                                                  (str(corp_id), str(emp_id)))
        conn.commit()
        return {"active": bool(active), "released": released}
    finally:
        conn.close()


def delete_corp_employee(corp_id, emp_id):
    """Remove an employee from a corporate and release its pending tasks."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            released = _release_pending_tasks(cur, "corp_id=%s AND emp_id=%s",
                                              (str(corp_id), str(emp_id)))
            cur.execute("DELETE FROM corp_employees WHERE corp_id=%s AND emp_id=%s",
                        (str(corp_id), str(emp_id)))
        conn.commit()
        return {"released": released}
    finally:
        conn.close()


def set_campaign_day(campaign_id, day, planned):
    """Admin edited one day's target. Pin it and rebalance the rest (auto-rebalance).

    Rejects a value that would push the plan past the monthly budget: a day can hold at
    most `budget - (other pinned + past days)`. Without this a single edit could make the
    plan sum exceed the budget, silently breaking the "month totals budget" invariant.
    """
    planned = int(planned)
    if planned < 0:
        raise ValueError("planned must be >= 0")
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT budget FROM campaigns WHERE id=%s AND status='active'",
                        (campaign_id,))
            row = cur.fetchone()
            if not row:
                raise ValueError("no active campaign with that id")
            budget = int(row[0])

            # Budget already spoken for by OTHER fixed days (pinned, or past-and-unpinned),
            # excluding the day being edited.
            cur.execute("""
                SELECT COALESCE(sum(planned), 0) FROM campaign_days
                 WHERE campaign_id=%s AND day <> %s
                   AND (pinned = TRUE OR day < CURRENT_DATE)
            """, (campaign_id, day))
            other_fixed = int(cur.fetchone()[0])
            ceiling = max(0, budget - other_fixed)
            if planned > ceiling:
                raise ValueError(
                    f"that day can be at most {ceiling:,} — the rest of the fixed plan "
                    f"already accounts for {other_fixed:,} of the {budget:,} budget")

            cur.execute("""
                UPDATE campaign_days SET planned=%s, pinned=TRUE
                 WHERE campaign_id=%s AND day=%s
            """, (planned, campaign_id, day))
            if cur.rowcount == 0:
                raise ValueError("that day is not in the campaign plan")
            _rebalance(cur, campaign_id)
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def set_today_target(campaign_id, planned):
    """Set TODAY's transaction target (the quick "only N today" / "complete the rest"
    control on the Subscription page). Resolves the server's CURRENT_DATE so it lines
    up exactly with buyer_daily_cap_reached()'s CURRENT_DATE check — set it to 100 and
    the buyer auto-pauses once 100 are claimed today; raise it (or send a huge number)
    and the buyer resumes. The value is CLAMPED to the max this day can hold (budget
    minus the other fixed days), so "complete the rest" can pass a big number safely."""
    planned = max(0, int(planned))
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT to_char(CURRENT_DATE, 'YYYY-MM-DD')")
            today = cur.fetchone()[0]
            cur.execute("SELECT budget FROM campaigns WHERE id=%s AND status='active'", (campaign_id,))
            r = cur.fetchone()
            if not r:
                raise ValueError("no active campaign with that id")
            budget = int(r[0])
            cur.execute("""
                SELECT COALESCE(sum(planned), 0) FROM campaign_days
                 WHERE campaign_id=%s AND day <> %s AND (pinned = TRUE OR day < CURRENT_DATE)
            """, (campaign_id, today))
            other_fixed = int(cur.fetchone()[0])
            ceiling = max(0, budget - other_fixed)
    finally:
        conn.close()
    if planned > ceiling:
        planned = ceiling      # "complete the rest" — cap at what today can hold
    return set_campaign_day(campaign_id, today, planned)


def _autoclose_expired(cur):
    """Mark any active campaign whose month has ended as 'done', so last month's
    campaign becomes a history entry automatically when the month rolls over.
    Runs inside the caller's transaction (cheap, idempotent)."""
    cur.execute("""
        UPDATE campaigns SET status='done'
         WHERE status='active' AND end_date < CURRENT_DATE
    """)


def close_campaign(campaign_id=None):
    """Manually complete/close a campaign -> status 'done' (moves it to history).

    campaign_id=None closes the currently-active one. Returns the closed id, or None
    if there was nothing active to close.
    """
    conn = _conn()
    try:
        with conn.cursor() as cur:
            if campaign_id is not None:
                cur.execute("UPDATE campaigns SET status='done' "
                            "WHERE id=%s AND status='active' RETURNING id", (campaign_id,))
            else:
                cur.execute("UPDATE campaigns SET status='done' "
                            "WHERE status='active' RETURNING id")
            row = cur.fetchone()
        conn.commit()
        return row[0] if row else None
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def campaign_list():
    """Every campaign (active + past), newest first — for the history dropdown.

    Each row carries enough to label it and show at-a-glance progress without the
    full per-day plan. So a completed month stays viewable/exportable next month.
    """
    conn = _conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            _autoclose_expired(cur)          # roll last month's campaign to 'done'
            conn.commit()
            cur.execute("""
                SELECT c.id, c.name, c.budget, c.status, c.start_date, c.end_date,
                       c.created_at, c.corp_id, c.employee_ids, c.backup_employee_ids,
                       (SELECT count(*) FROM tasks t
                         WHERE t.campaign_id=c.id
                           AND t.status = 'completed') AS done,
                       (SELECT count(*) FROM tasks t
                         WHERE t.campaign_id=c.id AND t.status='completed') AS success,
                       (SELECT count(*) FROM cards cd
                         WHERE cd.campaign_id=c.id AND cd.card_no IS NOT NULL) AS cards_filled
                  FROM campaigns c
                 ORDER BY c.start_date DESC, c.id DESC
            """)
            out = []
            for r in cur.fetchall():
                d = dict(r)
                d["done"] = int(d["done"] or 0)
                d["success"] = int(d["success"] or 0)
                d["cards_filled"] = int(d["cards_filled"] or 0)
                budget = int(d["budget"]) or 1
                d["pct"] = round(min(100.0, d["done"] / budget * 100), 1)
                d["success_rate"] = round(d["success"] / d["done"] * 100, 1) if d["done"] else 0.0
                d["month"] = d["start_date"].strftime("%b %Y")
                d["label"] = f"{d['name']} · {d['month']}"
                for k in ("start_date", "end_date"):
                    d[k] = d[k].isoformat() if d[k] else None
                d["created_at"] = d["created_at"].strftime("%Y-%m-%d") if d["created_at"] else None
                out.append(d)
            return out
    finally:
        conn.close()


# The configurable report. ONE row per transaction, spanning the whole lifecycle:
# card (+ when generated) -> account -> transaction (+ when) -> read (+ when).
# Each entry: (column key, human label, group, SQL expression aliased to the key).
# The picker groups by `group`; the admin chooses exactly which columns to download.
_REPORT_FIELDS = [
    # Card details
    ("card_number",     "Card number",      "Card",        "c.card_no"),
    ("card_expiry",     "Expiry",           "Card",        "c.expiry"),
    ("card_cvv",        "CVV",              "Card",        "c.cvv"),
    ("card_max_amount", "Card limit",       "Card",        "c.max_amount"),
    ("card_generated_at","Card generated",  "Card",        "to_char(c.generated_at,'YYYY-MM-DD HH24:MI:SS')"),
    ("card_status",     "Card status",      "Card",        "c.status"),
    # Account / identity
    ("email",           "Email",            "Account",     "COALESCE(t.updated_email, e.email)"),
    ("first_name",      "First name",       "Account",     "i.first_name"),
    ("last_name",       "Last name",        "Account",     "i.last_name"),
    # Transaction details
    ("txn_id",          "Transaction ID",   "Transaction", "t.transaction_id"),
    ("txn_status",      "Transaction status","Transaction","t.status"),
    ("txn_date",        "Transaction date", "Transaction", "to_char(t.updated_at,'YYYY-MM-DD HH24:MI:SS')"),
    ("txn_duration_sec","Duration (s)",     "Transaction", "t.duration_sec"),
    ("txn_proxy_ip",    "Transaction IP",   "Transaction", "t.proxy_ip"),
    ("emp_id",          "Employee",         "Transaction", "t.emp_id"),
    ("corp_id",         "Corporate",        "Transaction", "t.corp_id"),
    ("txn_error",       "Error",            "Transaction", "t.error"),
    # Read details
    ("read_status",     "Read status",      "Read",        "rt.status"),
    ("read_bought_at",  "Bought at",        "Read",        "to_char(rt.transaction_at,'YYYY-MM-DD HH24:MI:SS')"),
    ("read_date",       "Read date",        "Read",        "to_char(rt.read_at,'YYYY-MM-DD HH24:MI:SS')"),
    ("read_proxy_ip",   "Read IP",          "Read",        "rt.proxy_ip"),
    ("read_books",      "Books read",       "Read",        "rt.books_read"),
    ("read_duration_sec","Read duration (s)","Read",       "rt.duration_sec"),
]
_REPORT_BY_KEY = {f[0]: f for f in _REPORT_FIELDS}

# Column metadata for the picker (key + label + group), in report order.
EXPORT_COLUMN_META = [{"key": k, "label": lbl, "group": grp}
                      for (k, lbl, grp, _sql) in _REPORT_FIELDS]
# Backwards-compatible allow-list (all report keys).
EXPORT_COLUMNS = {"report": [f[0] for f in _REPORT_FIELDS]}


def export_campaign_rows(campaign_id, kind="report", columns=None):
    """Rows for a CSV export of one campaign. Returns (header, rows).

    One configurable report: one row per transaction with the card, account,
    transaction and read details joined in. `columns` = the subset/order the admin
    picked (validated against the report field list); defaults to all of them.
    """
    keys = columns or [f[0] for f in _REPORT_FIELDS]
    keys = [k for k in keys if k in _REPORT_BY_KEY] or [f[0] for f in _REPORT_FIELDS]
    # Build the SELECT from the whitelisted field expressions — `keys` can only be
    # known report keys, so nothing user-supplied reaches the SQL text.
    select = ", ".join(f"{_REPORT_BY_KEY[k][3]} AS {k}" for k in keys)

    conn = _conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(f"""
                SELECT {select}
                  FROM tasks t
                  LEFT JOIN cards c        ON c.id = t.card_id
                  LEFT JOIN identities i   ON i.id = t.identity_id
                  LEFT JOIN emails e       ON e.id = i.email_id
                  LEFT JOIN read_tasks rt  ON rt.source_task_id = t.id
                 WHERE t.campaign_id = %s AND t.status <> 'pending'
                 ORDER BY t.updated_at
            """, (campaign_id,))
            rows = [[("" if r[k] is None else r[k]) for k in keys] for r in cur.fetchall()]
            # Human labels as the CSV header, in the chosen order.
            header = [_REPORT_BY_KEY[k][1] for k in keys]
            return header, rows
    finally:
        conn.close()


def campaign_overview(campaign_id=None):
    """A campaign + its plan + live progress. Powers the Campaign page.

    campaign_id=None -> the ACTIVE campaign (default). Pass an id to view a PAST
    campaign read-only (history). Returns None if there's no such campaign.

    Returns None if no matching campaign, else:
      {id, name, budget, buffer_days, start_date, end_date, account_password,
       done, pct, remaining, cards_filled, emails_left, email_alert, today,
       plan: [{day, planned, done, pinned, is_today, is_past}]}
    """
    conn = _conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            _autoclose_expired(cur)          # a month that has ended is no longer active
            conn.commit()
            if campaign_id is not None:
                cur.execute("""
                    SELECT id, name, budget, buffer_days, start_date, end_date,
                           account_password, email_alert_days, created_at,
                           corp_id, employee_ids, backup_employee_ids, status
                      FROM campaigns WHERE id=%s
                """, (campaign_id,))
            else:
                cur.execute("""
                    SELECT id, name, budget, buffer_days, start_date, end_date,
                           account_password, email_alert_days, created_at,
                           corp_id, employee_ids, backup_employee_ids, status
                      FROM campaigns WHERE status='active'
                """)
            c = cur.fetchone()
            if not c:
                return None
            c = dict(c)
            cid = c["id"]
            is_active = (c.get("status") == "active")

            # Show the FULL plan from the day the campaign started (creation day) through
            # month-end — for the active campaign too, not just today onward. The operator
            # needs to SEE past days (pinned to what they actually delivered) so carry-over
            # reads clearly: a day that fell short shows its real number, and the shortfall
            # visibly rolls into today + future (replan_forward keeps the month summing to
            # budget). A campaign started on the 17th plans 17..month-end.
            cur.execute("""
                SELECT d.day, d.planned, d.pinned,
                       (d.day = CURRENT_DATE) AS is_today,
                       (d.day <  CURRENT_DATE) AS is_past,
                       COALESCE((
                         SELECT count(*) FROM tasks t
                          WHERE t.campaign_id=%s
                            AND t.status = 'completed'
                            AND t.updated_at::date = d.day), 0) AS done
                  FROM campaign_days d
                 WHERE d.campaign_id=%s
                 ORDER BY d.day
            """, (cid, cid))
            plan = []
            today_planned = today_done = 0
            for r in cur.fetchall():
                row = dict(r)
                row["done"] = int(row["done"])
                if row["is_today"]:
                    today_planned, today_done = int(row["planned"]), row["done"]
                row["day"] = row["day"].isoformat()
                plan.append(row)

            # Whole-campaign progress = all terminal transactions for it.
            # DONE = actually COMPLETED buys only (operator rule: "show only what actually
            # completes"). Excludes failed/declined/ineligible (not delivered) AND in-flight
            # running/retry/pending. This makes progress = delivered/budget, agrees with the
            # dashboard's "Confirmed buys", and is monotonic — it never dips when crash-recovery
            # re-queues a stuck row (no code path un-completes a completed task).
            cur.execute("""
                SELECT count(*) AS n FROM tasks
                 WHERE campaign_id=%s AND status = 'completed'
            """, (cid,))
            done = int(cur.fetchone()["n"])

            cur.execute("SELECT count(*) AS n FROM cards WHERE campaign_id=%s AND card_no IS NOT NULL",
                        (cid,))
            cards_filled = int(cur.fetchone()["n"])

            # Email runway: unused emails vs how many a typical day needs.
            cur.execute("""
                SELECT count(*) AS n FROM emails
                 WHERE status='active'
                   AND (campaign_id=%s OR campaign_id IS NULL)
                   AND id NOT IN (SELECT email_id FROM identities WHERE campaign_id=%s)
            """, (cid, cid))
            emails_left = int(cur.fetchone()["n"])

            budget = int(c["budget"]) or 1
            avg_daily = max(1, budget // max(1, (c["end_date"] - c["start_date"]).days + 1
                                            - int(c["buffer_days"])))
            runway_days = emails_left / avg_daily if avg_daily else 0

            # NEVER ship the account password to the browser. This overview feeds
            # /api/campaign and the home widget; no template renders the password, so
            # returning it was pure needless exposure (browser cache, devtools, XSS
            # blast radius). The promoter reads campaigns.account_password directly in
            # SQL — it never needs it from here.
            c.pop("account_password", None)

            c.update({
                "start_date": c["start_date"].isoformat(),
                "end_date": c["end_date"].isoformat(),
                "created_at": c["created_at"].strftime("%Y-%m-%d %H:%M"),
                "done": done,
                "pct": round(min(100.0, done / budget * 100), 1),
                "remaining": max(0, budget - done),
                "cards_filled": cards_filled,
                "emails_left": emails_left,
                "email_alert": runway_days < int(c["email_alert_days"]),
                "runway_days": round(runway_days, 1),
                "today_planned": today_planned,
                "today_done": today_done,
                "today_met": today_done >= today_planned and today_planned > 0,
                "read_only": not is_active,   # a past campaign is view/export only
                "plan": plan,
            })
            return c
    finally:
        conn.close()


def claim_card_slots(instance_id, limit=1):
    """Claim `requested` card slots for the generation agent to fill (§5.1).

    Same pattern as _try_claim (db.py:763) — FOR UPDATE SKIP LOCKED — so any number
    of generation agents can run without two of them filling the same slot.

    Returns {'ids': [...], 'corp_id': <str|None>, 'login': {'username','password'}|None}.
    All claimed slots belong to ONE corporate (so the agent logs into that corp's portal
    once and fills them). corp_id NULL = legacy/untagged slots -> login None -> the agent
    uses the global Settings login. Only slots of ACTIVE corporates (or NULL) are claimed.
    The slots are empty; the agent puts real numbers in them via fill_card().
    """
    conn = _conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            # which corporate to work this run: the oldest claimable slot's corp (NULL groups
            # legacy slots together). Skip corps that are turned off.
            cur.execute("""
                SELECT corp_id FROM cards
                 WHERE status='requested'
                   AND campaign_id IN (SELECT id FROM campaigns WHERE status='active')
                   -- allow every slot EXCEPT those tagged with a corporate explicitly turned
                   -- OFF. A corp tag with no corporates row (just a label) or an active corp
                   -- both generate normally, so a tag never stalls card generation.
                   AND (corp_id IS NULL
                        OR corp_id NOT IN (SELECT corp_id FROM corporates WHERE NOT active))
                 ORDER BY id
                 LIMIT 1
            """)
            pick = cur.fetchone()
            if not pick:
                conn.commit()
                return {"ids": [], "corp_id": None, "login": None}
            corp = pick["corp_id"]
            cur.execute("""
                UPDATE cards
                   SET status='generating', ran_by=%s, claimed_at=now(), updated_at=now()
                 WHERE id IN (
                       SELECT id FROM cards
                        WHERE status='requested'
                          AND campaign_id IN (SELECT id FROM campaigns WHERE status='active')
                          AND corp_id IS NOT DISTINCT FROM %s
                        ORDER BY id
                        FOR UPDATE SKIP LOCKED
                        LIMIT %s)
             RETURNING id
            """, (int(instance_id), corp, int(limit)))
            ids = [r["id"] for r in cur.fetchall()]
            login = None
            if corp is not None:
                cur.execute("SELECT portal_username, portal_password FROM corporates WHERE corp_id=%s", (corp,))
                lr = cur.fetchone()
                if lr and (lr["portal_username"] or lr["portal_password"]):
                    login = {"username": lr["portal_username"] or "", "password": lr["portal_password"] or ""}
        conn.commit()
        return {"ids": ids, "corp_id": corp, "login": login}
    finally:
        conn.close()


def fill_card(card_id, card_no, expiry, cvv, max_amount=None):
    """The portal produced a real card — put it in the slot. 'generating' -> 'unused'.

    Guarded on status='generating': if a stale-reset already returned this slot to
    the pool, the write must not resurrect it under a second agent.
    """
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE cards
                   SET card_no=%s, expiry=%s, cvv=%s,
                       max_amount=COALESCE(%s, max_amount),
                       status='unused', generated_at=now(), updated_at=now(), error=NULL
                 WHERE id=%s AND status='generating'
            """, (card_no, expiry, cvv, max_amount, int(card_id)))
            ok = cur.rowcount > 0
        conn.commit()
        if not ok:
            print(f"⚠️ fill_card: slot {card_id} was not 'generating' — skipped", flush=True)
        return ok
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def fail_card_slot(card_id, error=""):
    """The portal failed for this slot — put it back so another agent retries it."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE cards
                   SET status='requested', ran_by=NULL, claimed_at=NULL,
                       error=%s, updated_at=now()
                 WHERE id=%s AND status='generating'
            """, (str(error)[:500], int(card_id)))
        conn.commit()
    finally:
        conn.close()


def release_card_slots(ids):
    """Return specific just-claimed slots to 'requested' (e.g. the agent bailed before
    generating — no portal login for the corp). Only affects rows still 'generating'."""
    ids = [int(i) for i in (ids or [])]
    if not ids:
        return 0
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""UPDATE cards
                              SET status='requested', ran_by=NULL, claimed_at=NULL, updated_at=now()
                            WHERE id = ANY(%s) AND status='generating'""", (ids,))
            n = cur.rowcount
        conn.commit()
        return n
    finally:
        conn.close()


def reset_stale_card_slots(stale_seconds=1800):
    """Return slots stuck 'generating' to 'requested' — the portal crashes.

    Mirrors reset_stale_running (db.py) for the buyer. Without this, a crashed
    generation agent silently strands its claimed slots and the pool never fills.
    """
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE cards
                   SET status='requested', ran_by=NULL, claimed_at=NULL, updated_at=now()
                 WHERE status='generating'
                   AND claimed_at < now() - (%s || ' seconds')::interval
            """, (str(int(stale_seconds)),))
            n = cur.rowcount
        conn.commit()
        return n
    finally:
        conn.close()


def upload_emails(campaign_id, emails, password=None):
    """Bulk-add uploaded emails to a campaign (spec: partial uploads allowed).

    Deduped on the global unique email — an address already present is skipped, not
    errored, so re-uploading an overlapping list is safe. Returns {added, skipped}.
    """
    clean, seen = [], set()
    for e in emails:
        e = (e or "").strip().lower()
        if e and "@" in e and e not in seen:
            seen.add(e)
            clean.append(e)
    if not clean:
        return {"added": 0, "skipped": 0, "received": len(emails)}
    conn = _conn()
    try:
        with conn.cursor() as cur:
            rows = psycopg2.extras.execute_values(cur, """
                INSERT INTO emails (email, campaign_id, password, status)
                VALUES %s
                ON CONFLICT (email) DO NOTHING
                RETURNING id
            """, [(e, campaign_id, password, "active") for e in clean], fetch=True)
            added = len(rows)
        conn.commit()
        return {"added": added, "skipped": len(clean) - added, "received": len(emails)}
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def upload_names(firsts, lasts):
    """Add uploaded first/last names (spec: uploaded once, reused). Deduped.

    Names feed the 1M-capacity cross-product (§5.2). Returns per-pool add counts.
    """
    def _clean(xs):
        out, seen = [], set()
        for x in xs:
            x = (x or "").strip()
            if x and x.lower() not in seen:
                seen.add(x.lower())
                out.append(x)
        return out
    firsts, lasts = _clean(firsts), _clean(lasts)
    conn = _conn()
    try:
        with conn.cursor() as cur:
            fa = la = 0
            if firsts:
                fa = len(psycopg2.extras.execute_values(
                    cur, "INSERT INTO first_names (name) VALUES %s "
                         "ON CONFLICT (name) DO NOTHING RETURNING id",
                    [(n,) for n in firsts], fetch=True))
            if lasts:
                la = len(psycopg2.extras.execute_values(
                    cur, "INSERT INTO last_names (name) VALUES %s "
                         "ON CONFLICT (name) DO NOTHING RETURNING id",
                    [(n,) for n in lasts], fetch=True))
            cur.execute("SELECT (SELECT count(*) FROM first_names), (SELECT count(*) FROM last_names)")
            tf, tl = cur.fetchone()
        conn.commit()
        return {"first_added": fa, "last_added": la,
                "first_total": int(tf), "last_total": int(tl),
                "capacity": int(tf) * int(tl)}
    finally:
        conn.close()


def generate_identities(campaign_id, n):
    """Materialise up to `n` fresh (first, last, email) identities for a campaign (§5.2).

    Draws distinct name pairs from the first×last space that have NEVER been used
    (uq_identity_pair spans all campaigns, so a pair is never reused), each paired with
    the least-used active email. This is the only place identities are created.

    Returns {created, capacity, exhausted, no_emails} — `created` may be < n if the name
    space or the email pool runs dry, which the dashboard surfaces as an alert.
    """
    n = int(n)
    if n < 1:
        return {"created": 0, "capacity": 0, "exhausted": False, "no_emails": False}
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM first_names")
            nf = int(cur.fetchone()[0])
            cur.execute("SELECT count(*) FROM last_names")
            nl = int(cur.fetchone()[0])
            capacity = nf * nl

            # Emails available to this campaign, least-used first — the order we hand
            # them out in. This snapshot is taken ONCE; we round-robin across it in
            # Python so a batch spreads over the whole pool instead of dumping every
            # row on the single least-used email (the old correlated-subquery bug).
            cur.execute("""
                SELECT id FROM emails
                 WHERE status='active' AND (campaign_id=%s OR campaign_id IS NULL)
                 ORDER BY times_used, id
            """, (campaign_id,))
            email_ids = [r[0] for r in cur.fetchall()]
            if not email_ids:
                return {"created": 0, "capacity": capacity, "exhausted": False,
                        "no_emails": True}

            # Fresh (never-used) name pairs, capped at n. At 1M rows the CROSS JOIN
            # materialises in ~1s; past that switch to random-offset sampling (§5.2).
            cur.execute("""
                SELECT f.name, l.name
                  FROM first_names f CROSS JOIN last_names l
                 WHERE NOT EXISTS (
                       SELECT 1 FROM identities i
                        WHERE i.first_name = f.name AND i.last_name = l.name)
                 ORDER BY random()
                 LIMIT %s
            """, (n,))
            pairs = cur.fetchall()
            if not pairs:
                return {"created": 0, "capacity": capacity,
                        "exhausted": capacity > 0, "no_emails": False}

            # Round-robin the email pool across the batch — identity i gets email
            # i % len(pool), so a batch of 6 over 2 emails lands 3/3, not 6/0.
            rows = [(campaign_id, f, l, email_ids[i % len(email_ids)], "unused")
                    for i, (f, l) in enumerate(pairs)]
            inserted = psycopg2.extras.execute_values(cur, """
                INSERT INTO identities (campaign_id, first_name, last_name, email_id, status)
                VALUES %s
                ON CONFLICT (first_name, last_name) DO NOTHING
                RETURNING email_id
            """, rows, fetch=True)
            created = len(inserted)

            # Recompute times_used ABSOLUTELY from the ground truth — the count of
            # identities actually referencing each email. Idempotent and drift-proof,
            # unlike the old `+= cumulative` which double-counted across batches.
            if created:
                touched = tuple({r[0] for r in inserted})
                cur.execute("""
                    UPDATE emails e
                       SET times_used = (SELECT count(*) FROM identities i
                                          WHERE i.email_id = e.id)
                     WHERE e.id IN %s
                """, (touched,))
        conn.commit()
        return {"created": created, "capacity": capacity,
                "exhausted": created < n and capacity > 0,
                "no_emails": False}
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def card_pool():
    """Card pool composition by status + fill progress. {counts, total, ...}

    Drives the Card Pool page's stacked bar. The status order here is the CARD
    LIFECYCLE order (requested -> ... -> used) and the ordinal colour ramp in
    app.css is keyed to it — a lifecycle is ordered, so it gets one hue
    light->dark rather than unrelated categorical hues.
    """
    order = ["requested", "generating", "unused", "reserved", "used", "payment_failed"]
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT status, count(*) FROM cards GROUP BY status")
            counts = {k: 0 for k in order}
            for status, n in cur.fetchall():
                counts[status] = int(n)
            total = sum(counts.values())
            # A slot is "filled" once the portal agent has written a real number to it.
            cur.execute("SELECT count(*) FROM cards WHERE card_no IS NOT NULL")
            filled = int(cur.fetchone()[0])
            return {
                "order": order,
                "counts": counts,
                "total": total,
                "filled": filled,
                "fill_pct": round(filled / total * 100, 1) if total else 0.0,
                "available": counts["unused"],
                "burned": counts["payment_failed"],
            }
    finally:
        conn.close()


def card_pool_by_corp():
    """Per-corporate card breakdown: how many cards each portal login generated,
    where they are in the lifecycle, and how much has actually been SPENT.

    'spent' = SUM(max_amount) of that corp's USED cards — a used card is a card that
    completed a purchase, so its limit is the money that went out under that corp.
    Cards with no corp_id (imported before tagging, or the global login) group under
    'Unassigned' so the totals always reconcile with the whole pool.
    """
    order = ["requested", "generating", "unused", "reserved", "used", "payment_failed"]
    conn = _conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            # Join case-INsensitively and group under the corporate's canonical corp_id, so a
            # pool split across 'streakads' / 'STREAKADS' collapses into the one configured row.
            cur.execute("""
                SELECT COALESCE(co.corp_id, c.corp_id, '') AS corp_id,
                       co.label               AS label,
                       co.active              AS active,
                       c.status               AS status,
                       count(*)               AS n,
                       COALESCE(SUM(CASE WHEN c.status='used' THEN c.max_amount END), 0) AS spent
                  FROM cards c
                  LEFT JOIN corporates co ON lower(co.corp_id) = lower(c.corp_id)
                 GROUP BY COALESCE(co.corp_id, c.corp_id, ''), co.label, co.active, c.status
            """)
            agg = {}
            for r in cur.fetchall():
                cid = r["corp_id"] or ""
                d = agg.setdefault(cid, {
                    "corp_id": cid,
                    "label": r["label"] or (cid if cid else "Unassigned"),
                    "active": r["active"],
                    "counts": {k: 0 for k in order},
                    "total": 0, "spent": 0.0,
                })
                st = r["status"]
                if st in d["counts"]:
                    d["counts"][st] = int(r["n"])
                d["total"] += int(r["n"])
                d["spent"] += float(r["spent"] or 0)
            rows = []
            for d in agg.values():
                c = d["counts"]
                d["available"] = c["unused"]
                d["used"] = c["used"]
                d["wasted"] = c["payment_failed"]
                d["awaiting"] = c["requested"] + c["generating"]
                rows.append(d)
            # Configured corps first (active before inactive), then Unassigned, each by size.
            rows.sort(key=lambda x: (x["corp_id"] == "", not x.get("active"), -x["total"]))
            return rows
    finally:
        conn.close()


def requeue_failed_buys(campaign_id=None, limit=1000):
    """Re-run terminally FAILED buyer tasks (operator action from the dashboard).

    A failed buy already spent its card (marked 'payment_failed'), so a real retry needs a
    FRESH unused card — reusing the wasted one would just fail again. For each failed task we
    reserve a new unused card (preferring the task's own corporate, else any), then reset the
    task to 'pending' with retries cleared so the buyer picks it up behind fresh work. Tasks
    with no card available are left failed and counted. Returns {requeued, no_card, considered}."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            # default to the ACTIVE campaign so a bulk retry never wakes old closed-campaign rows
            if campaign_id is None:
                cur.execute("SELECT id FROM campaigns WHERE status='active' ORDER BY id LIMIT 1")
                _ac = cur.fetchone()
                campaign_id = _ac[0] if _ac else None
            if campaign_id:
                cur.execute("""SELECT id, corp_id FROM tasks
                                WHERE status=%s AND campaign_id=%s ORDER BY id LIMIT %s""",
                            (ST_FAILED, int(campaign_id), int(limit)))
            else:
                cur.execute("""SELECT id, corp_id FROM tasks
                                WHERE status=%s ORDER BY id LIMIT %s""",
                            (ST_FAILED, int(limit)))
            failed = cur.fetchall()
            requeued = no_card = 0
            for tid, corp in failed:
                new_card = None
                # prefer a card from the task's own corporate, else fall back to any unused one
                for corp_filter in ((corp,) if corp else ()) + (None,):
                    cur.execute("""
                        UPDATE cards SET status='reserved', updated_at=now()
                         WHERE id = (SELECT id FROM cards
                                      WHERE status='unused' AND card_no IS NOT NULL
                                        AND (%s IS NULL OR lower(corp_id)=lower(%s))
                                      ORDER BY id FOR UPDATE SKIP LOCKED LIMIT 1)
                     RETURNING id
                    """, (corp_filter, corp_filter))
                    r = cur.fetchone()
                    if r:
                        new_card = r[0]
                        break
                if not new_card:
                    no_card += 1
                    continue
                cur.execute("""UPDATE tasks
                                  SET card_id=%s, status=%s, retries=0, ran_by=NULL,
                                      error=NULL, updated_at=now()
                                WHERE id=%s AND status=%s""",
                            (new_card, ST_PENDING, tid, ST_FAILED))
                if cur.rowcount:
                    requeued += 1
                else:
                    # lost a race — release the card we just reserved
                    cur.execute("UPDATE cards SET status='unused', updated_at=now() WHERE id=%s AND status='reserved'", (new_card,))
            conn.commit()
            return {"requeued": requeued, "no_card": no_card, "considered": len(failed)}
    except Exception as e:
        print(f"⚠️ requeue_failed_buys failed: {e}", flush=True)
        try: conn.rollback()
        except Exception: pass
        raise
    finally:
        conn.close()


def requeue_with_email_mutation(campaign_id=None, statuses=("ineligible", "failed"), limit=1000):
    """Manual rescue (operator action): re-run FAILED / INELIGIBLE buys with a MUTATED email
    AND a fresh card. 'Not eligible' ('account already exists' / 'existing GOLD user') can only
    succeed on a DIFFERENT email — and auto-mutation may not have fired (e.g. it died on a
    generic Stripe error before the eligibility step). For each row we pick a fresh mutated
    email (derived from the ORIGINAL identity email so mutations don't drift), REUSE the task's
    own card (that attempt never charged it — flip it back to 'reserved', so this works even
    with zero unused cards in the pool), and reset it to pending with retries cleared. Only
    'failed'/'ineligible' by default — NEVER 'declined' (that card is genuinely bad). Skips
    rows with no email on file. Returns {requeued, no_email, considered}."""
    stt = list(statuses)
    conn = _conn()
    try:
        with conn.cursor() as cur:
            # default to the ACTIVE campaign so a bulk retry never wakes old closed-campaign rows
            if campaign_id is None:
                cur.execute("SELECT id FROM campaigns WHERE status='active' ORDER BY id LIMIT 1")
                _ac = cur.fetchone()
                campaign_id = _ac[0] if _ac else None
            if campaign_id:
                cur.execute("""
                    SELECT t.id, t.card_id, COALESCE(t.email_attempts,0),
                           e.email AS original, COALESCE(t.updated_email, e.email) AS current
                      FROM tasks t
                      LEFT JOIN identities i ON i.id = t.identity_id
                      LEFT JOIN emails e     ON e.id = i.email_id
                     WHERE t.status = ANY(%s) AND t.campaign_id = %s
                     ORDER BY t.id LIMIT %s
                """, (stt, int(campaign_id), int(limit)))
            else:
                cur.execute("""
                    SELECT t.id, t.card_id, COALESCE(t.email_attempts,0),
                           e.email AS original, COALESCE(t.updated_email, e.email) AS current
                      FROM tasks t
                      LEFT JOIN identities i ON i.id = t.identity_id
                      LEFT JOIN emails e     ON e.id = i.email_id
                     WHERE t.status = ANY(%s)
                     ORDER BY t.id LIMIT %s
                """, (stt, int(limit)))
            rows = cur.fetchall()
            requeued = no_email = 0
            for tid, card_id, attempts, original, current in rows:
                base = original or current
                new_email = mutate_email(base, {current} if current else None) if base else None
                if not new_email:
                    no_email += 1
                    continue
                # Reuse the task's OWN card — a failed/ineligible attempt never charged it
                # (a charged buy would be completed/unconfirmed, not failed), so flip its card
                # back from the conservatively-'wasted' state to 'reserved'. Works even with
                # zero unused cards in the pool. (declined is excluded by the caller — that
                # card really is bad and must not be reused.)
                if card_id:
                    cur.execute("UPDATE cards SET status='reserved', updated_at=now() "
                                "WHERE id=%s AND status IN ('payment_failed','reserved')", (card_id,))
                cur.execute("""
                    UPDATE tasks
                       SET updated_email = %s, email_attempts = %s,
                           status = %s, retries = 0, ran_by = NULL,
                           error = %s, updated_at = now()
                     WHERE id = %s AND status = ANY(%s)
                """, (new_email, int(attempts) + 1, ST_PENDING,
                      f"Manual retry with mutated email: {base} -> {new_email}", tid, stt))
                if cur.rowcount:
                    requeued += 1
            conn.commit()
            return {"requeued": requeued, "no_email": no_email, "considered": len(rows)}
    except Exception as e:
        print(f"⚠️ requeue_with_email_mutation failed: {e}", flush=True)
        try: conn.rollback()
        except Exception: pass
        raise
    finally:
        conn.close()


def normalize_card_corp_ids():
    """One-time heal (idempotent): retag any card whose corp_id matches a corporate only by
    CASE to the corporate's exact casing. Without this, exact-match joins — the claim's
    active-corp filter and the generator's per-corp portal-login lookup — miss a card tagged
    'streakads' when the corporate is 'STREAKADS', and the pool splits one corporate in two.
    Safe to run every tick: once healed it matches nothing. Returns rows changed."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE cards c
                   SET corp_id = co.corp_id
                  FROM corporates co
                 WHERE lower(c.corp_id) = lower(co.corp_id)
                   AND c.corp_id <> co.corp_id
            """)
            n = cur.rowcount
        conn.commit()
        return n
    except Exception as e:
        print(f"⚠️ normalize_card_corp_ids failed: {e}", flush=True)
        try: conn.rollback()
        except Exception: pass
        return 0
    finally:
        conn.close()


def card_bin_by_corp(limit=60):
    """Per corporate, per card-BIN outcomes — so you can see which corporate's BINs perform.
    [{corp_id, label, bin, total, success, declined, rate}] grouped by corporate then worst
    BIN first. Case-insensitive corp join so a corp isn't split by casing."""
    conn = _conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT corp_id, label, bin, total, success, declined
                  FROM (
                    SELECT COALESCE(co.corp_id, c.corp_id, '') AS corp_id,
                           co.label AS label,
                           LEFT(regexp_replace(COALESCE(c.card_no,''),'\\D','','g'),6) AS bin,
                           COUNT(*) AS total,
                           COUNT(*) FILTER (WHERE t.status=%s) AS success,
                           COUNT(*) FILTER (WHERE t.status=%s) AS declined
                      FROM tasks t
                      JOIN cards c        ON c.id = t.card_id
                      LEFT JOIN corporates co ON lower(co.corp_id) = lower(c.corp_id)
                     WHERE t.status IN (%s,%s,%s,%s,%s) AND c.card_no IS NOT NULL
                     GROUP BY COALESCE(co.corp_id, c.corp_id, ''), co.label,
                              LEFT(regexp_replace(COALESCE(c.card_no,''),'\\D','','g'),6)
                    HAVING COUNT(*) >= 1
                  ) x
                 WHERE LENGTH(bin) = 6
                 ORDER BY corp_id, success::numeric / NULLIF(total,0) ASC, total DESC
                 LIMIT %s
            """, (ST_COMPLETED, ST_DECLINED,
                  ST_COMPLETED, ST_FAILED, ST_DECLINED, ST_INELIGIBLE, ST_UNCONFIRMED, int(limit)))
            out = []
            for r in cur.fetchall():
                d = dict(r)
                d["corp_id"] = d["corp_id"] or ""
                d["label"] = d["label"] or (d["corp_id"] if d["corp_id"] else "Unassigned")
                d["rate"] = round(d["success"] / d["total"] * 100, 1) if d["total"] else 0.0
                out.append(d)
            return out
    except Exception:
        return []
    finally:
        conn.close()


def transactions_by_corp(campaign_id=None):
    """Per-corporate TRANSACTION counts — how many buys each corporate delivered. For the
    dashboard "which corp did how many transactions". Defaults to the ACTIVE campaign.
    completed = confirmed transactions; unconfirmed = awaiting confirmation; total = all
    attempts. Joins case-insensitively so a corp isn't split by casing."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            if campaign_id is None:
                cur.execute("SELECT id FROM campaigns WHERE status='active' ORDER BY id LIMIT 1")
                r = cur.fetchone()
                campaign_id = r[0] if r else None
            where, params = "", []
            if campaign_id:
                where = "WHERE t.campaign_id = %s"
                params = [int(campaign_id)]
            cur.execute(f"""
                SELECT COALESCE(co.corp_id, t.corp_id, '') AS corp_id, co.label,
                       count(*) FILTER (WHERE t.status='completed')   AS completed,
                       count(*) FILTER (WHERE t.status='unconfirmed') AS unconfirmed,
                       count(*) FILTER (WHERE t.status='running')     AS running,
                       count(*) AS total
                  FROM tasks t
                  LEFT JOIN corporates co ON lower(co.corp_id) = lower(t.corp_id)
                  {where}
                 GROUP BY COALESCE(co.corp_id, t.corp_id, ''), co.label
                 ORDER BY completed DESC, total DESC
            """, params)
            out = []
            for cid, label, comp, unc, run, tot in cur.fetchall():
                out.append({"corp_id": cid, "label": label or (cid if cid else "Unassigned"),
                            "completed": int(comp), "unconfirmed": int(unc),
                            "running": int(run), "total": int(tot)})
            return out
    except Exception:
        return []
    finally:
        conn.close()


def identity_pool():
    """Identity usage vs the 1M capacity headroom gauge (REVAMP_PLAN §5.2).

    capacity = first_names x last_names. This is a COMPUTED number, not a table:
    1,000 x 1,000 is the space we can draw from, not 1M rows we materialise.
    """
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM first_names")
            firsts = int(cur.fetchone()[0])
            cur.execute("SELECT count(*) FROM last_names")
            lasts = int(cur.fetchone()[0])
            cur.execute("SELECT status, count(*) FROM identities GROUP BY status")
            counts = {"unused": 0, "reserved": 0, "used": 0}
            for status, n in cur.fetchall():
                counts[status] = int(n)
            cur.execute("SELECT count(*) FROM emails WHERE status='active'")
            emails_active = int(cur.fetchone()[0])
            capacity = firsts * lasts
            materialised = sum(counts.values())
            return {
                "first_names": firsts, "last_names": lasts,
                "capacity": capacity,
                "materialised": materialised,
                "counts": counts,
                "emails_active": emails_active,
                "headroom_pct": round(materialised / capacity * 100, 2) if capacity else 0.0,
                "exhausted": bool(capacity and materialised >= capacity),
            }
    finally:
        conn.close()


def needs_review(limit=100):
    """The Needs Review queue (REVAMP_PLAN §6.4).

    Ambiguous outcomes hold their card in 'reserved' and the task in 'unconfirmed'.
    There is NO automatic resolver — recheck.py does not exist and is not being
    written — so this queue is the ONLY thing that unsticks a held card. If it
    grows unattended, cards leak out of the pool permanently.
    """
    conn = _conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT t.id AS task_id, t.status, t.updated_at, t.error, t.emp_id,
                       t.proxy_ip, t.transaction_id,
                       c.id AS card_id, c.card_no, c.status AS card_status,
                       COALESCE(t.updated_email, e.email) AS email,
                       i.first_name, i.last_name,
                       a.outcome, a.created_at AS attempt_at
                  FROM tasks t
                  LEFT JOIN cards      c ON c.id = t.card_id
                  LEFT JOIN identities i ON i.id = t.identity_id
                  LEFT JOIN emails     e ON e.id = i.email_id
                  LEFT JOIN LATERAL (
                      SELECT outcome, created_at FROM card_attempts
                       WHERE task_id = t.id ORDER BY id DESC LIMIT 1
                  ) a ON TRUE
                 WHERE t.status = %s OR (c.status = 'reserved' AND COALESCE(t.status,'') <> 'running')
                 ORDER BY t.updated_at DESC NULLS LAST
                 LIMIT %s
            """, (ST_UNCONFIRMED, int(limit)))
            out = []
            for r in cur.fetchall():
                d = dict(r)
                d["updated_at"] = d["updated_at"].strftime("%d %b %H:%M") if d["updated_at"] else ""
                d["attempt_at"] = d["attempt_at"].strftime("%d %b %H:%M") if d["attempt_at"] else ""
                cn = d.get("card_no") or ""
                d["card_masked"] = f"{cn[:4]}···{cn[-4:]}" if len(cn) >= 8 else (cn or "—")
                d["name"] = " ".join(x for x in [d.pop("first_name", None), d.pop("last_name", None)] if x)
                out.append(d)
            return out
    finally:
        conn.close()


def needs_review_count():
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT count(*) FROM tasks t
                LEFT JOIN cards c ON c.id = t.card_id
                WHERE t.status = %s OR (c.status = 'reserved' AND COALESCE(t.status,'') <> 'running')
            """, (ST_UNCONFIRMED,))
            return int(cur.fetchone()[0])
    finally:
        conn.close()


# ============================================================================
# Records browser — row-level datatables for the /records page. Lets the operator
# see "what I uploaded" (emails), "what got generated" (identities, cards) and the
# run history (transactions, reads). All optionally scoped to one campaign.
# ============================================================================

def _mask_card(cn):
    """BIN + last-4, middle hidden. Full PANs never enter the DOM or logs."""
    cn = (cn or "").strip()
    return f"{cn[:6]}······{cn[-4:]}" if len(cn) >= 10 else (cn or "—")


def _fmt_dt(v):
    return v.strftime("%d %b %Y %H:%M") if v else ""


def _campaign_clause(campaign_id, alias=""):
    """Return (sql_fragment, params) that filters by campaign when one is given."""
    if not campaign_id:
        return "", []
    col = f"{alias}.campaign_id" if alias else "campaign_id"
    return f" AND {col} = %s", [int(campaign_id)]


def _extra(date_col, status_col, date_from=None, date_to=None, status=None):
    """Optional date-range + status filters shared by every records datatable.

    date_from/date_to are 'YYYY-MM-DD'; date_to is inclusive of that whole day.
    Everything is parameterised (%s), so a bad value is a clean DB error, not
    an injection surface.
    """
    sql = ""
    params = []
    if date_from:
        sql += f" AND {date_col} >= %s::date"
        params.append(date_from)
    if date_to:
        sql += f" AND {date_col} < (%s::date + 1)"
        params.append(date_to)
    if status:
        sql += f" AND {status_col} = %s"
        params.append(status)
    return sql, params


def list_emails(campaign_id=None, limit=1000, date_from=None, date_to=None, status=None):
    """Uploaded email pool — 'kya upload kiya'."""
    where, params = _campaign_clause(campaign_id)
    ex, exp = _extra("created_at", "status", date_from, date_to, status)
    where += ex
    params += exp
    conn = _conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(f"""
                SELECT id, email, status, times_used, campaign_id, created_at
                  FROM emails
                 WHERE TRUE{where}
                 ORDER BY id DESC
                 LIMIT %s
            """, params + [int(limit)])
            out = []
            for r in cur.fetchall():
                d = dict(r)
                d["created_at"] = _fmt_dt(d["created_at"])
                out.append(d)
            return out
    finally:
        conn.close()


def list_identities(campaign_id=None, limit=1000, date_from=None, date_to=None, status=None):
    """Generated (first, last, email) triples — 'kya identity generate huyi'."""
    where, params = _campaign_clause(campaign_id, "i")
    ex, exp = _extra("i.created_at", "i.status", date_from, date_to, status)
    where += ex
    params += exp
    conn = _conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(f"""
                SELECT i.id, i.first_name, i.last_name, i.status,
                       e.email, i.campaign_id, i.created_at, i.used_at
                  FROM identities i
                  LEFT JOIN emails e ON e.id = i.email_id
                 WHERE TRUE{where}
                 ORDER BY i.id DESC
                 LIMIT %s
            """, params + [int(limit)])
            out = []
            for r in cur.fetchall():
                d = dict(r)
                d["name"] = " ".join(x for x in [d.get("first_name"), d.get("last_name")] if x)
                d["created_at"] = _fmt_dt(d["created_at"])
                d["used_at"] = _fmt_dt(d["used_at"])
                out.append(d)
            return out
    finally:
        conn.close()


def list_cards(campaign_id=None, limit=1000, date_from=None, date_to=None, status=None):
    """Generated cards — 'kya card generate huye'. These are the operator's own
    generated virtual cards, so full number + CVV are returned for verification
    and use; card_masked is kept for any UI that wants the short form."""
    where, params = _campaign_clause(campaign_id)
    ex, exp = _extra("generated_at", "status", date_from, date_to, status)
    where += ex
    params += exp
    conn = _conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(f"""
                SELECT id, card_no, cvv, expiry, status, max_amount, attempts,
                       campaign_id, corp_id, generated_at, used_at, error
                  FROM cards
                 WHERE TRUE{where}
                 ORDER BY id DESC
                 LIMIT %s
            """, params + [int(limit)])
            out = []
            for r in cur.fetchall():
                d = dict(r)
                d["card_masked"] = _mask_card(d.get("card_no"))
                d["max_amount"] = float(d["max_amount"]) if d["max_amount"] is not None else None
                d["generated_at"] = _fmt_dt(d["generated_at"])
                d["used_at"] = _fmt_dt(d["used_at"])
                out.append(d)
            return out
    finally:
        conn.close()


def list_transactions(campaign_id=None, emp_id=None, limit=1000,
                      date_from=None, date_to=None, status=None):
    """Buyer run history — card + identity + email + outcome per task."""
    where, params = _campaign_clause(campaign_id, "t")
    if emp_id:
        where += " AND t.emp_id = %s"
        params.append(emp_id)
    ex, exp = _extra("t.updated_at", "t.status", date_from, date_to, status)
    where += ex
    params += exp
    conn = _conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(f"""
                SELECT t.id, t.status, t.emp_id, t.transaction_id, t.proxy_ip,
                       t.duration_sec, t.error, t.updated_at,
                       c.card_no,
                       i.first_name, i.last_name,
                       COALESCE(t.updated_email, e.email) AS email,
                       t.campaign_id
                  FROM tasks t
                  LEFT JOIN cards      c ON c.id = t.card_id
                  LEFT JOIN identities i ON i.id = t.identity_id
                  LEFT JOIN emails     e ON e.id = i.email_id
                 WHERE TRUE{where}
                 ORDER BY t.id DESC
                 LIMIT %s
            """, params + [int(limit)])
            out = []
            for r in cur.fetchall():
                d = dict(r)
                d["card_masked"] = _mask_card(d.pop("card_no", None))
                d["name"] = " ".join(x for x in [d.pop("first_name", None), d.pop("last_name", None)] if x)
                d["duration_sec"] = float(d["duration_sec"]) if d["duration_sec"] is not None else None
                d["updated_at"] = _fmt_dt(d["updated_at"])
                out.append(d)
            return out
    finally:
        conn.close()


def list_reads(campaign_id=None, emp_id=None, limit=1000,
               date_from=None, date_to=None, status=None):
    """Reader run history. read_tasks has no campaign_id/emp_id column, so those
    filters are applied via the source transaction. Date range is on read_at
    (falling back to updated_at)."""
    conn = _conn()
    params = []
    conds = []
    join = ""
    if campaign_id or emp_id:
        join = " JOIN tasks t ON t.id = r.source_task_id"
        if campaign_id:
            conds.append("t.campaign_id = %s")
            params.append(int(campaign_id))
        if emp_id:
            conds.append("t.emp_id = %s")
            params.append(emp_id)
    if date_from:
        conds.append("COALESCE(r.read_at, r.updated_at) >= %s::date")
        params.append(date_from)
    if date_to:
        conds.append("COALESCE(r.read_at, r.updated_at) < (%s::date + 1)")
        params.append(date_to)
    if status:
        conds.append("r.status = %s")
        params.append(status)
    where = (" WHERE " + " AND ".join(conds)) if conds else ""
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(f"""
                SELECT r.id, r.email, r.password, r.name_used, r.status, r.books_read,
                       r.transaction_id, r.duration_sec, r.error,
                       r.transaction_at, r.read_at, r.updated_at,
                       r.source_task_id, r.proof_shot, r.proof_node
                  FROM read_tasks r{join}{where}
                 ORDER BY r.id DESC
                 LIMIT %s
            """, params + [int(limit)])
            out = []
            for r in cur.fetchall():
                d = dict(r)
                d["duration_sec"] = float(d["duration_sec"]) if d["duration_sec"] is not None else None
                d["transaction_at"] = _fmt_dt(d["transaction_at"])
                d["read_at"] = _fmt_dt(d["read_at"])
                d["updated_at"] = _fmt_dt(d["updated_at"])
                out.append(d)
            return out
    finally:
        conn.close()


# --- By-Campaign drill-down (campaign ▸ employee ▸ daily) --------------------
# "Failed" for a buyer task groups the three hard-outcome statuses; 'unconfirmed'
# is Needs-Review, counted separately so it isn't mistaken for a clean failure.
_TX_FAILED = ("failed", "declined", "ineligible")


def _fmt_day(iso):
    try:
        import datetime as _dt
        return _dt.datetime.strptime(iso, "%Y-%m-%d").strftime("%d %b %Y")
    except Exception:
        return iso or ""


def campaign_records_summary():
    """Every campaign with the aggregates the drill-down's top row shows."""
    conn = _conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            _autoclose_expired(cur)
            conn.commit()
            cur.execute("""
                SELECT c.id, c.name, c.budget, c.status, c.start_date,
                       (SELECT count(*) FROM emails e WHERE e.campaign_id=c.id) AS emails,
                       (SELECT count(*) FROM identities i WHERE i.campaign_id=c.id) AS identities,
                       (SELECT count(*) FROM cards cd WHERE cd.campaign_id=c.id) AS cards,
                       (SELECT count(*) FROM cards cd
                         WHERE cd.campaign_id=c.id AND cd.card_no IS NOT NULL) AS cards_filled,
                       (SELECT count(*) FROM tasks t
                         WHERE t.campaign_id=c.id AND t.status<>'pending') AS txns,
                       (SELECT count(*) FROM tasks t
                         WHERE t.campaign_id=c.id AND t.status='completed') AS completed,
                       (SELECT count(*) FROM read_tasks r JOIN tasks t ON t.id=r.source_task_id
                         WHERE t.campaign_id=c.id AND r.status='done') AS reads_done
                  FROM campaigns c
                 ORDER BY c.start_date DESC, c.id DESC
            """)
            out = []
            for r in cur.fetchall():
                d = dict(r)
                d["budget"] = int(d["budget"] or 0)
                for k in ("emails", "identities", "cards", "cards_filled",
                          "txns", "completed", "reads_done"):
                    d[k] = int(d[k] or 0)
                d["success_rate"] = round(d["completed"] / d["txns"] * 100, 1) if d["txns"] else 0.0
                d["month"] = d["start_date"].strftime("%b %Y") if d["start_date"] else ""
                d["label"] = f"{d['name']} · {d['month']}" if d["month"] else d["name"]
                d.pop("start_date", None)
                out.append(d)
            return out
    finally:
        conn.close()


def campaign_employee_breakdown(campaign_id):
    """Per-employee (emp_id) performance inside one campaign.

    OTP failure counters come from otp_alerts, which is GLOBAL per emp_id (not
    campaign-scoped) — it is the employee's live OTP health, shown here as a
    heads-up, not a per-campaign number.
    """
    cid = int(campaign_id)
    conn = _conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT t.emp_id,
                       count(*) FILTER (WHERE t.status <> 'pending') AS txns,
                       count(*) FILTER (WHERE t.status = 'completed') AS completed,
                       count(*) FILTER (WHERE t.status IN ('failed','declined','ineligible')) AS failed,
                       count(*) FILTER (WHERE t.status = 'unconfirmed') AS review
                  FROM tasks t
                 WHERE t.campaign_id = %s AND t.emp_id IS NOT NULL
                 GROUP BY t.emp_id
            """, (cid,))
            rows = {r["emp_id"]: dict(r) for r in cur.fetchall()}
            cur.execute("""
                SELECT t.emp_id,
                       count(*) FILTER (WHERE r.status='done') AS reads_done,
                       count(*) AS reads_total
                  FROM read_tasks r JOIN tasks t ON t.id = r.source_task_id
                 WHERE t.campaign_id = %s AND t.emp_id IS NOT NULL
                 GROUP BY t.emp_id
            """, (cid,))
            for r in cur.fetchall():
                d = rows.setdefault(r["emp_id"], {"emp_id": r["emp_id"]})
                d["reads_done"] = int(r["reads_done"] or 0)
                d["reads_total"] = int(r["reads_total"] or 0)
            cur.execute("SELECT emp_id, consecutive_failures, total_failures FROM otp_alerts")
            otp = {r["emp_id"]: dict(r) for r in cur.fetchall()}
            out = []
            for emp, d in rows.items():
                for k in ("txns", "completed", "failed", "review", "reads_done", "reads_total"):
                    d[k] = int(d.get(k) or 0)
                o = otp.get(emp) or {}
                d["otp_fail_streak"] = int(o.get("consecutive_failures") or 0)
                d["otp_fail_total"] = int(o.get("total_failures") or 0)
                d["success_rate"] = round(d["completed"] / d["txns"] * 100, 1) if d["txns"] else 0.0
                out.append(d)
            out.sort(key=lambda x: x["txns"], reverse=True)
            return out
    finally:
        conn.close()


def campaign_employee_daily(campaign_id, emp_id, date_from=None, date_to=None):
    """Per-day transaction + read totals for one employee in one campaign."""
    cid = int(campaign_id)
    tx_f, tx_p = _extra("t.updated_at", None, date_from, date_to, None)
    rd_f, rd_p = _extra("COALESCE(r.read_at, r.updated_at)", None, date_from, date_to, None)
    conn = _conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            days = {}
            cur.execute(f"""
                SELECT to_char(date_trunc('day', t.updated_at),'YYYY-MM-DD') AS iso,
                       count(*) FILTER (WHERE t.status <> 'pending') AS txns,
                       count(*) FILTER (WHERE t.status = 'completed') AS completed,
                       count(*) FILTER (WHERE t.status IN ('failed','declined','ineligible')) AS failed
                  FROM tasks t
                 WHERE t.campaign_id = %s AND t.emp_id = %s AND t.updated_at IS NOT NULL{tx_f}
                 GROUP BY 1
            """, [cid, emp_id] + tx_p)
            for r in cur.fetchall():
                days[r["iso"]] = {"iso": r["iso"], "txns": int(r["txns"]),
                                  "completed": int(r["completed"]), "failed": int(r["failed"]),
                                  "reads_done": 0, "books": 0}
            cur.execute(f"""
                SELECT to_char(date_trunc('day', COALESCE(r.read_at, r.updated_at)),'YYYY-MM-DD') AS iso,
                       count(*) FILTER (WHERE r.status='done') AS reads_done,
                       COALESCE(sum(r.books_read),0) AS books
                  FROM read_tasks r JOIN tasks t ON t.id = r.source_task_id
                 WHERE t.campaign_id = %s AND t.emp_id = %s{rd_f}
                 GROUP BY 1
            """, [cid, emp_id] + rd_p)
            for r in cur.fetchall():
                d = days.setdefault(r["iso"], {"iso": r["iso"], "txns": 0, "completed": 0,
                                               "failed": 0, "reads_done": 0, "books": 0})
                d["reads_done"] = int(r["reads_done"] or 0)
                d["books"] = int(r["books"] or 0)
            out = sorted(days.values(), key=lambda x: x["iso"], reverse=True)
            for d in out:
                d["date"] = _fmt_day(d["iso"])
            return out
    finally:
        conn.close()


def resolve_review(task_id, decision):
    """Human resolution of an ambiguous outcome (REVAMP_PLAN §6.4).

    confirm -> the charge DID go through: card 'used', task 'completed'
    reject  -> it did NOT: card back to 'unused' (retryable), task 'failed'

    Single transaction: a half-applied decision would either strand the card or
    double-count the transaction. Returns True if a row actually changed.
    """
    if decision not in ("confirm", "reject"):
        raise ValueError(f"decision must be confirm|reject, got {decision!r}")
    card_status = "0000000000000000" if decision == "confirm" else "unused"
    task_status = ST_COMPLETED if decision == "confirm" else ST_FAILED
    conn = _conn()
    try:
        with conn.cursor() as cur:
            # Guarded on the CURRENT status so two operators clicking at once can't
            # both apply — the second finds nothing to update.
            cur.execute("""
                UPDATE tasks SET status=%s, updated_at=now(),
                                 error = CASE WHEN %s='reject'
                                              THEN 'Rejected in Needs Review' ELSE error END
                 WHERE id=%s AND status=%s
             RETURNING card_id
            """, (task_status, decision, int(task_id), ST_UNCONFIRMED))
            row = cur.fetchone()
            if not row:
                conn.rollback()
                return False
            card_id = row[0]
            if card_id:
                cur.execute("""
                    UPDATE cards
                       SET status=%s, updated_at=now(),
                           used_at = CASE WHEN %s='used' THEN now() ELSE used_at END
                     WHERE id=%s AND status='reserved'
                """, (card_status, card_status, card_id))
                cur.execute("""
                    INSERT INTO card_attempts (card_id, task_id, outcome, error)
                    VALUES (%s, %s, %s, %s)
                """, (card_id, int(task_id),
                      "success" if decision == "confirm" else "soft_fail",
                      f"Manually {decision}ed in Needs Review"))
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ================= GLOBAL PAUSE (operator kill-switch) =================

def is_paused():
    """True if the operator has globally PAUSED the bots. Each bot polls this before
    claiming the next task: paused => finish the current task, then wait instead of
    claiming. Fail-safe: any DB hiccup returns False so a transient error never silently
    halts the fleet."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT paused FROM system_state WHERE id = 1")
            r = cur.fetchone()
            return bool(r and r[0])
    except Exception:
        return False
    finally:
        conn.close()


def set_paused(paused, note=None):
    """Flip the global pause switch. Returns True on success."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO system_state (id, paused, note, updated_at)
                     VALUES (1, %s, %s, now())
                ON CONFLICT (id) DO UPDATE
                   SET paused = EXCLUDED.paused, note = EXCLUDED.note, updated_at = now()
            """, (bool(paused), note))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()


def is_reader_sync_paused():
    """True if the operator has STOPPED the reader (readfile) sheet↔DB sync from the
    dashboard. The reader promoter checks this: when on, it stops promoting
    sheet into read_tasks (so the DB stops being re-filled from the sheet) — the buyer
    Tasks sync keeps running. Fail-safe: any DB hiccup returns False."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT reader_sync_paused FROM system_state WHERE id = 1")
            r = cur.fetchone()
            return bool(r and r[0])
    except Exception:
        return False
    finally:
        conn.close()


def set_reader_sync_paused(paused, note=None):
    """Flip the reader-sync stop switch. Returns True on success."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO system_state (id, reader_sync_paused, note, updated_at)
                     VALUES (1, %s, %s, now())
                ON CONFLICT (id) DO UPDATE
                   SET reader_sync_paused = EXCLUDED.reader_sync_paused,
                       note = EXCLUDED.note, updated_at = now()
            """, (bool(paused), note))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()


def system_state():
    """{paused, reader_sync_paused, note, updated_at} for the dashboard banners."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT paused, note, updated_at, reader_sync_paused FROM system_state WHERE id = 1")
            r = cur.fetchone()
            if not r:
                return {"paused": False, "reader_sync_paused": False, "note": None, "updated_at": None}
            return {"paused": bool(r[0]), "note": r[1],
                    "updated_at": r[2].strftime("%Y-%m-%d %H:%M:%S") if r[2] else None,
                    "reader_sync_paused": bool(r[3])}
    except Exception:
        return {"paused": False, "reader_sync_paused": False, "note": None, "updated_at": None}
    finally:
        conn.close()


# ================= OTP AUTO-COOLDOWN + BACKUP SHIFT =================

def cooldown_and_reassign():
    """When an employee's OTPs stop arriving (>= OTP_COOLDOWN_THRESHOLD CONSECUTIVE failures)
    it is 'dying' — move its PENDING (not-yet-run) tasks onto a HEALTHY employee so the work
    flows to a live account instead of burning on a dead one. The corporate stays the same;
    only the employee id changes.

    CORP-WISE (default, when you use the Corporates page): the replacement is another ACTIVE
    employee OF THE SAME CORPORATE (from corp_employees) — the least-loaded one. So you do NOT
    keep a separate backup list: just add 2-3 employees to each corporate on the Corporates
    page, and if one dies its pending work auto-shifts to the corp's other employees.

    LEGACY fallback (only when NO corporates are configured): a flat reserve list from
    config.json  ->  BACKUP_EMPLOYEES: ["EMP999","EMP888"].

    Config (read live from config.json):
       OTP_COOLDOWN_ENABLED   (default true)
       OTP_COOLDOWN_THRESHOLD (default 5 consecutive OTP fails)
    Reassigned rows are flagged reassigned=TRUE. Returns [{corp_id?, from_emp, to_emp, moved}];
    safe no-op when disabled / none dying / no healthy replacement."""
    cfg = _load_config()
    if str(cfg.get("OTP_COOLDOWN_ENABLED", True)).lower() in ("0", "false", "no", "off"):
        return []
    try:
        threshold = max(2, int(cfg.get("OTP_COOLDOWN_THRESHOLD", 5)))
    except Exception:
        threshold = 5
    conn = _conn()
    out = []
    try:
        with conn.cursor() as cur:
            # the dying set: every emp at/over the consecutive-OTP-fail threshold
            cur.execute("SELECT emp_id FROM otp_alerts WHERE consecutive_failures >= %s", (threshold,))
            dying = [r[0] for r in cur.fetchall()]
            if not dying:
                return []
            # corp-wise mode = the Corporates page is in use (corp_employees has rows)
            cur.execute("SELECT count(*) FROM corp_employees")
            corp_mode = int(cur.fetchone()[0]) > 0

            if corp_mode:
                # dying emps' pending work, split by corporate (an emp usually maps to one corp)
                cur.execute("""
                    SELECT COALESCE(corp_id,''), emp_id, count(*)
                      FROM tasks
                     WHERE status = %s AND emp_id = ANY(%s)
                     GROUP BY COALESCE(corp_id,''), emp_id
                """, (ST_PENDING, dying))
                for corp_id, demp, pend in cur.fetchall():
                    if not pend:
                        continue
                    # replacement = least-loaded ACTIVE, non-dying employee of THIS corporate
                    cur.execute("""
                        SELECT ce.emp_id,
                               (SELECT count(*) FROM tasks t
                                 WHERE t.emp_id = ce.emp_id AND t.status = %s) AS load
                          FROM corp_employees ce
                         WHERE ce.corp_id = %s AND ce.active = TRUE
                           AND ce.emp_id <> %s AND NOT (ce.emp_id = ANY(%s))
                         ORDER BY load ASC, ce.emp_id
                         LIMIT 1
                    """, (ST_PENDING, corp_id, demp, dying))
                    tr = cur.fetchone()
                    if not tr:
                        print(f"⚠️ cooldown: corp {corp_id or '—'} has no healthy employee left "
                              f"for dying {demp} ({pend} pending stuck) — add more employees to "
                              f"this corporate on the Corporates page", flush=True)
                        continue
                    target = tr[0]
                    cur.execute("""
                        UPDATE tasks SET emp_id = %s, reassigned = TRUE, updated_at = now()
                         WHERE status = %s AND emp_id = %s AND COALESCE(corp_id,'') = %s
                    """, (target, ST_PENDING, demp, corp_id))
                    moved = cur.rowcount
                    out.append({"corp_id": corp_id, "from_emp": demp, "to_emp": target, "moved": moved})
                    print(f"🔁 OTP cooldown (corp {corp_id or '—'}): {demp} dying — moved {moved} "
                          f"pending → {target} (same corporate)", flush=True)
            else:
                # LEGACY: flat BACKUP_EMPLOYEES reserve list (no corporates configured)
                norm = []
                for b in (cfg.get("BACKUP_EMPLOYEES") or []):
                    if isinstance(b, str) and b.strip():
                        norm.append(b.strip())
                    elif isinstance(b, dict) and b.get("emp_id"):
                        norm.append(str(b["emp_id"]).strip())
                if not norm:
                    return []
                cur.execute("""
                    SELECT a.emp_id,
                           (SELECT COUNT(*) FROM tasks t
                             WHERE t.emp_id = a.emp_id AND t.status = %s) AS pend
                      FROM otp_alerts a
                     WHERE a.consecutive_failures >= %s
                     ORDER BY a.consecutive_failures DESC
                """, (ST_PENDING, threshold))
                dyingp = [(r[0], int(r[1])) for r in cur.fetchall() if int(r[1]) > 0]
                cur.execute("SELECT DISTINCT emp_id FROM tasks WHERE emp_id IS NOT NULL")
                used = {r[0] for r in cur.fetchall()}
                free = [e for e in norm if e not in used]
                i = 0
                for emp, pend in dyingp:
                    if i >= len(free):
                        print(f"⚠️ cooldown: NO free backup emp for dying emp {emp} "
                              f"({pend} pending stuck) — add more BACKUP_EMPLOYEES", flush=True)
                        break
                    bk = free[i]; i += 1
                    cur.execute("""
                        UPDATE tasks SET emp_id = %s, reassigned = TRUE, updated_at = now()
                         WHERE emp_id = %s AND status = %s
                    """, (bk, emp, ST_PENDING))
                    moved = cur.rowcount
                    out.append({"from_emp": emp, "to_emp": bk, "moved": moved})
                    print(f"🔁 OTP cooldown: emp {emp} dying — moved {moved} pending "
                          f"→ backup emp {bk} (corp unchanged)", flush=True)
        conn.commit()
        return out
    except Exception as e:
        try: conn.rollback()
        except Exception: pass
        print(f"⚠️ cooldown_and_reassign error: {e}", flush=True)
        return []
    finally:
        conn.close()


def cooldown_status():
    """Live status of OTP auto-cooldown for the dashboard: is it on, the threshold, the
    backup pool (total/used/free), which employees are currently DYING (>= threshold
    consecutive OTP fails), and where reassigned work has gone. So the operator can SEE
    the cooldown working without grepping logs."""
    cfg = _load_config()
    enabled = str(cfg.get("OTP_COOLDOWN_ENABLED", True)).lower() not in ("0", "false", "no", "off")
    try:
        threshold = max(2, int(cfg.get("OTP_COOLDOWN_THRESHOLD", 5)))
    except Exception:
        threshold = 5
    backups = []
    for b in (cfg.get("BACKUP_EMPLOYEES") or []):
        if isinstance(b, str) and b.strip():
            backups.append(b.strip())
        elif isinstance(b, dict) and b.get("emp_id"):
            backups.append(str(b["emp_id"]).strip())
    base = {"enabled": enabled, "threshold": threshold, "backups_total": len(backups),
            "backups_used": 0, "backups_free": len(backups), "dying": [], "reassigned": []}
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT DISTINCT emp_id FROM tasks WHERE emp_id IS NOT NULL")
            used = {r[0] for r in cur.fetchall()}
            cur.execute("""SELECT emp_id, consecutive_failures FROM otp_alerts
                            WHERE consecutive_failures >= %s
                            ORDER BY consecutive_failures DESC LIMIT 20""", (threshold,))
            base["dying"] = [{"emp_id": r[0], "consecutive": int(r[1])} for r in cur.fetchall()]
            cur.execute("""SELECT emp_id, COUNT(*) total,
                                  COUNT(*) FILTER (WHERE status=%s) pending,
                                  COUNT(*) FILTER (WHERE status=%s) success
                             FROM tasks WHERE reassigned = TRUE
                            GROUP BY emp_id ORDER BY total DESC LIMIT 20""",
                        (ST_PENDING, ST_COMPLETED))
            base["reassigned"] = [{"emp_id": r[0], "total": int(r[1]),
                                   "pending": int(r[2]), "success": int(r[3])}
                                  for r in cur.fetchall()]
        base["backups_used"] = len([b for b in backups if b in used])
        base["backups_free"] = len([b for b in backups if b not in used])
        return base
    except Exception:
        return base
    finally:
        conn.close()


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
    """Clean a possibly-messy email so we NEVER pass an invalid one forward: trim, lowercase,
    drop internal spaces, collapse/strip stray dots, and fix common domain typos
    (gmail.con -> gmail.com etc.). Returns a VALID email, or None if unsalvageable."""
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
    """A RANDOM valid alternative for an email that came back 'not eligible' (account
    exists). No '+tag' (Magzter rejects those). Each call picks a RANDOM strategy and
    RANDOM position — never the same pattern: dot at a random spot, append/insert a random
    digit, provider swap, or a combo. Always returns a VALID email not already in `tried`,
    or None if it can't find a fresh one. Pass the set of already-tried emails to avoid
    repeats."""
    clean = sanitize_email(original)
    if not clean:
        return None
    if isinstance(tried, int):            # back-compat: old idx arg -> ignore
        tried = None
    tried = set(tried or ())
    tried.add(clean)
    local, domain = clean.split("@", 1)
    base = re.sub(r"[.]", "", local)      # dot-free base
    domains = ["gmail.com", "outlook.com", "hotmail.com", "yahoo.com"]
    for _ in range(40):                   # try random strategies until a fresh valid one
        b, d = base, domain
        s = random.randint(0, 4)
        if s == 0 and len(b) > 1:                          # dot at a RANDOM position
            p = random.randint(1, len(b) - 1); cl = b[:p] + "." + b[p:]
        elif s == 1:                                       # append 1-2 random digits
            cl = b + str(random.randint(1, 99))
        elif s == 2 and len(b) > 1:                        # insert a random digit randomly
            p = random.randint(1, len(b)); cl = b[:p] + str(random.randint(0, 9)) + b[p:]
        elif s == 3:                                       # swap provider
            cl = b; d = random.choice([x for x in domains if x != domain])
        else:                                              # dot + digit combo
            p = random.randint(1, max(1, len(b) - 1))
            cl = b[:p] + "." + b[p:] + str(random.randint(1, 9))
        cand = f"{cl}@{d}"
        if cand != clean and cand not in tried and _EMAIL_RE.match(cand):
            return cand
    return None


def set_updated_email(task_id, email, attempts=None):
    """Record the email that was actually USED (after in-session mutation) in the separate
    `updated_email` column — the original `email` is never touched. Surfaces in the sheet's
    Updated_Email column too. Best-effort."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            if attempts is None:
                cur.execute("UPDATE tasks SET updated_email=%s WHERE id=%s",
                            (email, task_id))
            else:
                cur.execute("UPDATE tasks SET updated_email=%s, email_attempts=%s WHERE id=%s",
                            (email, int(attempts), task_id))
        conn.commit()
        return True
    except Exception:
        try: conn.rollback()
        except Exception: pass
        return False
    finally:
        conn.close()


def requeue_email_mutation(task_id, original_email):
    """A 'not eligible' row: try the NEXT mutated email and re-queue it as pending so a
    buyer retries with it. The ORIGINAL email stays untouched in `email`; the mutated one
    goes in `updated_email` (separate column — nothing overwritten). Returns the new email,
    or None when mutations are exhausted (caller then finalizes the row as INELIGIBLE)."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            # email moved off `tasks` to identities (migration 0003). Read the mutated
            # address if one exists, else the canonical identity email — NOT `tasks.email`
            # (dropped). The old query referenced that dead column and always failed.
            cur.execute("""
                SELECT COALESCE(t.email_attempts, 0),
                       COALESCE(t.updated_email, e.email)
                  FROM tasks t
                  LEFT JOIN identities i ON i.id = t.identity_id
                  LEFT JOIN emails e     ON e.id = i.email_id
                 WHERE t.id = %s
            """, (task_id,))
            row = cur.fetchone()
            if not row:
                return None
            attempt = int(row[0]); orig = original_email or row[1]
            cand = mutate_email(orig, attempt)
            if not cand:
                return None
            cur.execute("""
                UPDATE tasks
                   SET updated_email = %s, email_attempts = %s, status = %s,
                       ran_by = NULL, claimed_at = NULL,
                       error = %s, updated_at = now()
                 WHERE id = %s AND status = %s
            """, (cand, attempt + 1, ST_PENDING,
                  f"Email mutation #{attempt+1}: {orig} -> {cand}", task_id, ST_RUNNING))
            ok = cur.rowcount > 0
        conn.commit()
        return cand if ok else None
    except Exception:
        try: conn.rollback()
        except Exception: pass
        return None
    finally:
        conn.close()


# ================= CLAIMING (bot side) =================

def _claimable_exists(cur, me, ipe):
    """True if some pending emp is NOT yet at its instance capacity. An emp is 'full'
    when >= ipe DISTINCT OTHER instances are already running it (ipe=1 => locked to one
    instance, the original behaviour)."""
    cur.execute("""
        SELECT 1 FROM tasks
        WHERE status = %s
          AND emp_id NOT IN (
              SELECT emp_id FROM tasks
              WHERE status = %s AND ran_by IS DISTINCT FROM %s
              GROUP BY emp_id HAVING COUNT(DISTINCT ran_by) >= %s
          )
        LIMIT 1
    """, (ST_PENDING, ST_RUNNING, me, int(ipe)))
    return cur.fetchone() is not None


def _try_claim(conn, me, ipe):
    """One atomic claim attempt. Up to `ipe` instances may share an employee (aws
    INSTANCES_PER_EMP). Each call grabs a SLICE (~pending/ipe rows) of the next
    not-full emp via FOR UPDATE SKIP LOCKED so concurrent claimers never collide.
    Per-employee OTP safety is handled at run time by db.otp_lock + card_last_four."""
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        # 1) Resume MY OWN interrupted rows first (left 'running' by me after a crash).
        cur.execute("""
            SELECT emp_id FROM tasks
            WHERE status = %s AND ran_by = %s
            ORDER BY emp_id LIMIT 1
        """, (ST_RUNNING, me))
        own = cur.fetchone()
        if own:
            cur.execute("""
                SELECT * FROM tasks
                WHERE status = %s AND ran_by = %s AND emp_id = %s
                ORDER BY id
            """, (ST_RUNNING, me, own["emp_id"]))
            rows = cur.fetchall()
            conn.commit()
            return rows

        # 2) Claim a SMALL slice of the next emp that is NOT at capacity (< ipe other
        #    instances). LIMIT = min(ceil(pending/ipe), CLAIM_BATCH) — capped small so an
        #    instance never hogs (and never orphans on crash) a big chunk of rows. The IPE
        #    cap (≤ipe distinct instances per emp) still holds via the HAVING above; this
        #    just makes each grab tiny so work spreads and a crash loses ≤CLAIM_BATCH rows.
        # DEFER RETRIES (user rule: "jab sab run ho jaye then retry wale"): while ANY
        # fresh (never-retried) pending row exists, retried rows (retries>0) are held
        # back so every account gets its first attempt before any second attempt runs.
        # Retries flow automatically once no fresh work is left. Env DEFER_RETRIES=0
        # restores the old interleaved order (fail-safe revert without a code change).
        defer_retries = os.environ.get("DEFER_RETRIES", "1") == "1"
        cur.execute("""
            WITH fresh AS (
                -- is there any never-retried (fresh) pending row anywhere right now?
                SELECT EXISTS(
                    SELECT 1 FROM tasks WHERE status = %(p)s AND COALESCE(retries,0) = 0
                ) AS has_fresh
            ),
            load AS (
                -- how many distinct instances are CURRENTLY working each employee
                SELECT emp_id, COUNT(DISTINCT ran_by) AS insts
                  FROM tasks WHERE status = %(r)s GROUP BY emp_id
            ),
            pick AS (
                -- the LEAST-LOADED employee that still has pending rows and is not at the
                -- ipe cap. Least-loaded first => instances spread EVENLY across employees,
                -- and a freed instance joins whoever is busiest-with-fewest-helpers — so no
                -- instance sits idle while another employee is buried in pending rows.
                SELECT t.emp_id
                  FROM tasks t
                  LEFT JOIN load l ON l.emp_id = t.emp_id
                 WHERE t.status = %(p)s
                   -- hold retries until no fresh work remains (see DEFER RETRIES above)
                   AND ( NOT %(defer)s
                         OR COALESCE(t.retries,0) = 0
                         OR NOT (SELECT has_fresh FROM fresh) )
                   AND t.emp_id NOT IN (
                       SELECT emp_id FROM tasks
                        WHERE status = %(r)s AND ran_by IS DISTINCT FROM %(me)s
                        GROUP BY emp_id HAVING COUNT(DISTINCT ran_by) >= %(ipe)s
                   )
                 GROUP BY t.emp_id, l.insts
                 ORDER BY COALESCE(l.insts, 0) ASC, t.emp_id
                 LIMIT 1
            )
            UPDATE tasks
               SET status = %(r)s, ran_by = %(me)s, claimed_at = now(),
                   updated_at = now()
             WHERE id IN (
                   SELECT id FROM tasks
                    WHERE status = %(p)s AND emp_id = (SELECT emp_id FROM pick)
                      AND ( NOT %(defer)s
                            OR COALESCE(retries,0) = 0
                            OR NOT (SELECT has_fresh FROM fresh) )
                    ORDER BY COALESCE(retries,0), id   -- fresh before retried, then oldest
                    FOR UPDATE SKIP LOCKED
                    LIMIT %(batch)s
             )
         RETURNING *
        """, {"p": ST_PENDING, "r": ST_RUNNING, "me": me, "ipe": int(ipe),
              "batch": CLAIM_BATCH, "defer": defer_retries})
        rows = cur.fetchall()
        conn.commit()
        return rows


def buyer_daily_cap_reached():
    """Auto-pause the buyer when today's plan is met (REVAMP: editable daily target).

    True if the active campaign has already CLAIMED >= today's planned target for
    today. Lets the operator lower today's plan (e.g. 500 -> 100) and have the buyer
    stop claiming once 100 are reached — it resumes automatically when the target is
    raised or the day rolls over. Fail-safe: any error, no active campaign, or a
    non-positive planned value returns False so the fleet is never blocked.
    """
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM campaigns WHERE status='active' ORDER BY id DESC LIMIT 1")
            row = cur.fetchone()
            if not row:
                return False
            cid = int(row[0])
            cur.execute("SELECT planned FROM campaign_days WHERE campaign_id=%s AND day=CURRENT_DATE", (cid,))
            pr = cur.fetchone()
            if not pr:
                return False
            planned = int(pr[0] or 0)
            if planned <= 0:                 # 0 = no per-day cap set (don't surprise-stop)
                return False
            cur.execute("SELECT count(*) FROM tasks WHERE campaign_id=%s AND claimed_at::date=CURRENT_DATE", (cid,))
            claimed_today = int(cur.fetchone()[0])
            return claimed_today >= planned
    except Exception:
        return False
    finally:
        conn.close()


def claim_next_group(instance_id, attempts=25, instances_per_emp=1):
    """Claim a small batch of work for this instance.
      instances_per_emp = N  -> at most N distinct instances may work one employee.
      instances_per_emp = 0  -> UNLIMITED: ANY number of instances can pile onto a single
                                employee, so even ONE employee keeps all 50 instances busy
                                (the OTP window still serializes per-emp via db.otp_lock +
                                card_last_four, so OTP stays correct — only that step
                                queues; the slow browser work runs fully in parallel).
    Returns task dicts, or None when no claimable work is left for this instance."""
    # Editable daily-target auto-pause: once today's plan is met, claim nothing more
    # (the buyer idles) until the target is raised or the day rolls over. Opt-out with
    # AUTO_DAILY_CAP=0. Fail-safe helper => a DB hiccup never pauses the fleet.
    if os.environ.get("AUTO_DAILY_CAP", "1") == "1" and buyer_daily_cap_reached():
        return None
    me = int(instance_id)
    _ipe = int(instances_per_emp)
    ipe = 10**9 if _ipe <= 0 else max(1, _ipe)   # 0 => unlimited (no per-emp cap)
    conn = _conn()
    try:
        for _ in range(attempts):
            rows = _try_claim(conn, me, ipe)
            if rows:
                _enrich_claimed(conn, rows)      # runtime engine: JOIN card+identity+email
                return [_to_task(r) for r in rows]
            with conn.cursor() as cur:
                if not _claimable_exists(cur, me, ipe):
                    conn.commit()
                    return None
            conn.commit()
            time.sleep(1.5)             # lost a race this round — retry
        return None
    finally:
        conn.close()


# ================= STATUS WRITE (bot side) =================

def update_task_step(task_id, step):
    """Record the STEP a running task just entered (+ timestamp). Best-effort: a failure
    here must never break the bot. The dashboard reads step + step_at to show which
    instance is on which step and for how long (spot stuck tasks)."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE tasks SET step=%s, step_at=now() WHERE id=%s",
                        (str(step)[:40], task_id))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()


def update_task(task_id, status, name_used="", proxy_ip="", duration_sec=None,
                error="", transaction_id=None):
    """Write a task's result back to the DB and flag it for sheet writeback.

    A FINAL status (anything other than 'running') is only written if the row is
    STILL 'running' — so a finished row can never be overwritten. This protects
    against a duplicate bot (instance-id collision) clobbering an already-completed
    task and making the 'done' count go DOWN. Returns False if the guard blocked it
    (the row was already finalized by someone else)."""
    dur = (str(duration_sec) if duration_sec is not None else None)
    err = str(error)[:500]
    conn = _conn()
    try:
        with conn.cursor() as cur:
            if status == ST_RUNNING:
                guard, extra = "", ()        # marking running (claim already did) — no guard
            else:
                guard, extra = " AND status = %s", (ST_RUNNING,)
            cur.execute(f"""
                UPDATE tasks
                   SET status = %s,
                       name_used = COALESCE(NULLIF(%s,''), name_used),
                       proxy_ip  = COALESCE(NULLIF(%s,''), proxy_ip),
                       duration_sec = COALESCE(%s, duration_sec),
                       error = %s,
                       transaction_id = COALESCE(%s, transaction_id),
                       updated_at = now()
                 WHERE id = %s{guard}
            """, (status, name_used, proxy_ip, dur, err, transaction_id, task_id) + extra)
            changed = cur.rowcount
            # CARD ACCOUNTING (so the dashboard shows used vs waste): a COMPLETED buy
            # consumed its card -> mark it 'used'. This is the ONLY place a normal success
            # flips the card (previously it stayed 'reserved' forever, so nothing ever read
            # as 'used'). Guard on <>'used' keeps it idempotent.
            if changed and status == ST_COMPLETED:
                cur.execute("""
                    UPDATE cards SET status='used', updated_at=now()
                     WHERE id = (SELECT card_id FROM tasks WHERE id=%s)
                       AND status <> 'used'
                """, (task_id,))
        conn.commit()
        if changed == 0 and status != ST_RUNNING:
            print(f"   ⚠️ update_task: row {task_id} was already finalized by another "
                  f"process — skipped (instance-id collision?)", flush=True)
        return changed > 0
    except Exception as e:
        print(f"❌ DB update_task failed: {e}", flush=True)
        return False
    finally:
        conn.close()


# ================= ETA helper (bot side) =================

def count_pending():
    """(pending_rows, pending_groups) across the whole table — for the rough ETA."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*) , COUNT(DISTINCT emp_id)
                  FROM tasks WHERE status IN (%s, %s)
            """, (ST_PENDING, ST_RUNNING))
            row = cur.fetchone()
            return int(row[0]), int(row[1])
    except Exception:
        return 0, 0
    finally:
        conn.close()


def status_counts():
    """{status: count} across the whole table + a 'total' key — for the dashboard."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT status, COUNT(*) FROM tasks GROUP BY status")
            out = {row[0]: int(row[1]) for row in cur.fetchall()}
            out["total"] = sum(out.values())
            return out
    except Exception as e:
        return {"error": str(e)[:120]}
    finally:
        conn.close()


# ================= READER (read.py) =================

def _to_read_task(r):
    """read_tasks row dict -> the row_data shape read.py's process_account expects."""
    return {
        "task_id":   r["id"],
        # sheet_row is dropped by 0005; source_task_id is the reader row's identity.
        "row_index": r.get("source_task_id") if hasattr(r, "get") else None,
        "email":     r["email"],
        "password":  r["password"],
        "name":      r["name_used"],
    }


def claim_read_rows(instance_id, limit=3):
    """Atomically claim up to `limit` pending reader rows for this instance.

    Uses FOR UPDATE SKIP LOCKED so any number of parallel sessions/instances across
    servers can claim concurrently and never grab the same row (replaces the old
    write-token-then-reread Sheets jugaad). Returns a list of read-task dicts."""
    me = int(instance_id)
    conn = _conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            # Claim pending rows AND 'retry' rows (transient failures auto-retried).
            # PRIORITY: reads whose source buy is still 'unconfirmed' go FIRST — reading them
            # scrapes the real transaction id and flips the buy unconfirmed -> completed, so it
            # clears the review queue and unsticks a held card. Everything else follows, by id.
            cur.execute("""
                UPDATE read_tasks
                   SET status = %s, ran_by = %s, claimed_at = now(),
                       updated_at = now()
                 WHERE id IN (
                       SELECT r.id FROM read_tasks r
                        LEFT JOIN tasks t ON t.id = r.source_task_id
                        WHERE r.status IN (%s, %s)
                        ORDER BY (CASE WHEN t.status = %s THEN 0 ELSE 1 END), r.id
                        FOR UPDATE OF r SKIP LOCKED
                        LIMIT %s
                 )
             RETURNING *
            """, (ST_RUNNING, me, ST_PENDING, ST_RETRY, ST_UNCONFIRMED, int(limit)))
            rows = cur.fetchall()
        conn.commit()
        return [_to_read_task(r) for r in rows]
    finally:
        conn.close()


def read_retry_or_fail(task_id, max_retries=3, error="", books_read=None):
    """Reader transient-failure handler (buyer-style auto-retry). If the row's retry
    count is still under max_retries, bump it and set status 'retry' so claim_read_rows
    re-runs it; otherwise mark it 'failed'. Returns the status string it set."""
    err = str(error)[:500]
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE read_tasks
                   SET status = CASE WHEN retries + 1 < %s THEN %s ELSE %s END,
                       retries = retries + 1,
                       ran_by = CASE WHEN retries + 1 < %s THEN NULL ELSE ran_by END,
                       error = %s,
                       books_read = COALESCE(%s, books_read),
                       updated_at = now()
                 WHERE id = %s
             RETURNING status
            """, (max_retries, ST_RETRY, ST_FAILED, max_retries, err, books_read, task_id))
            row = cur.fetchone()
        conn.commit()
        return row[0] if row else None
    except Exception as e:
        print(f"❌ read_retry_or_fail failed: {e}", flush=True)
        return None
    finally:
        conn.close()


def update_read_task(task_id, status, transaction_id=None, transaction_date=None,
                     duration_sec=None, error="", books_read=None,
                     proof_shot=None, proof_node=None):
    """Write a reader row's result back to the DB and flag it for sheet writeback.

    proof_shot/proof_node: when no order id was found, the reader saved a full-page
    screenshot of my_orders as evidence — store its path + which node holds it so the
    dashboard can show it on the row. Only written when provided (a later success clears it)."""
    dur = (str(duration_sec) if duration_sec is not None else None)
    conn = _conn()
    try:
        with conn.cursor() as cur:
            # NOTE: transaction_at is a TIMESTAMP column and is already set at promote time
            # from the buy. The reader's `transaction_date` is a human date string scraped
            # from my_orders (e.g. "24 Aug 2026"), NOT a timestamp — writing it here caused
            # "COALESCE types text and timestamp cannot be matched" and silently failed the
            # whole writeback (status/txn/books never saved). So we do NOT touch transaction_at
            # here; we persist status + transaction_id + books + duration, which is what the
            # reader owns.
            # read.py sends "NOT_FOUND" (not '') when no order/txn was seen, so treat that
            # as "no id" everywhere — never persist the literal string.
            _txn = (str(transaction_id).strip() if transaction_id is not None else "")
            if _txn.upper() == "NOT_FOUND":
                _txn = ""
            # Proof: set it when given; CLEAR it once a real txn is found (no longer 'no order').
            _proof = (str(proof_shot).strip() if proof_shot else None)
            _pnode = (str(proof_node).strip() if proof_node else None)
            cur.execute("""
                UPDATE read_tasks
                   SET status = %s,
                       transaction_id   = COALESCE(NULLIF(%s,''), transaction_id),
                       duration_sec     = COALESCE(%s, duration_sec),
                       error = %s,
                       books_read = COALESCE(%s, books_read),
                       proof_shot = CASE WHEN %s <> '' THEN NULL ELSE COALESCE(%s, proof_shot) END,
                       proof_node = CASE WHEN %s <> '' THEN NULL ELSE COALESCE(%s, proof_node) END,
                       updated_at = now()
                 WHERE id = %s
            """, (status, _txn, dur, str(error)[:500],
                  books_read, _txn, _proof, _txn, _pnode, task_id))
            # CONFIRM-BACK (user rule): a reader that scraped a REAL transaction id has
            # PROVEN the purchase went through. If the source buy is still parked in
            # 'unconfirmed' (Needs Review), promote it to 'completed' and backfill its
            # transaction_id — the successful read IS the confirmation.
            if _txn:
                cur.execute("""
                    UPDATE tasks
                       SET status = %s,
                           transaction_id = COALESCE(NULLIF(transaction_id,''), %s),
                           updated_at = now()
                     WHERE id = (SELECT source_task_id FROM read_tasks WHERE id = %s)
                       AND status = %s
                 RETURNING card_id
                """, (ST_COMPLETED, _txn, task_id, ST_UNCONFIRMED))
                _promoted = cur.fetchone()
                # the confirmed buy consumed its card -> mark 'used' (accounting parity
                # with the normal-success path in update_task).
                if _promoted and _promoted[0] is not None:
                    cur.execute("UPDATE cards SET status='used', updated_at=now() "
                                "WHERE id=%s AND status <> 'used'", (_promoted[0],))
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ DB update_read_task failed: {e}", flush=True)
        return False
    finally:
        conn.close()


def backfill_confirmed_from_reads():
    """One-time (idempotent) repair: promote every buy still parked in 'unconfirmed'
    whose reader ALREADY scraped a real transaction id — the same confirm-back that
    update_read_task now does live, applied retroactively to rows read before the fix.
    Safe to re-run: only ever touches rows still 'unconfirmed'. Returns #promoted."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE tasks t
                   SET status = %s,
                       transaction_id = COALESCE(NULLIF(t.transaction_id,''), btrim(r.transaction_id)),
                       updated_at = now()
                  FROM read_tasks r
                 WHERE r.source_task_id = t.id
                   AND t.status = %s
                   AND r.transaction_id IS NOT NULL
                   AND btrim(r.transaction_id) <> ''
                   AND upper(btrim(r.transaction_id)) <> 'NOT_FOUND'
            """, (ST_COMPLETED, ST_UNCONFIRMED))
            n = cur.rowcount
        conn.commit()
        return n
    except Exception as e:
        print(f"❌ backfill_confirmed_from_reads failed: {e}", flush=True)
        return 0
    finally:
        conn.close()


def backfill_card_status():
    """One-time (idempotent) repair: apply the new card accounting to OLD rows that
    finalized before the fix, so used vs waste is correct historically.
      - a COMPLETED buy's card  -> 'used'   (was left 'reserved')
      - a terminally-FAILED buy's card -> 'payment_failed' (= waste)
    Unconfirmed buys are left alone (their card stays 'reserved' pending confirmation).
    Never downgrades an already-'used' card. Returns {'used': n, 'wasted': m}."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE cards SET status='used', updated_at=now()
                 WHERE status <> 'used'
                   AND id IN (SELECT card_id FROM tasks
                               WHERE status = %s AND card_id IS NOT NULL)
            """, (ST_COMPLETED,))
            used = cur.rowcount
            cur.execute("""
                UPDATE cards SET status='payment_failed', updated_at=now()
                 WHERE status = 'reserved'
                   AND id IN (SELECT card_id FROM tasks
                               WHERE status IN (%s, %s, %s) AND card_id IS NOT NULL)
            """, (ST_FAILED, ST_DECLINED, ST_INELIGIBLE))
            wasted = cur.rowcount
        conn.commit()
        return {"used": used, "wasted": wasted}
    except Exception as e:
        print(f"❌ backfill_card_status failed: {e}", flush=True)
        return {"used": 0, "burned": 0}
    finally:
        conn.close()


def reset_stale_reads(stale_seconds=1200):
    """Return reader rows stuck 'running' for too long (reader died mid-account)
    back to 'pending' so another session retries them. Call from the sync daemon."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE read_tasks
                   SET status = %s, ran_by = NULL, updated_at = now()
                 WHERE status = %s
                   AND claimed_at < now() - (%s || ' seconds')::interval
            """, (ST_PENDING, ST_RUNNING, str(int(stale_seconds))))
            n = cur.rowcount
        conn.commit()
        return n
    except Exception:
        return 0
    finally:
        conn.close()


def count_read_pending():
    """How many reader rows are still pending or running — for ETA/dashboard."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM read_tasks WHERE status IN (%s, %s, %s)",
                        (ST_PENDING, ST_RUNNING, ST_RETRY))
            return int(cur.fetchone()[0])
    except Exception:
        return 0
    finally:
        conn.close()


# ================= SOURCE (source.py) =================
# The pool behind "run this URL N times across the fleet". A batch is the N; the rows
# are the units. Every source instance on every server claims from this ONE pool, so
# the N is split across the fleet automatically — no per-server maths, no double-runs,
# and the count is exact because a row can only leave 'pending' once.

def create_source_batch(url, count, note=None):
    """Submit "run `url` `count` times". Creates the batch + `count` pending rows.

    Returns {"batch_id": id, "created": n}. The rows go in with one multi-row INSERT
    (generate_series) — 500 or 50,000 rows is a single statement either way.
    """
    url = (url or "").strip()
    count = int(count)
    if not url:
        raise ValueError("url is required")
    if count <= 0:
        raise ValueError("count must be > 0")
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO source_batches (url, total, status, note)
                VALUES (%s, %s, 'active', %s) RETURNING id
            """, (url, count, note))
            bid = int(cur.fetchone()[0])
            cur.execute("""
                INSERT INTO source_tasks (batch_id, url, status)
                SELECT %s, %s, 'pending' FROM generate_series(1, %s)
            """, (bid, url, count))
            created = cur.rowcount
        conn.commit()
        return {"batch_id": bid, "created": int(created)}
    finally:
        conn.close()


def claim_source_task(instance_id):
    """Claim ONE unit of source work for this instance, or None if the pool is dry.

    Same shape as claim_card_slots (db.py:1037) — FOR UPDATE SKIP LOCKED — so any
    number of instances across any number of servers can claim concurrently without
    two of them running the same row.

    Crash recovery first: a row this instance left 'running' (killed mid-run, node
    rebooted) is resumed before new work is taken, so it can never be orphaned.

    `None` is the signal the bot should EXIT — that is what makes the fleet go idle
    when the batch is finished, rather than spinning on an empty pool.
    """
    me = int(instance_id)
    conn = _conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            # 1) resume my own interrupted row
            cur.execute("""
                SELECT id, batch_id, url, attempts FROM source_tasks
                 WHERE status = 'running' AND ran_by = %s
                 ORDER BY id LIMIT 1
            """, (me,))
            row = cur.fetchone()
            if row:
                conn.commit()
                return dict(row)

            # 2) otherwise take the next pending row of an ACTIVE batch
            cur.execute("""
                UPDATE source_tasks
                   SET status = 'running', ran_by = %s, claimed_at = now(),
                       updated_at = now(), attempts = attempts + 1
                 WHERE id IN (
                       SELECT t.id FROM source_tasks t
                        WHERE t.status = 'pending'
                          AND t.batch_id IN (SELECT id FROM source_batches
                                              WHERE status = 'active')
                        ORDER BY t.id
                        FOR UPDATE SKIP LOCKED
                        LIMIT 1)
             RETURNING id, batch_id, url, attempts
            """, (me,))
            row = cur.fetchone()
        conn.commit()
        return dict(row) if row else None
    finally:
        conn.close()


def finish_source_task(task_id, ok=True, result=None, error=None, duration_sec=None):
    """Close a claimed row: 'running' -> 'done' | 'failed'.

    Guarded on status='running' so a stale-reset that already returned this row to the
    pool is not resurrected by a late write from the instance that lost it.
    """
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE source_tasks
                   SET status = %s, result = %s, error = %s,
                       duration_sec = %s, updated_at = now()
                 WHERE id = %s AND status = 'running'
            """, ('done' if ok else 'failed', result, error, duration_sec, int(task_id)))
            n = cur.rowcount
            # A batch whose rows are all settled is done — flips it out of 'active' so
            # the scheduler stops counting it and the UI can show it as finished.
            cur.execute("""
                UPDATE source_batches b SET status = 'done', updated_at = now()
                 WHERE b.id = (SELECT batch_id FROM source_tasks WHERE id = %s)
                   AND b.status = 'active'
                   AND NOT EXISTS (SELECT 1 FROM source_tasks t
                                    WHERE t.batch_id = b.id
                                      AND t.status IN ('pending', 'running'))
            """, (int(task_id),))
        conn.commit()
        return int(n)
    finally:
        conn.close()


def release_source_task(task_id):
    """Un-claim a row: 'running' -> 'pending', and give back the attempt.

    For INFRASTRUCTURE failures, not task failures. If the browser cannot launch at
    all (no chromium on the box, out of memory), the URL is blameless — marking it
    'failed' would burn one unit of the operator's count for a problem that has
    nothing to do with the work. Releasing puts it back so it runs once the box is
    fixed. Guarded on 'running' so a stale-reset that already freed it wins.
    """
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE source_tasks
                   SET status='pending', ran_by=NULL, claimed_at=NULL,
                       attempts=GREATEST(0, attempts - 1), updated_at=now()
                 WHERE id=%s AND status='running'
            """, (int(task_id),))
            n = cur.rowcount
        conn.commit()
        return int(n)
    finally:
        conn.close()


def requeue_failed_source(batch_id=None):
    """'failed' -> 'pending', so a batch ruined by a broken box can be re-run.

    Also reopens a batch that had already flipped to 'done' on failures alone —
    otherwise the rows would be pending inside an inactive batch and never claimed.
    `batch_id=None` requeues every failed row.
    """
    conn = _conn()
    try:
        with conn.cursor() as cur:
            if batch_id is None:
                cur.execute("""
                    UPDATE source_tasks
                       SET status='pending', ran_by=NULL, claimed_at=NULL,
                           error=NULL, updated_at=now()
                     WHERE status='failed'
                """)
            else:
                cur.execute("""
                    UPDATE source_tasks
                       SET status='pending', ran_by=NULL, claimed_at=NULL,
                           error=NULL, updated_at=now()
                     WHERE status='failed' AND batch_id=%s
                """, (int(batch_id),))
            n = cur.rowcount
            cur.execute("""
                UPDATE source_batches b SET status='active', updated_at=now()
                 WHERE b.status='done'
                   AND EXISTS (SELECT 1 FROM source_tasks t
                                WHERE t.batch_id=b.id AND t.status='pending')
            """)
        conn.commit()
        return int(n)
    finally:
        conn.close()


def source_progress():
    """Per-batch progress + a fleet-wide total, for the Source page.

    Each batch: {id, url, total, status, done, failed, running, pending, settled, pct}.
    `pending` is what is still claimable — when it hits 0 fleet-wide, no new source
    slot is filled and the running ones exit as they finish.
    """
    conn = _conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT b.id, b.url, b.total, b.status, b.note, b.created_at, b.updated_at,
                       COALESCE(SUM((t.status = 'done')::int),    0) AS done,
                       COALESCE(SUM((t.status = 'failed')::int),  0) AS failed,
                       COALESCE(SUM((t.status = 'running')::int), 0) AS running,
                       COALESCE(SUM((t.status = 'pending')::int), 0) AS pending
                  FROM source_batches b
                  LEFT JOIN source_tasks t ON t.batch_id = b.id
                 GROUP BY b.id
                 ORDER BY b.id DESC
            """)
            rows = [dict(r) for r in cur.fetchall()]
        agg = {"total": 0, "done": 0, "failed": 0, "running": 0, "pending": 0}
        for r in rows:
            for k in ("done", "failed", "running", "pending"):
                r[k] = int(r[k])
                agg[k] += r[k]
            r["total"] = int(r["total"])
            agg["total"] += r["total"]
            r["settled"] = r["done"] + r["failed"]
            r["pct"] = round(100.0 * r["settled"] / r["total"], 1) if r["total"] else 0.0
            for k in ("created_at", "updated_at"):
                r[k] = r[k].isoformat() if r.get(k) else None
        agg["settled"] = agg["done"] + agg["failed"]
        agg["pct"] = round(100.0 * agg["settled"] / agg["total"], 1) if agg["total"] else 0.0
        return {"batches": rows, "agg": agg}
    finally:
        conn.close()


def set_source_batch_status(batch_id, status):
    """active | stopped | done. 'stopped' makes the batch unclaimable immediately
    (claims filter on active) without deleting anything — flip it back to resume."""
    if status not in ("active", "stopped", "done"):
        raise ValueError("status must be active|stopped|done")
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE source_batches SET status=%s, updated_at=now() WHERE id=%s",
                        (status, int(batch_id)))
            n = cur.rowcount
        conn.commit()
        return int(n)
    finally:
        conn.close()


def clear_stuck_source(minutes=30):
    """Return rows stuck 'running' for > `minutes` to the pool.

    A killed instance leaves its claimed row 'running' forever — it holds a slot of the
    count that will never complete, so the batch never reaches 100%. This is the same
    escape hatch as the reader's Clear Stuck button."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE source_tasks
                   SET status='pending', ran_by=NULL, claimed_at=NULL, updated_at=now()
                 WHERE status='running'
                   AND claimed_at < now() - (%s || ' minutes')::interval
            """, (int(minutes),))
            n = cur.rowcount
        conn.commit()
        return int(n)
    finally:
        conn.close()


# ================= NYKAA (nykaa.py) =================
# The pool behind "make N Nykaa accounts". Deliberately a near-copy of the source pool:
# same claim semantics, same release-vs-fail distinction, same requeue. Two pools that
# behave identically are two pools an operator only has to learn once.

def create_nykaa_batch(count, note=None):
    """Submit "make `count` accounts". Creates the batch + `count` pending rows."""
    count = int(count)
    if count <= 0:
        raise ValueError("count must be > 0")
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO nykaa_batches (total, status, note) "
                        "VALUES (%s, 'active', %s) RETURNING id", (count, note))
            bid = int(cur.fetchone()[0])
            cur.execute("INSERT INTO nykaa_tasks (batch_id, status) "
                        "SELECT %s, 'pending' FROM generate_series(1, %s)", (bid, count))
            created = cur.rowcount
        conn.commit()
        return {"batch_id": bid, "created": int(created)}
    finally:
        conn.close()


def claim_nykaa_task(instance_id):
    """Claim ONE account to create, or None if the pool is dry.

    Crash recovery first: a row this instance left 'running' is resumed before new work
    is taken, so it can never be orphaned. `None` is the signal to EXIT — that is what
    takes the fleet idle when the batch is finished.
    """
    me = int(instance_id)
    conn = _conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT id, batch_id, attempts FROM nykaa_tasks
                 WHERE status = 'running' AND ran_by = %s
                 ORDER BY id LIMIT 1
            """, (me,))
            row = cur.fetchone()
            if row:
                conn.commit()
                return dict(row)

            cur.execute("""
                UPDATE nykaa_tasks
                   SET status='running', ran_by=%s, claimed_at=now(),
                       updated_at=now(), attempts = attempts + 1
                 WHERE id IN (
                       SELECT t.id FROM nykaa_tasks t
                        WHERE t.status = 'pending'
                          AND t.batch_id IN (SELECT id FROM nykaa_batches
                                              WHERE status = 'active')
                        ORDER BY t.id
                        FOR UPDATE SKIP LOCKED
                        LIMIT 1)
             RETURNING id, batch_id, attempts
            """, (me,))
            row = cur.fetchone()
        conn.commit()
        return dict(row) if row else None
    finally:
        conn.close()


def finish_nykaa_task(task_id, ok=True, result=None, error=None, duration_sec=None):
    """'running' -> 'done' | 'failed'. Guarded on 'running' so a stale-reset that
    already freed the row is not undone by a late write."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE nykaa_tasks
                   SET status=%s, result=%s, error=%s, duration_sec=%s, updated_at=now()
                 WHERE id=%s AND status='running'
            """, ('done' if ok else 'failed', result, error, duration_sec, int(task_id)))
            n = cur.rowcount
            cur.execute("""
                UPDATE nykaa_batches b SET status='done', updated_at=now()
                 WHERE b.id = (SELECT batch_id FROM nykaa_tasks WHERE id=%s)
                   AND b.status='active'
                   AND NOT EXISTS (SELECT 1 FROM nykaa_tasks t
                                    WHERE t.batch_id=b.id
                                      AND t.status IN ('pending','running'))
            """, (int(task_id),))
        conn.commit()
        return int(n)
    finally:
        conn.close()


def release_nykaa_task(task_id):
    """Un-claim: 'running' -> 'pending', attempt given back.

    For INFRASTRUCTURE failures only. If Chrome will not start, the account is
    blameless — spending a unit of the operator's count on a broken box is exactly the
    bug this exists to prevent."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE nykaa_tasks
                   SET status='pending', ran_by=NULL, claimed_at=NULL,
                       attempts=GREATEST(0, attempts - 1), updated_at=now()
                 WHERE id=%s AND status='running'
            """, (int(task_id),))
            n = cur.rowcount
        conn.commit()
        return int(n)
    finally:
        conn.close()


def requeue_failed_nykaa(batch_id=None):
    """'failed' -> 'pending', and reopen a batch that flipped to 'done' on failures
    alone (otherwise its rows sit pending inside an inactive batch, unclaimable)."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            if batch_id is None:
                cur.execute("UPDATE nykaa_tasks SET status='pending', ran_by=NULL, "
                            "claimed_at=NULL, error=NULL, updated_at=now() "
                            "WHERE status='failed'")
            else:
                cur.execute("UPDATE nykaa_tasks SET status='pending', ran_by=NULL, "
                            "claimed_at=NULL, error=NULL, updated_at=now() "
                            "WHERE status='failed' AND batch_id=%s", (int(batch_id),))
            n = cur.rowcount
            cur.execute("""
                UPDATE nykaa_batches b SET status='active', updated_at=now()
                 WHERE b.status='done'
                   AND EXISTS (SELECT 1 FROM nykaa_tasks t
                                WHERE t.batch_id=b.id AND t.status='pending')
            """)
        conn.commit()
        return int(n)
    finally:
        conn.close()


def clear_stuck_nykaa(minutes=30):
    """Rows a killed instance left 'running' hold a piece of the count that never
    completes, so the batch stalls short of 100%. Return them to the pool."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE nykaa_tasks
                   SET status='pending', ran_by=NULL, claimed_at=NULL, updated_at=now()
                 WHERE status='running'
                   AND claimed_at < now() - (%s || ' minutes')::interval
            """, (int(minutes),))
            n = cur.rowcount
        conn.commit()
        return int(n)
    finally:
        conn.close()


def set_nykaa_batch_status(batch_id, status):
    """active | stopped | done. 'stopped' makes the batch unclaimable at once without
    deleting anything — flip it back to resume."""
    if status not in ("active", "stopped", "done"):
        raise ValueError("status must be active|stopped|done")
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE nykaa_batches SET status=%s, updated_at=now() WHERE id=%s",
                        (status, int(batch_id)))
            n = cur.rowcount
        conn.commit()
        return int(n)
    finally:
        conn.close()


def save_nykaa_account(record, ran_by=None, task_id=None):
    """Store one created account. Replaces the Google Sheet + CSV append.

    ON CONFLICT DO NOTHING on `mobile`: a retry that re-uses the same number must not
    create a second row. Returns the row id, or None if it was already there.
    """
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO nykaa_accounts
                       (mobile, name, email, session_file, provider, ran_by, task_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (mobile) DO NOTHING
             RETURNING id
            """, (str(record.get("mobile") or "").strip(),
                  record.get("name"), record.get("email"),
                  record.get("session_file"), record.get("provider"),
                  int(ran_by) if ran_by else None,
                  int(task_id) if task_id else None))
            row = cur.fetchone()
        conn.commit()
        return int(row[0]) if row else None
    finally:
        conn.close()


def nykaa_accounts(limit=500, offset=0):
    """Newest accounts first, for the Nykaa page's table / CSV export."""
    conn = _conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT id, mobile, name, email, session_file, provider, ran_by, created_at
                  FROM nykaa_accounts
                 ORDER BY id DESC LIMIT %s OFFSET %s
            """, (int(limit), int(offset)))
            rows = [dict(r) for r in cur.fetchall()]
            cur.execute("SELECT count(*) AS n FROM nykaa_accounts")
            total = int(cur.fetchone()["n"])
        for r in rows:
            r["created_at"] = r["created_at"].isoformat() if r.get("created_at") else None
        return {"accounts": rows, "total": total}
    finally:
        conn.close()


def nykaa_progress():
    """Per-batch progress + a fleet-wide roll-up, for the Nykaa page."""
    conn = _conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT b.id, b.total, b.status, b.note, b.created_at, b.updated_at,
                       COALESCE(SUM((t.status='done')::int),    0) AS done,
                       COALESCE(SUM((t.status='failed')::int),  0) AS failed,
                       COALESCE(SUM((t.status='running')::int), 0) AS running,
                       COALESCE(SUM((t.status='pending')::int), 0) AS pending
                  FROM nykaa_batches b
                  LEFT JOIN nykaa_tasks t ON t.batch_id = b.id
                 GROUP BY b.id ORDER BY b.id DESC
            """)
            rows = [dict(r) for r in cur.fetchall()]
        agg = {"total": 0, "done": 0, "failed": 0, "running": 0, "pending": 0}
        for r in rows:
            for k in ("done", "failed", "running", "pending"):
                r[k] = int(r[k]); agg[k] += r[k]
            r["total"] = int(r["total"]); agg["total"] += r["total"]
            r["settled"] = r["done"] + r["failed"]
            r["pct"] = round(100.0 * r["settled"] / r["total"], 1) if r["total"] else 0.0
            for k in ("created_at", "updated_at"):
                r[k] = r[k].isoformat() if r.get(k) else None
        agg["settled"] = agg["done"] + agg["failed"]
        agg["pct"] = round(100.0 * agg["settled"] / agg["total"], 1) if agg["total"] else 0.0
        return {"batches": rows, "agg": agg}
    finally:
        conn.close()


def scheduler_pending():
    """CLAIMABLE work counts by work-kind, for the node_agent auto-scheduler so it
    never spawns a bot when the DB has nothing for it to do.

    Returns {"buyer": n, "reader": n, "cards": n} counting ONLY rows a freshly-launched
    bot could actually claim (not rows already 'running' under another instance):
      buyer  -> tasks.status = 'pending'
      reader -> read_tasks.status IN ('pending','retry')
      cards  -> cards.status = 'requested' in an ACTIVE campaign (what claim_card_slots
                grabs — line 819)
      source -> source_tasks.status = 'pending' in an ACTIVE batch (what
                claim_source_task grabs). Hitting 0 is what takes the source slots
                idle once a batch's count is used up.
    Raises on DB failure so the caller can fail-open (keep launching) rather than
    silently starving production on a transient blip."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM tasks WHERE status = %s", (ST_PENDING,))
            buyer = int(cur.fetchone()[0])
            # The buyer STOPS claiming once today's plan is met (claim_next_group ->
            # buyer_daily_cap_reached). If we still reported those pending rows as claimable,
            # the auto-scheduler would flood every free slot with buyers that instantly claim
            # nothing and exit — churning slots and starving reads. So zero it when capped.
            if buyer and os.environ.get("AUTO_DAILY_CAP", "1") == "1" and buyer_daily_cap_reached():
                buyer = 0
            cur.execute("SELECT COUNT(*) FROM read_tasks WHERE status IN (%s, %s)",
                        (ST_PENDING, ST_RETRY))
            reader = int(cur.fetchone()[0])
            cur.execute("""
                SELECT COUNT(*) FROM cards
                 WHERE status = 'requested'
                   AND campaign_id IN (SELECT id FROM campaigns WHERE status = 'active')
            """)
            cards = int(cur.fetchone()[0])
            cur.execute("""
                SELECT COUNT(*) FROM source_tasks
                 WHERE status = 'pending'
                   AND batch_id IN (SELECT id FROM source_batches WHERE status = 'active')
            """)
            source = int(cur.fetchone()[0])
            cur.execute("""
                SELECT COUNT(*) FROM nykaa_tasks
                 WHERE status = 'pending'
                   AND batch_id IN (SELECT id FROM nykaa_batches WHERE status = 'active')
            """)
            nykaa = int(cur.fetchone()[0])
        return {"buyer": buyer, "reader": reader, "cards": cards,
                "source": source, "nykaa": nykaa}
    finally:
        conn.close()


def read_progress():
    """Snapshot of reader progress: {status: count}, total, and total books read.
    Use this to see at a glance what's left vs done."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT status, COUNT(*), COALESCE(SUM(books_read),0) "
                        "FROM read_tasks GROUP BY status")
            rows = cur.fetchall()
        out = {r[0]: int(r[1]) for r in rows}
        out["total"] = sum(int(r[1]) for r in rows)
        out["books_read"] = sum(int(r[2]) for r in rows)
        out["left"] = out.get(ST_PENDING, 0) + out.get(ST_RUNNING, 0) + out.get(ST_RETRY, 0)
        # Transaction-ID outcome: how many rows got a REAL txn id vs NOT_FOUND. Lets the
        # dashboard show reader success at a glance (txn found = order actually placed).
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                  COUNT(*) FILTER (WHERE transaction_id IS NOT NULL
                                     AND transaction_id <> ''
                                     AND transaction_id <> 'NOT_FOUND') AS found,
                  COUNT(*) FILTER (WHERE transaction_id = 'NOT_FOUND')   AS notfound
                FROM read_tasks
            """)
            tr = cur.fetchone()
        out["txn_found"] = int(tr[0] or 0)
        out["txn_notfound"] = int(tr[1] or 0)
        return out
    except Exception as e:
        return {"error": str(e)[:120]}
    finally:
        conn.close()


def clear_stuck_reads(minutes=8):
    """Re-queue reader rows stuck 'running' with transaction_id='NOT_FOUND' for longer
    than `minutes` (timed-out readers holding a slot) back to 'pending' so a fresh reader
    re-reads them. The age filter avoids touching readers that are still genuinely working
    (those finish well under `minutes`). Returns how many rows were re-queued."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE read_tasks
                   SET status = %s, ran_by = NULL, claimed_at = NULL
                 WHERE transaction_id = 'NOT_FOUND' AND status = %s
                   AND claimed_at < now() - (%s || ' minutes')::interval
            """, (ST_PENDING, ST_RUNNING, int(minutes)))
            n = cur.rowcount
        conn.commit()
        return n
    except Exception:
        try: conn.rollback()
        except Exception: pass
        return 0
    finally:
        conn.close()


def requeue_failed_reads(include_running_older_than=None):
    """Reset reader rows that did NOT complete back to 'pending' so the reader retries
    ONLY them (done rows are never touched). By default re-queues all 'failed' rows.
    Pass include_running_older_than=<seconds> to also free rows stuck 'running'.
    Returns how many rows were re-queued."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE read_tasks
                   SET status = %s, ran_by = NULL, error = NULL,
                       updated_at = now()
                 WHERE status = %s
            """, (ST_PENDING, ST_FAILED))
            n = cur.rowcount
            if include_running_older_than is not None:
                cur.execute("""
                    UPDATE read_tasks
                       SET status = %s, ran_by = NULL, updated_at = now()
                     WHERE status = %s
                       AND claimed_at < now() - (%s || ' seconds')::interval
                """, (ST_PENDING, ST_RUNNING, str(int(include_running_older_than))))
                n += cur.rowcount
        conn.commit()
        return n
    except Exception as e:
        print(f"❌ requeue_failed_reads failed: {e}", flush=True)
        return 0
    finally:
        conn.close()


# ================= BUYER: retry / OTP-lock / OTP-alerts / stale =================
# These power the "best-of-both" buyer (magzter-pro/buyer.py): aws-style transient
# retry, per-employee OTP serialization, and the OTP-failure alert banner — all on
# Postgres instead of /tmp lock files.

import contextlib


def retry_or_fail(task_id, max_retries=3, error="", final_status=None,
                  name_used="", proxy_ip="", duration_sec=None, transaction_id=None):
    """Failure handler (user rule: EVERY failure retries, then lands on its real status).
    If the row's retry count is still under max_retries, bump it and put the row BACK to
    'pending' so any instance re-runs it — but the DEFER_RETRIES claim order holds it
    behind ALL fresh work, so first attempts finish before any retry starts. Once retries
    are exhausted it's marked `final_status` (default 'failed'; pass 'declined'/'ineligible'
    to keep the real reason). Row metadata (name/proxy/duration/txn) is recorded either way.
    Only acts on a row still 'running'. Returns the status it set ('pending' or terminal)."""
    fs = final_status or ST_FAILED
    dur = (str(duration_sec) if duration_sec is not None else None)
    err = str(error)[:500]
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE tasks
                   SET status = CASE WHEN retries + 1 < %s THEN %s ELSE %s END,
                       retries = retries + 1,
                       ran_by = CASE WHEN retries + 1 < %s THEN NULL ELSE ran_by END,
                       name_used = COALESCE(NULLIF(%s,''), name_used),
                       proxy_ip  = COALESCE(NULLIF(%s,''), proxy_ip),
                       duration_sec = COALESCE(%s, duration_sec),
                       transaction_id = COALESCE(%s, transaction_id),
                       error = %s, updated_at = now()
                 WHERE id = %s AND status = %s
             RETURNING status, retries
            """, (max_retries, ST_PENDING, fs, max_retries,
                  name_used, proxy_ip, dur, transaction_id, err, task_id, ST_RUNNING))
            row = cur.fetchone()
            # CARD ACCOUNTING: if this attempt exhausted retries and the row landed on its
            # terminal FAILURE status, the reserved card was spent on a dead buy -> mark it
            # 'payment_failed' (= waste; the only non-success terminal card status allowed by
            # ck_cards_status). While it's still re-queued to 'pending' the card stays
            # 'reserved' (the retry reuses the same card).
            if row and row[0] == fs:
                cur.execute("""
                    UPDATE cards SET status='payment_failed', updated_at=now()
                     WHERE id = (SELECT card_id FROM tasks WHERE id=%s)
                       AND status = 'reserved'
                """, (task_id,))
        conn.commit()
        return row[0] if row else None
    except Exception as e:
        print(f"❌ retry_or_fail failed: {e}", flush=True)
        return None
    finally:
        conn.close()


@contextlib.contextmanager
def otp_lock(emp_id, timeout_s=300):
    """Serialize the corporate→OTP→confirm window PER EMPLOYEE across all instances/
    servers, so two bots on the same emp never consume each other's OTP. Postgres
    session advisory lock on hashtext(emp_id) held on a dedicated connection.

        with db.otp_lock(emp_id):
            ... submit corp form, fetch + fill OTP, confirm ...

    Blocks (up to timeout_s) until the lock is free, then yields. Always released."""
    conn = _conn()
    got = False
    try:
        with conn.cursor() as cur:
            cur.execute("SET LOCAL lock_timeout = %s", (f"{int(timeout_s)}s",))
            try:
                cur.execute("SELECT pg_advisory_lock(hashtext(%s))", (str(emp_id),))
                got = True
            except Exception as e:
                conn.rollback()
                print(f"⚠️ otp_lock({emp_id}) wait failed: {e}", flush=True)
        conn.commit()
        yield got
    finally:
        try:
            if got:
                with conn.cursor() as cur:
                    cur.execute("SELECT pg_advisory_unlock(hashtext(%s))", (str(emp_id),))
                conn.commit()
        except Exception:
            pass
        conn.close()


def record_otp_failure(emp_id):
    """Increment the consecutive + total OTP-failure counts for an employee."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO otp_alerts (emp_id, consecutive_failures, total_failures, last_failure, updated_at)
                VALUES (%s, 1, 1, now(), now())
                ON CONFLICT (emp_id) DO UPDATE
                    SET consecutive_failures = otp_alerts.consecutive_failures + 1,
                        total_failures = otp_alerts.total_failures + 1,
                        last_failure = now(), updated_at = now()
            """, (emp_id,))
        conn.commit()
    except Exception as e:
        print(f"⚠️ record_otp_failure failed: {e}", flush=True)
    finally:
        conn.close()


def record_otp_success(emp_id):
    """Reset the consecutive OTP-failure count for an employee (clears the alert)."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE otp_alerts SET consecutive_failures = 0, updated_at = now()
                 WHERE emp_id = %s
            """, (emp_id,))
        conn.commit()
    except Exception as e:
        print(f"⚠️ record_otp_success failed: {e}", flush=True)
    finally:
        conn.close()


def get_otp_alerts(threshold=3):
    """Employees at/above the OTP-failure threshold — for the dashboard red banner.
    Returns {emp_id, consecutive_failures, total_failures, last_failure}."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT emp_id, consecutive_failures, total_failures, last_failure
                  FROM otp_alerts WHERE consecutive_failures >= %s
                 ORDER BY consecutive_failures DESC, last_failure DESC
            """, (int(threshold),))
            return [{"emp_id": r[0], "consecutive_failures": int(r[1]),
                     "total_failures": int(r[2]),
                     "last_failure": (r[3].strftime("%Y-%m-%d %H:%M:%S") if r[3] else "")}
                    for r in cur.fetchall()]
    except Exception:
        return []
    finally:
        conn.close()


def recent_transactions(limit=30):
    """Last N finished buyer tasks for the dashboard feed:
    [{time, email, status, duration, error}] newest first. status is the canonical
    uppercase outcome (SUCCESS/FAILED/DECLINED/INELIGIBLE/UNCONFIRMED)."""
    label = {ST_COMPLETED: "SUCCESS", ST_FAILED: "FAILED", ST_DECLINED: "DECLINED",
             ST_INELIGIBLE: "INELIGIBLE", ST_UNCONFIRMED: "UNCONFIRMED"}
    conn = _conn()
    try:
        with conn.cursor() as cur:
            # email now comes from the identity (migration 0003). COALESCE to
            # updated_email so the feed shows the address the account was ACTUALLY
            # created with when email-mutation fired (buyer.py:1163) — showing the
            # canonical one would be a lie about what happened.
            # LEFT JOINs: a task that failed before an identity was reserved still
            # belongs in the feed, just without an email.
            cur.execute("""
                SELECT t.updated_at,
                       COALESCE(t.updated_email, e.email) AS email,
                       t.status, t.duration_sec, t.error
                  FROM tasks t
                  LEFT JOIN identities i ON i.id = t.identity_id
                  LEFT JOIN emails     e ON e.id = i.email_id
                 WHERE t.status IN (%s,%s,%s,%s,%s)
                 ORDER BY t.updated_at DESC NULLS LAST
                 LIMIT %s
            """, (ST_COMPLETED, ST_FAILED, ST_DECLINED, ST_INELIGIBLE,
                  ST_UNCONFIRMED, int(limit)))
            out = []
            for r in cur.fetchall():
                out.append({
                    "time":  r[0].strftime("%m-%d %H:%M:%S") if r[0] else "",
                    "email": r[1] or "",
                    "status": label.get(r[2], (r[2] or "").upper()),
                    "duration": (f"{float(r[3]):.0f}s" if r[3] is not None else ""),
                    "error": (r[4] or "")[:90],
                })
            return out
    except Exception:
        return []
    finally:
        conn.close()


def instance_status():
    """Per-instance (ran_by) live status, derived from the tasks table — the DB
    equivalent of aws's per-instance log parsing:
    [{id, done, success, failed, active, current_task, last_result, proxy_ip}]."""
    label = {ST_COMPLETED: "SUCCESS", ST_FAILED: "FAILED", ST_DECLINED: "DECLINED",
             ST_INELIGIBLE: "INELIGIBLE", ST_UNCONFIRMED: "UNCONFIRMED"}
    terminal = (ST_COMPLETED, ST_FAILED, ST_DECLINED, ST_INELIGIBLE, ST_UNCONFIRMED)
    conn = _conn()
    try:
        import psycopg2.extras
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        # counts per instance
        cur.execute("""
            SELECT ran_by, status, COUNT(*) c FROM tasks
             WHERE ran_by IS NOT NULL GROUP BY ran_by, status
        """)
        inst = {}
        for r in cur.fetchall():
            rid = int(r["ran_by"])
            d = inst.setdefault(rid, {"id": rid, "done": 0, "success": 0, "failed": 0,
                                      "active": False, "current_task": "",
                                      "current_emp": "CHANGE_ME_EMP_ID", "current_step": "", "step_secs": 0,
                                      "last_result": "Doe", "proxy_ip": ""})
            st, c = r["status"], int(r["c"])
            if st in terminal:
                d["done"] += c
                if st == ST_COMPLETED: d["success"] += c
                elif st == ST_FAILED:  d["failed"]  += c
        # current running task per instance (incl. which employee + STEP it's on, and how
        # long it's been on that step — so a stuck instance is obvious).
        cur.execute("""
            SELECT DISTINCT ON (ran_by) ran_by, id, email, emp_id, proxy_ip,
                   step, EXTRACT(EPOCH FROM (now() - step_at))::int AS step_secs
              FROM tasks WHERE status = %s AND ran_by IS NOT NULL
             ORDER BY ran_by, updated_at DESC
        """, (ST_RUNNING,))
        for r in cur.fetchall():
            rid = int(r["ran_by"])
            d = inst.setdefault(rid, {"id": rid, "done": 0, "success": 0, "failed": 0,
                                      "active": False, "current_task": "",
                                      "current_emp": "CHANGE_ME_EMP_ID", "current_step": "", "step_secs": 0,
                                      "last_result": "Doe", "proxy_ip": ""})
            d["active"] = True
            d["current_task"] = (f"#{r['id']}: " if r["id"] else "") + (r["email"] or "")
            d["current_emp"] = r["emp_id"] or ""
            d["current_step"] = r["step"] or ""
            d["step_secs"] = int(r["step_secs"] or 0)
            d["proxy_ip"] = r["proxy_ip"] or d["proxy_ip"]
        # last finished result per instance
        cur.execute("""
            SELECT DISTINCT ON (ran_by) ran_by, status, proxy_ip
              FROM tasks WHERE ran_by IS NOT NULL AND status = ANY(%s)
             ORDER BY ran_by, updated_at DESC
        """, (list(terminal),))
        for r in cur.fetchall():
            rid = int(r["ran_by"])
            if rid in inst:
                inst[rid]["last_result"] = label.get(r["status"], "")
                if not inst[rid]["proxy_ip"]:
                    inst[rid]["proxy_ip"] = r["proxy_ip"] or ""
        cur.close()
        return [inst[k] for k in sorted(inst)]
    except Exception:
        return []
    finally:
        conn.close()


def reset_stale_running(stale_seconds=360):
    """Buyer-side stale-row cleanup (aws clean_stale_rows). Rows stuck 'running' longer
    than stale_seconds (a crashed bot) go back to 'pending'. Run from the dashboard/
    supervisor periodically. Returns how many were reset."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE tasks SET status = %s, ran_by = NULL, updated_at = now()
                 WHERE status = %s AND claimed_at < now() - (%s || ' seconds')::interval
            """, (ST_PENDING, ST_RUNNING, str(int(stale_seconds))))
            n = cur.rowcount
        conn.commit()
        return n
    except Exception:
        return 0
    finally:
        conn.close()


def emp_progress():
    """Per-employee buyer progress for the dashboard:
    [{emp_id, total, completed, failed, declined, ineligible, unconfirmed,
      running, pending}] ordered by emp_id."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT emp_id, status, COUNT(*) FROM tasks GROUP BY emp_id, status")
            rows = cur.fetchall()
        agg = {}
        for emp, st, cnt in rows:
            d = agg.setdefault(emp or "(none)", {"emp_id": emp or "(none)", "total": 0,
                "completed": 0, "failed": 0, "declined": 0, "ineligible": 0,
                "unconfirmed": 0, "running": 0, "pending": 0})
            d["total"] += int(cnt)
            if st in d:
                d[st] += int(cnt)
        return sorted(agg.values(), key=lambda x: str(x["emp_id"]))
    except Exception:
        return []
    finally:
        conn.close()


# ================= DASHBOARD ANALYTICS (buyer + reader) =================
# All read-only aggregates for the dashboard panels. Every function is defensive and
# returns a safe default on error so a single bad query never blanks the dashboard.

# An error string is normalised to a REASON by taking the text before the first ':'
# and dropping any trailing "(...)" — so "Card declined: insufficient funds" and
# "Continue button stayed disabled (email not accepted)" collapse to clean buckets.
_REASON_SQL = (
    r"regexp_replace(split_part(COALESCE(NULLIF(TRIM(error),''),'(no message)'),"
    r"':',1), '\s*\(.*$', '')"
)


# Named dashboard periods → SQL WHERE fragment on updated_at. The connection runs in IST
# (SET TIME ZONE), so date_trunc('day', now()) is IST midnight → "today"/"yesterday" are
# calendar-correct for the operator. Whitelist-only, all literals → no params, no
# injection (used in both positional and named-param queries).
_PERIOD_SQL = {
    "today":     " AND updated_at >= date_trunc('day', now())",
    "yesterday": " AND updated_at >= date_trunc('day', now()) - interval '1 day'"
                 " AND updated_at <  date_trunc('day', now())",
    "1h":  " AND updated_at > now() - interval '1 hour'",
    "6h":  " AND updated_at > now() - interval '6 hours'",
    "24h": " AND updated_at > now() - interval '24 hours'",
    "7d":  " AND updated_at > now() - interval '7 days'",
    "30d": " AND updated_at > now() - interval '30 days'",
}

import re as _re
import datetime as _dtmod
# A custom range is encoded as  custom|<from>|<to>  where each side is a datetime the
# HTML datetime-local input produces (YYYY-MM-DDTHH:MM[:SS]) or a bare date. Strictly
# validated before it touches SQL — the fragment is interpolated, not parameterised.
_DT_RE = _re.compile(r"^\d{4}-\d{2}-\d{2}([ T]\d{2}:\d{2}(:\d{2})?)?$")


def _real_datetime(v):
    """True only if v is a REAL date/datetime — rejects format-valid nonsense like
    2026-13-99 (which the regex alone accepts and Postgres then errors on)."""
    v = v.strip()
    if not _DT_RE.match(v):
        return False
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            _dtmod.datetime.strptime(v.replace("T", " "), fmt)
            return True
        except ValueError:
            continue
    return False


def _win_clause(period):
    """SQL WHERE fragment (string only, no params) for a named dashboard period:
    all|today|yesterday|1h|6h|24h|7d|30d, or a custom range 'custom|FROM|TO'.
    Back-compat: a bare number => last N hours; None/0/'all' => no filter."""
    raw = str(period if period is not None else "all").strip()
    p = raw.lower()
    if p in ("all", "0", "", "none"):
        return ""

    if p.startswith("custom|"):
        parts = raw.split("|")            # use raw (original case) — timestamps have no letters but 'T'
        if len(parts) == 3:
            frm, to = parts[1].strip().replace("T", " "), parts[2].strip().replace("T", " ")
            # STRICT validation — must be a REAL date/datetime (not just format-valid),
            # so nothing injectable AND nothing that errors in Postgres reaches the SQL.
            if _real_datetime(parts[1]) and _real_datetime(parts[2]):
                return f" AND updated_at >= '{frm}' AND updated_at <= '{to}'"
        return ""                          # malformed custom range => no filter

    if p in _PERIOD_SQL:
        return _PERIOD_SQL[p]
    try:                                  # bare number / 'Nh' => last N hours (old API)
        h = int(p.rstrip("h"))
        if h > 0:
            return f" AND updated_at > now() - interval '{int(h)} hours'"
    except Exception:
        pass
    return ""


def _failure_breakdown(table, statuses, limit, period=None):
    win = _win_clause(period)
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT {_REASON_SQL} AS reason, COUNT(*) c
                  FROM {table}
                 WHERE status = ANY(%s){win}
                 GROUP BY reason ORDER BY c DESC LIMIT %s
            """, [list(statuses), int(limit)])
            return [{"reason": r[0] or "(no message)", "count": int(r[1])}
                    for r in cur.fetchall()]
    except Exception:
        return []
    finally:
        conn.close()


def failure_breakdown(limit=12, period=None):
    """Top BUYER failure reasons (normalised) among non-success outcomes. period:
    all|today|yesterday|1h|6h|24h|7d|30d for the dashboard date filter."""
    return _failure_breakdown("tasks",
        (ST_FAILED, ST_DECLINED, ST_INELIGIBLE, ST_UNCONFIRMED), limit, period)


def read_failure_breakdown(limit=12, period=None):
    """Top READER failure reasons (normalised) among failed read_tasks (period-filtered)."""
    return _failure_breakdown("read_tasks", (ST_FAILED,), limit, period)


# Map a buyer error string to the STAGE it died at (where in the funnel it failed).
# Order matters — first match wins.
_STAGE_CASE = """
    CASE
      WHEN error ILIKE '%%captcha%%' THEN 'CAPTCHA'
      WHEN error ILIKE '%%Site unavailable%%' OR error ILIKE '%%503%%'
           OR error ILIKE '%%too many requests%%' THEN 'SITE-DOWN'
      WHEN error ILIKE '%%not eligible%%' OR error ILIKE '%%ineligib%%' THEN 'ELIGIBILITY'
      WHEN error ILIKE '%%Continue button%%' OR error ILIKE '%%Email field%%'
           OR error ILIKE '%%login/verify%%' THEN 'EMAIL'
      WHEN error ILIKE '%%Could not navigate to payment%%'
           OR error ILIKE '%%Stripe payment form%%' THEN 'CHECKOUT'
      WHEN error ILIKE '%%Card field%%' OR error ILIKE '%%declined%%' THEN 'PAYMENT'
      WHEN error ILIKE '%%Corporate form%%' THEN 'CORPORATE'
      WHEN error ILIKE '%%OTP%%' OR error ILIKE '%%confirmation%%' THEN 'OTP'
      WHEN error ILIKE '%%Navigation failed%%' OR error ILIKE '%%Claim button%%' THEN 'START'
      ELSE 'OTHER'
    END
"""


def failure_by_stage(period=None):
    """Buyer failures bucketed by the STAGE of the funnel they died at — so you can see
    WHERE most tasks fail (email / checkout / payment / corporate / OTP). [{stage,count}]."""
    win = _win_clause(period)
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT {_STAGE_CASE} AS stage, COUNT(*) c
                  FROM tasks
                 WHERE status = ANY(%s){win}
                 GROUP BY stage ORDER BY c DESC
            """, [[ST_FAILED, ST_DECLINED, ST_INELIGIBLE, ST_UNCONFIRMED]])
            return [{"stage": r[0], "count": int(r[1])} for r in cur.fetchall()]
    except Exception:
        return []
    finally:
        conn.close()


def load_distribution(limit=1000):
    """Per-employee live load for the Load-Balancing view: how many instances are on each
    employee + its pending/running counts. Shows the balancer at work (and any hot emp).
    [{emp_id, instances, running, pending}] busiest first, plus an aggregate summary."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT emp_id,
                       COUNT(DISTINCT ran_by) FILTER (WHERE status = %s) AS instances,
                       COUNT(*) FILTER (WHERE status = %s) AS running,
                       COUNT(*) FILTER (WHERE status = %s) AS pending
                  FROM tasks
                 GROUP BY emp_id
                HAVING COUNT(*) FILTER (WHERE status IN (%s, %s)) > 0
                 ORDER BY instances DESC, pending DESC
                 LIMIT %s
            """, (ST_RUNNING, ST_RUNNING, ST_PENDING, ST_RUNNING, ST_PENDING, int(limit)))
            rows = [{"emp_id": r[0] or "(none)", "instances": int(r[1]),
                     "running": int(r[2]), "pending": int(r[3])} for r in cur.fetchall()]
        return rows
    except Exception:
        return []
    finally:
        conn.close()


def conversion_funnel(period=None):
    """Buyer pipeline funnel: how many tasks reached each stage and where they dropped.
    Returns ordered [{stage, reached, dropped, pct}] from Email -> ... -> Success, so the
    dashboard shows exactly WHERE the pipeline leaks. Filtered by period (all/today/...).
    Drops are attributed by the stage an error/outcome belongs to:
      Email   <- EMAIL/ELIGIBILITY/START failures + INELIGIBLE
      Checkout<- CHECKOUT failures
      Payment <- PAYMENT failures + DECLINED
      Corp    <- CORPORATE failures
      OTP     <- OTP/OTHER failures + UNCONFIRMED
    so the final 'reached' equals COMPLETED."""
    win = _win_clause(period)
    term = [ST_COMPLETED, ST_FAILED, ST_DECLINED, ST_INELIGIBLE, ST_UNCONFIRMED]
    params = {"c": ST_COMPLETED, "inel": ST_INELIGIBLE, "dec": ST_DECLINED,
              "unc": ST_UNCONFIRMED, "term": term}
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT
                  COUNT(*) AS total,
                  COUNT(*) FILTER (WHERE status=%(c)s) AS success,
                  COUNT(*) FILTER (WHERE status=%(inel)s
                     OR error ILIKE '%%not eligible%%' OR error ILIKE '%%ineligib%%'
                     OR error ILIKE '%%Continue button%%' OR error ILIKE '%%Email field%%'
                     OR error ILIKE '%%login/verify%%' OR error ILIKE '%%Navigation failed%%'
                     OR error ILIKE '%%Claim button%%') AS d_email,
                  COUNT(*) FILTER (WHERE error ILIKE '%%Could not navigate to payment%%'
                     OR error ILIKE '%%Stripe payment form%%') AS d_checkout,
                  COUNT(*) FILTER (WHERE status=%(dec)s
                     OR error ILIKE '%%Card field%%' OR error ILIKE '%%declined%%') AS d_payment,
                  COUNT(*) FILTER (WHERE error ILIKE '%%Corporate form%%') AS d_corp,
                  COUNT(*) FILTER (WHERE status=%(unc)s
                     OR error ILIKE '%%OTP%%' OR error ILIKE '%%confirmation%%') AS d_otp
                  FROM tasks
                 WHERE status = ANY(%(term)s){win}
            """, params)
            r = cur.fetchone() or [0]*7
            total, success = int(r[0]), int(r[1])
            d = {"Email": int(r[2]), "Checkout": int(r[3]), "Payment": int(r[4]),
                 "Corporate": int(r[5]), "OTP": int(r[6])}
        order = ["Email", "Checkout", "Payment", "Corporate", "OTP"]
        out, reached = [], total
        for st in order:
            dropped = d[st]
            out.append({"stage": st, "reached": reached, "dropped": dropped,
                        "pct": round(reached / total * 100, 1) if total else 0.0})
            reached = max(0, reached - dropped)
        out.append({"stage": "Success", "reached": max(reached, success), "dropped": 0,
                    "pct": round(max(reached, success) / total * 100, 1) if total else 0.0})
        return out
    except Exception:
        return []
    finally:
        conn.close()


def hourly_trend(hours=24):
    """Per-hour buyer throughput + success rate for the last N hours (sparklines/trends).
    [{hour 'HH:00', done, success, rate}] oldest->newest. Empty hours are omitted (the
    sparkline just shows the hours that had activity)."""
    term = [ST_COMPLETED, ST_FAILED, ST_DECLINED, ST_INELIGIBLE, ST_UNCONFIRMED]
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT to_char(date_trunc('hour', updated_at), 'HH24:00') AS h,
                       COUNT(*) AS done,
                       COUNT(*) FILTER (WHERE status=%s) AS success
                  FROM tasks
                 WHERE status = ANY(%s)
                   AND updated_at > now() - (%s || ' hours')::interval
                 GROUP BY date_trunc('hour', updated_at)
                 ORDER BY date_trunc('hour', updated_at)
            """, (ST_COMPLETED, term, str(int(hours))))
            return [{"hour": r[0], "done": int(r[1]), "success": int(r[2]),
                     "rate": round(int(r[2]) / int(r[1]) * 100, 1) if r[1] else 0.0}
                    for r in cur.fetchall()]
    except Exception:
        return []
    finally:
        conn.close()


def _throughput(table, done_statuses, left_statuses):
    """Generic throughput/ETA: finished in the last hour => rate/hr => ETA for what's
    left. Returns {done_1h, rate_hr, left, eta_min}."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT COUNT(*) FROM {table}
                 WHERE status = ANY(%s) AND updated_at > now() - interval '1 hour'
            """, (list(done_statuses),))
            done_1h = int(cur.fetchone()[0])
            cur.execute(f"SELECT COUNT(*) FROM {table} WHERE status = ANY(%s)",
                        (list(left_statuses),))
            left = int(cur.fetchone()[0])
        rate = done_1h  # per hour
        eta_min = int(round(left / rate * 60)) if rate else None
        return {"done_1h": done_1h, "rate_hr": rate, "left": left, "eta_min": eta_min}
    except Exception:
        return {"done_1h": 0, "rate_hr": 0, "left": 0, "eta_min": None}
    finally:
        conn.close()


def throughput_stats():
    """BUYER throughput/ETA (completed/finished per hour + ETA to clear pending)."""
    return _throughput("tasks",
        (ST_COMPLETED, ST_FAILED, ST_DECLINED, ST_INELIGIBLE, ST_UNCONFIRMED),
        (ST_PENDING, ST_RUNNING))


def read_throughput_stats():
    """READER throughput/ETA + books read in the last hour."""
    base = _throughput("read_tasks", (ST_DONE, ST_FAILED), (ST_PENDING, ST_RUNNING, ST_RETRY))
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT COALESCE(SUM(books_read),0) FROM read_tasks
                 WHERE updated_at > now() - interval '1 hour'
            """)
            base["books_1h"] = int(cur.fetchone()[0])
    except Exception:
        base["books_1h"] = 0
    finally:
        conn.close()
    return base


def proxy_health(limit=15):
    """Per proxy-IP buyer outcomes — spot blocked/declining exit IPs.
    [{proxy_ip, total, success, declined, failed, rate}] worst first."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            # The GROUP BY is wrapped in a subquery so `success`/`total` are real
            # columns by the time ORDER BY sees them. Postgres accepts an output
            # alias in ORDER BY only as a BARE name — inside an expression like
            # `success::numeric / total` it resolves against the INPUT columns and
            # errors with 'column "success" does not exist'. This function had
            # therefore never returned a row; `except Exception: return []` below
            # turned that into a permanently-empty panel instead of a crash.
            cur.execute(f"""
                SELECT ip, total, success, declined, failed
                  FROM (
                    SELECT COALESCE(NULLIF(TRIM(proxy_ip),''),'(none)') ip,
                           COUNT(*) total,
                           COUNT(*) FILTER (WHERE status=%s) success,
                           COUNT(*) FILTER (WHERE status=%s) declined,
                           COUNT(*) FILTER (WHERE status=%s) failed
                      FROM tasks
                     WHERE status IN (%s,%s,%s,%s,%s)
                     GROUP BY ip HAVING COUNT(*) >= 2
                  ) x
                 ORDER BY success::numeric / total ASC, total DESC
                 LIMIT %s
            """, (ST_COMPLETED, ST_DECLINED, ST_FAILED,
                  ST_COMPLETED, ST_FAILED, ST_DECLINED, ST_INELIGIBLE, ST_UNCONFIRMED,
                  int(limit)))
            out = []
            for r in cur.fetchall():
                tot = int(r[1])
                out.append({"proxy_ip": r[0], "total": tot, "success": int(r[2]),
                            "declined": int(r[3]), "failed": int(r[4]),
                            "rate": round(int(r[2]) / tot * 100, 1) if tot else 0.0})
            return out
    except Exception:
        return []
    finally:
        conn.close()


def card_bin_health(limit=15):
    """Per card BIN (first 6 digits) buyer outcomes — find bad card batches.
    [{bin, total, success, declined, rate}] worst first."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            # card_no now lives on `cards`, reached via tasks.card_id (migration 0003).
            # Also wrapped in a subquery: the old ORDER BY used the output alias
            # `success` inside an expression, which Postgres rejects — see the note in
            # proxy_health(). This function had never returned a row either.
            cur.execute(f"""
                SELECT bin, total, success, declined
                  FROM (
                    SELECT LEFT(regexp_replace(COALESCE(c.card_no,''),'\\D','','g'),6) bin,
                           COUNT(*) total,
                           COUNT(*) FILTER (WHERE t.status=%s) success,
                           COUNT(*) FILTER (WHERE t.status=%s) declined
                      FROM tasks t
                      JOIN cards c ON c.id = t.card_id
                     WHERE t.status IN (%s,%s,%s,%s,%s) AND c.card_no IS NOT NULL
                     GROUP BY bin
                    HAVING COUNT(*) >= 2
                  ) x
                 -- LENGTH(bin) is filtered HERE, not in HAVING: `bin` is an output
                 -- alias, and HAVING resolves against INPUT columns (same rule that
                 -- broke the ORDER BY). In the outer query it is a real column.
                 WHERE LENGTH(bin) = 6
                 ORDER BY success::numeric / total ASC, total DESC
                 LIMIT %s
            """, (ST_COMPLETED, ST_DECLINED,
                  ST_COMPLETED, ST_FAILED, ST_DECLINED, ST_INELIGIBLE, ST_UNCONFIRMED,
                  int(limit)))
            out = []
            for r in cur.fetchall():
                tot = int(r[1])
                out.append({"bin": r[0], "total": tot, "success": int(r[2]),
                            "declined": int(r[3]),
                            "rate": round(int(r[2]) / tot * 100, 1) if tot else 0.0})
            return out
    except Exception:
        return []
    finally:
        conn.close()


# Same stage attribution as conversion_funnel(), used to break a funnel stage into its
# top error reasons (funnel drill-down).
_FUNNEL_STAGE_CASE = """
    CASE
      WHEN status=%(inel)s OR error ILIKE '%%not eligible%%' OR error ILIKE '%%ineligib%%'
        OR error ILIKE '%%Continue button%%' OR error ILIKE '%%Email field%%'
        OR error ILIKE '%%login/verify%%' OR error ILIKE '%%Navigation failed%%'
        OR error ILIKE '%%Claim button%%' THEN 'Email'
      WHEN error ILIKE '%%Could not navigate to payment%%'
        OR error ILIKE '%%Stripe payment form%%' THEN 'Checkout'
      WHEN status=%(dec)s OR error ILIKE '%%Card field%%' OR error ILIKE '%%declined%%' THEN 'Payment'
      WHEN error ILIKE '%%Corporate form%%' THEN 'Corporate'
      WHEN status=%(unc)s OR error ILIKE '%%OTP%%' OR error ILIKE '%%confirmation%%' THEN 'OTP'
      ELSE 'Other'
    END
"""


def stage_reasons(period=None, per_stage=6):
    """Top error reasons WITHIN each funnel stage (for the funnel drill-down: click a
    stage to see what's killing it). Returns {stage: [{reason, count}]} with the same
    stage attribution as conversion_funnel(). Filtered by period."""
    win = _win_clause(period)
    params = {"term": [ST_FAILED, ST_DECLINED, ST_INELIGIBLE, ST_UNCONFIRMED],
              "inel": ST_INELIGIBLE, "dec": ST_DECLINED, "unc": ST_UNCONFIRMED}
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT {_FUNNEL_STAGE_CASE} AS stage, {_REASON_SQL} AS reason, COUNT(*) c
                  FROM tasks WHERE status = ANY(%(term)s){win}
                 GROUP BY stage, reason ORDER BY c DESC
            """, params)
            out = {}
            for stage, reason, c in cur.fetchall():
                out.setdefault(stage, [])
                if len(out[stage]) < per_stage:
                    out[stage].append({"reason": reason or "(no message)", "count": int(c)})
        return out
    except Exception:
        return {}
    finally:
        conn.close()


def card_economics():
    """Card-spend efficiency: distinct cards tried, how many ever got a success vs only
    ever got declined ('burned' = wasted), and success-per-card. Spot wasted card money.
    {cards, cards_success, cards_burned, total_success, total_declined,
     success_per_card, burn_rate}."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            # card_no now lives on `cards`, reached via tasks.card_id (migration 0003).
            cur.execute("""
                WITH per_card AS (
                    SELECT c.card_no,
                           COUNT(*) FILTER (WHERE t.status=%s) AS succ,
                           COUNT(*) FILTER (WHERE t.status=%s) AS decl
                      FROM tasks t
                      JOIN cards c ON c.id = t.card_id
                     WHERE c.card_no IS NOT NULL AND c.card_no <> ''
                       AND t.status IN (%s,%s,%s,%s,%s)
                     GROUP BY c.card_no
                )
                SELECT COUNT(*) AS cards,
                       COUNT(*) FILTER (WHERE succ>0) AS cards_success,
                       COUNT(*) FILTER (WHERE succ=0 AND decl>0) AS cards_burned,
                       COALESCE(SUM(succ),0) AS total_success,
                       COALESCE(SUM(decl),0) AS total_declined
                  FROM per_card
            """, (ST_COMPLETED, ST_DECLINED, ST_COMPLETED, ST_FAILED, ST_DECLINED,
                  ST_INELIGIBLE, ST_UNCONFIRMED))
            r = cur.fetchone() or [0, 0, 0, 0, 0]
            cards = int(r[0])
            return {"cards": cards, "cards_success": int(r[1]), "cards_burned": int(r[2]),
                    "total_success": int(r[3]), "total_declined": int(r[4]),
                    "success_per_card": round(int(r[3]) / cards, 2) if cards else 0.0,
                    "burn_rate": round(int(r[2]) / cards * 100, 1) if cards else 0.0}
    except Exception:
        return {}
    finally:
        conn.close()


def employee_health(min_total=3, window_hours=6):
    """Per-employee BUYER health score for spotting DYING employees early.
    success/decline/inelig rates + OTP consecutive failures + a flag:
      ok | watch | dying   (dying => replace this emp_id). Worst first.

    RECENT WINDOW (default 6h): the rate is computed only over the last `window_hours` of
    activity, NOT all-time — so an employee that was failing but has RECOVERED (OTPs flowing
    again) drops back to 'ok' and its alert CLEARS, instead of a stale cumulative rate keeping
    a dead alert forever. Set window_hours=0 for the old all-time behaviour."""
    conn = _conn()
    try:
        import psycopg2.extras
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        # Window BOTH signals: the success RATE (tasks in window) AND the OTP-fail streak
        # (only a RECENT streak counts). Without windowing the streak, `otp_fails >= 3` keeps
        # an idled/replaced employee flagged 'dying' forever even after full recovery — the
        # alert would never clear.
        if not window_hours:
            _joinwin, _win = "", ""
            _params = [ST_COMPLETED, ST_DECLINED, ST_INELIGIBLE, ST_PENDING, ST_RUNNING]
        else:
            _joinwin = "AND oa.last_failure >= now() - (%s || ' hours')::interval"
            _win = "WHERE t.updated_at >= now() - (%s || ' hours')::interval"
            _params = [ST_COMPLETED, ST_DECLINED, ST_INELIGIBLE, ST_PENDING, ST_RUNNING,
                       int(window_hours), int(window_hours)]
        cur.execute(f"""
            SELECT t.emp_id,
                   COUNT(*) total,
                   COUNT(*) FILTER (WHERE status=%s) success,
                   COUNT(*) FILTER (WHERE status=%s) declined,
                   COUNT(*) FILTER (WHERE status=%s) inelig,
                   COUNT(*) FILTER (WHERE status IN (%s,%s)) pending,
                   COALESCE(MAX(oa.consecutive_failures),0) otp_fails
              FROM tasks t
              LEFT JOIN otp_alerts oa ON oa.emp_id = t.emp_id {_joinwin}
              {_win}
             GROUP BY t.emp_id
        """, _params)
        out = []
        for r in cur.fetchall():
            tot = int(r["total"]); fin = tot - int(r["pending"])
            succ = int(r["success"])
            rate = round(succ / fin * 100, 1) if fin else 0.0
            otp_fails = int(r["otp_fails"])
            # flag: dying if enough finished AND (very low success OR repeated OTP fails)
            flag = "ok"
            if fin >= min_total:
                if rate < 20 or otp_fails >= 3:
                    flag = "dying"
                elif rate < 50 or otp_fails == 2:
                    flag = "watch"
            out.append({"emp_id": r["emp_id"] or "(none)", "total": tot,
                        "success": succ, "declined": int(r["declined"]),
                        "inelig": int(r["inelig"]), "pending": int(r["pending"]),
                        "otp_fails": otp_fails, "rate": rate, "flag": flag})
        cur.close()
        order = {"dying": 0, "watch": 1, "ok": 2}
        return sorted(out, key=lambda x: (order.get(x["flag"], 3), x["rate"]))
    except Exception:
        return []
    finally:
        conn.close()


def read_instance_status():
    """Per-instance READER status from read_tasks (mirror of instance_status for the
    reader): [{id, done, success, failed, active, current_email, books, proxy_ip?}]."""
    terminal = (ST_DONE, ST_FAILED)
    conn = _conn()
    try:
        import psycopg2.extras
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""
            SELECT ran_by, status, COUNT(*) c, COALESCE(SUM(books_read),0) books
              FROM read_tasks WHERE ran_by IS NOT NULL GROUP BY ran_by, status
        """)
        inst = {}
        for r in cur.fetchall():
            rid = int(r["ran_by"])
            d = inst.setdefault(rid, {"id": rid, "done": 0, "success": 0, "failed": 0,
                                      "active": False, "current_email": "test@example.com", "books": 0})
            st, c = r["status"], int(r["c"])
            d["books"] += int(r["books"])
            if st in terminal:
                d["done"] += c
                if st == ST_DONE: d["success"] += c
                elif st == ST_FAILED: d["failed"] += c
        cur.execute("""
            SELECT DISTINCT ON (ran_by) ran_by, email
              FROM read_tasks WHERE status = %s AND ran_by IS NOT NULL
             ORDER BY ran_by, updated_at DESC
        """, (ST_RUNNING,))
        for r in cur.fetchall():
            rid = int(r["ran_by"])
            d = inst.setdefault(rid, {"id": rid, "done": 0, "success": 0, "failed": 0,
                                      "active": False, "current_email": "test@example.com", "books": 0})
            d["active"] = True
            d["current_email"] = r["email"] or ""
        cur.close()
        return [inst[k] for k in sorted(inst)]
    except Exception:
        return []
    finally:
        conn.close()


# ============================================================================
# Telegram OTP provider — config (migration 011)
#
# Two tables on purpose: telegram_accounts is CAPACITY (one account = one purchase at a
# time, because a Telethon session is one chat), telegram_sources is the VENDOR (which
# bot/channel, and its menu profile). Adding bots does not add speed; adding accounts
# does. See schema.py for the longer note.
# ============================================================================

_TG_ACCOUNT_FIELDS = ("label", "phone", "api_id", "api_hash", "session_file",
                      "enabled", "note")
_TG_SOURCE_FIELDS = ("label", "account_id", "kind", "target", "service_command",
                     "profile", "priority", "enabled")


def _iso(row, *keys):
    for k in keys:
        if row.get(k) is not None:
            row[k] = row[k].isoformat()
    return row


def telegram_accounts(include_disabled=True):
    """Saare accounts, source ki ginti ke saath — page par 'kitne bot isse jude hain'."""
    conn = _conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT a.*, (SELECT count(*) FROM telegram_sources s
                              WHERE s.account_id = a.id) AS source_count
                  FROM telegram_accounts a
                 WHERE (%s OR a.enabled)
                 ORDER BY a.label
            """, (bool(include_disabled),))
            return [_iso(dict(r), "busy_until", "last_used_at", "created_at")
                    for r in cur.fetchall()]
    finally:
        conn.close()


def save_telegram_account(data, account_id=None):
    """Naya account banao ya purana update karo. Sirf wahi columns chhuye jaate hain jo
    bheje gaye hain — session_file/session_ok galti se mit na jaayein."""
    fields = {k: data[k] for k in _TG_ACCOUNT_FIELDS if k in data}
    if not fields:
        raise ValueError("kuch bhi save karne ko nahi mila")
    conn = _conn()
    try:
        with conn.cursor() as cur:
            if account_id:
                sets = ", ".join(f"{k} = %s" for k in fields)
                cur.execute(f"UPDATE telegram_accounts SET {sets} WHERE id = %s RETURNING id",
                            list(fields.values()) + [int(account_id)])
            else:
                cols = ", ".join(fields)
                marks = ", ".join(["%s"] * len(fields))
                cur.execute(f"INSERT INTO telegram_accounts ({cols}) VALUES ({marks}) "
                            f"RETURNING id", list(fields.values()))
            row = cur.fetchone()
        conn.commit()
        return int(row[0]) if row else None
    finally:
        conn.close()


def delete_telegram_account(account_id):
    """Account tabhi hatega jab uspe koi source na ho — warna source anaath ho jaate."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM telegram_sources WHERE account_id = %s",
                        (int(account_id),))
            n = int(cur.fetchone()[0])
            if n:
                raise ValueError(f"pehle iske {n} source hatao ya kisi aur account par le jao")
            cur.execute("DELETE FROM telegram_accounts WHERE id = %s", (int(account_id),))
        conn.commit()
        return True
    finally:
        conn.close()


def telegram_sources(include_disabled=True, labels=None):
    """Sources + unke account ka naam. `labels` do to sirf wahi (Settings me chune hue)."""
    conn = _conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT s.*, a.label AS account_label, a.phone AS account_phone,
                       a.enabled AS account_enabled, a.session_ok
                  FROM telegram_sources s
                  JOIN telegram_accounts a ON a.id = s.account_id
                 WHERE (%s OR (s.enabled AND a.enabled))
                   AND (%s::text[] IS NULL OR s.label = ANY(%s::text[]))
                 ORDER BY s.priority, s.label
            """, (bool(include_disabled), labels, labels))
            return [_iso(dict(r), "last_used_at", "created_at") for r in cur.fetchall()]
    finally:
        conn.close()


def save_telegram_source(data, source_id=None):
    fields = {k: data[k] for k in _TG_SOURCE_FIELDS if k in data}
    if "profile" in fields and fields["profile"] is not None:
        fields["profile"] = psycopg2.extras.Json(fields["profile"])
    if not fields:
        raise ValueError("kuch bhi save karne ko nahi mila")
    conn = _conn()
    try:
        with conn.cursor() as cur:
            if source_id:
                sets = ", ".join(f"{k} = %s" for k in fields)
                cur.execute(f"UPDATE telegram_sources SET {sets} WHERE id = %s RETURNING id",
                            list(fields.values()) + [int(source_id)])
            else:
                cols = ", ".join(fields)
                marks = ", ".join(["%s"] * len(fields))
                cur.execute(f"INSERT INTO telegram_sources ({cols}) VALUES ({marks}) "
                            f"RETURNING id", list(fields.values()))
            row = cur.fetchone()
        conn.commit()
        return int(row[0]) if row else None
    finally:
        conn.close()


def delete_telegram_source(source_id):
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM telegram_sources WHERE id = %s", (int(source_id),))
        conn.commit()
        return True
    finally:
        conn.close()
