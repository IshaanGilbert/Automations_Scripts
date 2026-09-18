#!/usr/bin/env python3
"""One-off: import ALREADY-MADE real cards from a CSV straight into the pool as 'unused'
(ready to use — no portal generation), tagged with a corporate. Dedups on card_no, so
re-running is safe. Reads DB creds from the box's own config (db._conn), so run it on the
server:  sudo ./venv/bin/python import_cards_now.py cards_streakads.csv streakads
CSV columns (no header needed): card_no, expiry, cvv, max_amount
"""
import sys, csv
import db

CSV = sys.argv[1] if len(sys.argv) > 1 else "cards_streakads.csv"
CORP = sys.argv[2] if len(sys.argv) > 2 else "streakads"

conn = db._conn()
try:
    cur = conn.cursor()
    # make sure the corp-tag column + dedup index exist (idempotent — no-op if already there,
    # so this works even if migration 0013 hasn't been applied yet)
    cur.execute("ALTER TABLE cards ADD COLUMN IF NOT EXISTS corp_id text")
    cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_cards_no ON cards(card_no) WHERE card_no IS NOT NULL")
    conn.commit()
    cur.execute("SELECT id, COALESCE(name,'') FROM campaigns WHERE status='active' ORDER BY id LIMIT 1")
    row = cur.fetchone()
    if not row:
        print("no active campaign — create/activate one first, nothing imported.")
        sys.exit(1)
    cid, cname = row
    # dedup set: every card number already in the pool (global unique index)
    cur.execute("SELECT card_no FROM cards WHERE card_no IS NOT NULL")
    existing = {r[0] for r in cur.fetchall()}
    # existing EMPTY 'requested' slots already tagged for this corp — FILL THESE FIRST
    # (user rule: "streakads ke requested slots hain, unhi me add karo"), oldest first.
    cur.execute("SELECT id FROM cards WHERE campaign_id=%s AND corp_id=%s AND status='requested' "
                "AND card_no IS NULL ORDER BY id", (cid, CORP))
    slots = [r[0] for r in cur.fetchall()]
    filled = inserted = skipped = 0
    si = 0
    with open(CSV, newline="") as f:
        for rec in csv.reader(f):
            if not rec:
                continue
            cn = "".join(ch for ch in (rec[0] or "") if ch.isdigit())
            if len(cn) not in (15, 16) or cn in existing:
                skipped += 1                        # invalid or duplicate card_no
                continue
            existing.add(cn)
            ex = (rec[1] if len(rec) > 1 else "").strip()
            cv = "".join(ch for ch in (rec[2] if len(rec) > 2 else "") if ch.isdigit())
            mx = (rec[3] if len(rec) > 3 else "").strip()
            try:
                mx = float(mx) if mx else None
            except Exception:
                mx = None
            if si < len(slots):                     # fill an existing requested slot
                cur.execute("""UPDATE cards SET card_no=%s, expiry=%s, cvv=%s, max_amount=%s,
                                     status='unused', generated_at=now(), updated_at=now()
                               WHERE id=%s AND status='requested'""",
                            (cn, ex, cv, mx, slots[si]))
                si += 1
                filled += 1
            else:                                   # no slot left — add as a fresh unused card
                cur.execute("""INSERT INTO cards (campaign_id, corp_id, card_no, expiry, cvv,
                                     max_amount, status, generated_at)
                               VALUES (%s,%s,%s,%s,%s,%s,'unused', now())
                               ON CONFLICT (card_no) WHERE card_no IS NOT NULL DO NOTHING""",
                            (cid, CORP, cn, ex, cv, mx))
                inserted += cur.rowcount
    conn.commit()
    cur.execute("SELECT count(*) FROM cards WHERE corp_id=%s AND status='unused'", (CORP,))
    ready = cur.fetchone()[0]
    left = len(slots) - si
    print(f"campaign '{cname}' (id {cid}) — {CORP}:")
    print(f"  filled existing requested slots : {filled}")
    print(f"  added as new unused cards       : {inserted}")
    print(f"  skipped (dupes/invalid)         : {skipped}")
    if left > 0:
        print(f"  still-empty requested slots left: {left} (fewer cards than requested slots)")
    print(f"  {CORP} unused cards now ready    : {ready}")
finally:
    conn.close()
