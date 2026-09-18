#!/usr/bin/env python3
"""Seed the LOCAL dev database with realistic data.

    ./dev.sh seed

This is a DEV-ONLY fixture generator. It exists so the dashboard has something to
render + exercise the automation. It seeds a campaign the same way the
eventually do for real:

  - a monthly campaign with a computed daily plan
  - a card pool part-filled by the "card_generation agent"
  - an identity pool drawn from the first x last name space
  - completed/failed/declined transactions spread over the last few days
  - reader rows promoted from completed transactions, with the §6.7 audit trail

REFUSES TO RUN against anything that isn't a local dev DB — see _assert_dev_db().
Nothing here is imported by the bots or the controller.
"""

import os
import random
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import psycopg2  # noqa: E402

# Deterministic: a re-seed produces the same data, so a dashboard bug is reproducible.
random.seed(20260717)

ACCOUNT_PASSWORD = "CHANGE_ME_PASSWORD"

FIRST = ["Amit", "Rahul", "Priya", "Sneha", "Vikas", "Neha", "Rohan", "Pooja",
         "Arjun", "Kavya", "Manish", "Divya", "Sanjay", "Anita", "Karan", "Meera",
         "Rajesh", "Swati", "Nikhil", "Ritu", "Aditya", "Isha", "Varun", "Tanya",
         "Gaurav", "Nisha", "Deepak", "Payal", "Suresh", "Alka", "Vivek", "Rekha",
         "Ashok", "Sonia", "Harsh", "Preeti", "Yash", "Simran", "Kunal", "Jaya"]
LAST = ["Sharma", "Singh", "Kumar", "Verma", "Gupta", "Yadav", "Patel", "Jain",
        "Mishra", "Reddy", "Nair", "Bose", "Chopra", "Malhotra", "Iyer", "Desai",
        "Kapoor", "Joshi", "Rao", "Menon", "Agarwal", "Bhatt", "Chauhan", "Das",
        "Ghosh", "Khanna", "Mehta", "Pillai", "Saxena", "Trivedi", "Bansal", "Dubey",
        "Goyal", "Sethi", "Sinha", "Rana", "Tiwari", "Naik", "Chawla", "Bajaj"]
EMPS = ["STREAKADS1", "STREAKADS2", "STREAKADS3"]
BINS = ["541200", "541333", "552011"]          # 3 batches, one deliberately bad
PROXIES = ["103.14.22.7", "103.14.22.19", "45.118.9.204", "45.118.9.88"]
ERRORS = ["Card declined by issuer", "OTP timeout", "Corporate form not found",
          "Checkout timeout", "Not eligible for this offer"]


def _assert_dev_db(dsn: str) -> None:
    """Never let this run anywhere but a local dev database."""
    bad = []
    if "localhost" not in dsn and "127.0.0.1" not in dsn:
        bad.append("host is not localhost")
    if "magzter_dev" not in dsn:
        bad.append("database is not named magzter_dev")
    if "51.222.20.8" in dsn:
        bad.append("this is the PRODUCTION host")
    if bad:
        sys.exit(
            "REFUSING TO SEED — this does not look like a local dev DB:\n"
            + "".join(f"  - {b}\n" for b in bad)
            + f"  dsn: {dsn}\n\n"
            "seed_dev.py writes thousands of fake rows. Point DATABASE_URL at the dev\n"
            "database (./dev.sh up) and try again."
        )


def main() -> None:
    dsn = os.environ.get("DATABASE_URL", "")
    if not dsn:
        sys.exit("DATABASE_URL is not set — run this via ./dev.sh seed")
    _assert_dev_db(dsn)

    conn = psycopg2.connect(dsn)
    conn.autocommit = False
    cur = conn.cursor()

    # Idempotent: wipe in FK-safe order so re-seeding is repeatable.
    cur.execute("""
        TRUNCATE card_attempts, read_tasks, tasks, cards, identities,
                 emails, first_names, last_names, campaign_days, campaigns
                 RESTART IDENTITY CASCADE
    """)

    # ---- name pools -------------------------------------------------------
    cur.executemany("INSERT INTO first_names (name) VALUES (%s)", [(n,) for n in FIRST])
    cur.executemany("INSERT INTO last_names (name) VALUES (%s)", [(n,) for n in LAST])

    # ---- emails -----------------------------------------------------------
    emails = [(f"user{i:04d}@example.com", ACCOUNT_PASSWORD) for i in range(1, 121)]
    cur.executemany("INSERT INTO emails (email, password) VALUES (%s,%s)", emails)
    cur.execute("SELECT id FROM emails ORDER BY id")
    email_ids = [r[0] for r in cur.fetchall()]

    today = datetime.now(timezone.utc).date()
    this_start = today.replace(day=1)
    this_end = (this_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    last_start = (this_start - timedelta(days=1)).replace(day=1)
    last_end = this_start - timedelta(days=1)

    # Seed TWO months so the campaign table shows history: last month (done) + this
    # month (active). Transactions are dated inside each campaign's own window.
    seed_campaign(cur, name=last_start.strftime("%B"), start=last_start, end=last_end,
                  status="done", budget=5000, filled=800, n_tx=340,
                  email_ids=email_ids, day_from=last_start, day_to=last_end)
    seed_campaign(cur, name=this_start.strftime("%B"), start=this_start, end=this_end,
                  status="active", budget=2000, filled=600, n_tx=190,
                  email_ids=email_ids, day_from=today, day_to=this_end)

    # an OTP alert so the red banner has something to show
    cur.execute("""
        INSERT INTO otp_alerts (emp_id, consecutive_failures, total_failures, last_failure)
        VALUES ('STREAKADS3', 4, 11, now() - interval '25 minutes')
        ON CONFLICT (emp_id) DO UPDATE SET consecutive_failures=EXCLUDED.consecutive_failures
    """)
    conn.commit()

    def one(q):
        cur.execute(q); return cur.fetchone()[0]
    print("seeded local dev DB:")
    cur.execute("SELECT name, status, budget FROM campaigns ORDER BY start_date")
    for nm, stt, bud in cur.fetchall():
        print(f"  campaign        {nm} ({stt}, budget {bud})")
    print(f"  cards           {one('SELECT count(*) FROM cards')}")
    print(f"  identities      {one('SELECT count(*) FROM identities')}  (capacity {len(FIRST)*len(LAST)})")
    print(f"  emails          {one('SELECT count(*) FROM emails')}")
    print(f"  tasks           {one('SELECT count(*) FROM tasks')}")
    print(f"  read_tasks      {one('SELECT count(*) FROM read_tasks')}")
    print(f"  card_attempts   {one('SELECT count(*) FROM card_attempts')}")
    conn.close()


def seed_campaign(cur, name, start, end, status, budget, filled, n_tx, email_ids,
                  day_from, day_to):
    """Seed one month's campaign with cards, identities, transactions and reads.
    Transactions are dated uniformly across [start, end] (or up to today for the
    active month). Identities are drawn from globally-unused name pairs."""
    cur.execute("""
        INSERT INTO campaigns (name, budget, buffer_days, start_date, end_date,
                               status, account_password, email_alert_days,
                               corp_id, employee_ids, backup_employee_ids)
        VALUES (%s,%s,5,%s,%s,%s,%s,2,'streakads',%s,%s) RETURNING id
    """, (name, budget, start, end, status, ACCOUNT_PASSWORD, EMPS, ["EMP999", "EMP888"]))
    campaign_id = cur.fetchone()[0]

    # even plan across day_from..day_to (buffer = last 5 days)
    span = (day_to - day_from).days + 1
    per = budget // max(1, span - 5)
    d = day_from
    for i in range(span):
        cur.execute("INSERT INTO campaign_days (campaign_id, day, planned) VALUES (%s,%s,%s)",
                    (campaign_id, d, per if i < span - 5 else 0))
        d = d + timedelta(days=1)

    # cards: budget slots, some filled by the "agent"
    cur.execute("INSERT INTO cards (campaign_id, status) "
                "SELECT %s,'requested' FROM generate_series(1,%s)", (campaign_id, budget - filled))
    rows = []
    for i in range(filled):
        bin_ = BINS[0] if i % 10 else (BINS[2] if i % 30 == 0 else BINS[1])
        rows.append((campaign_id, f"{bin_}{random.randint(0,9999999999):010d}",
                     f"{random.randint(1,12):02d}/{random.randint(27,31)}",
                     f"{random.randint(0,999):03d}", 500, "unused"))
    cur.executemany("""
        INSERT INTO cards (campaign_id, card_no, expiry, cvv, max_amount, status, generated_at)
        VALUES (%s,%s,%s,%s,%s,%s, %s::timestamptz - (random()*interval '5 days'))
    """, [(a, b, c, dd, e, f, str(end)) for (a, b, c, dd, e, f) in rows])

    # identities from globally-unused pairs
    cur.execute("""
        SELECT f.name, l.name FROM first_names f CROSS JOIN last_names l
         WHERE NOT EXISTS (SELECT 1 FROM identities i
                            WHERE i.first_name=f.name AND i.last_name=l.name)
         ORDER BY random() LIMIT %s
    """, (n_tx + 30,))
    pairs = cur.fetchall()
    cur.executemany("""
        INSERT INTO identities (campaign_id, first_name, last_name, email_id, status)
        VALUES (%s,%s,%s,%s,'unused') ON CONFLICT (first_name, last_name) DO NOTHING
    """, [(campaign_id, f, l, random.choice(email_ids)) for f, l in pairs])

    cur.execute("SELECT id FROM cards WHERE campaign_id=%s AND status='unused' ORDER BY id", (campaign_id,))
    card_ids = [r[0] for r in cur.fetchall()]
    cur.execute("SELECT id FROM identities WHERE campaign_id=%s AND status='unused' ORDER BY id", (campaign_id,))
    ident_ids = [r[0] for r in cur.fetchall()]

    n = min(len(card_ids), len(ident_ids), n_tx)
    outcomes = ["completed"] * 22 + ["failed"] * 5 + ["declined"] * 4 + ["ineligible"] * 2 + ["unconfirmed"] * 1
    span_days = max(1, (day_to - day_from).days)
    for i in range(n):
        cid, iid = card_ids[i], ident_ids[i]
        st = random.choice(outcomes)
        day = day_from + timedelta(days=random.randint(0, span_days))
        ts = datetime(day.year, day.month, day.day, random.randint(0, 22),
                      random.randint(0, 59), tzinfo=timezone.utc)
        cur.execute("""
            INSERT INTO tasks (card_id, identity_id, campaign_id, corp_id, emp_id, status,
                               ran_by, proxy_ip, duration_sec, error, transaction_id,
                               claimed_at, updated_at)
            VALUES (%s,%s,%s,'streakads',%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id
        """, (cid, iid, campaign_id, random.choice(EMPS), st, random.randint(1, 8),
              random.choice(PROXIES), round(random.uniform(45, 260), 1),
              "" if st == "completed" else random.choice(ERRORS),
              f"txn_{campaign_id}{i:05d}" if st == "completed" else None,
              ts - timedelta(seconds=200), ts))
        task_id = cur.fetchone()[0]
        cstatus, outcome = {
            "completed": ("used", "success"), "declined": ("payment_failed", "hard_decline"),
            "unconfirmed": ("reserved", "ambiguous"),
        }.get(st, ("used", "soft_fail"))
        cur.execute("UPDATE cards SET status=%s, used_at=%s, attempts=1 WHERE id=%s", (cstatus, ts, cid))
        cur.execute("UPDATE identities SET status='used', used_at=%s WHERE id=%s", (ts, iid))
        cur.execute("INSERT INTO card_attempts (card_id, task_id, outcome, error, created_at) "
                    "VALUES (%s,%s,%s,%s,%s)",
                    (cid, task_id, outcome, None if outcome == "success" else random.choice(ERRORS), ts))
        cur.execute("UPDATE emails SET times_used=times_used+1 WHERE id="
                    "(SELECT email_id FROM identities WHERE id=%s)", (iid,))

    # promote ~60% of completed to reads, mark ~70% of those done
    cur.execute("""
        WITH picked AS (
            SELECT t.id, i.first_name, i.last_name, i.email_id, t.updated_email,
                   t.campaign_id, t.transaction_id, t.updated_at
              FROM tasks t JOIN identities i ON i.id=t.identity_id
             WHERE t.campaign_id=%s AND t.status='completed' AND t.read_request=FALSE
             ORDER BY t.id
             LIMIT (SELECT GREATEST(1,(count(*)*6)/10) FROM tasks WHERE campaign_id=%s AND status='completed')
        ), ins AS (
            INSERT INTO read_tasks (email, password, name_used, source_task_id, status,
                                    transaction_id, transaction_at)
            SELECT COALESCE(p.updated_email,e.email), q.account_password,
                   p.first_name||' '||p.last_name, p.id, 'pending', p.transaction_id, p.updated_at
              FROM picked p JOIN emails e ON e.id=p.email_id JOIN campaigns q ON q.id=p.campaign_id
            ON CONFLICT (source_task_id) DO NOTHING RETURNING source_task_id
        )
        UPDATE tasks SET read_request=TRUE WHERE id IN (SELECT source_task_id FROM ins)
    """, (campaign_id, campaign_id))
    cur.execute("""
        UPDATE read_tasks SET status='done', books_read=2+(random()*6)::int,
               duration_sec=120+(random()*400)::int,
               read_at=transaction_at+interval '1 hour'+(random()*interval '5 hours'),
               proxy_ip=(ARRAY['103.14.22.7','103.14.22.19','45.118.9.204'])[1+floor(random()*3)],
               ran_by=1+floor(random()*4)
         WHERE source_task_id IN (SELECT id FROM tasks WHERE campaign_id=%s)
           AND id IN (SELECT id FROM read_tasks WHERE source_task_id IN
                      (SELECT id FROM tasks WHERE campaign_id=%s) ORDER BY id
                      LIMIT (SELECT (count(*)*7)/10 FROM read_tasks rt JOIN tasks t ON t.id=rt.source_task_id
                             WHERE t.campaign_id=%s))
    """, (campaign_id, campaign_id, campaign_id))


if __name__ == "__main__":
    main()
