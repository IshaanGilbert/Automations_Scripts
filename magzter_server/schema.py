"""SQLAlchemy Core metadata — the single source of truth for the DB schema.

THIS FILE IS FOR ALEMBIC ONLY. The runtime never imports it.

There are no ORM models, no sessions, no declarative_base here — only Core `Table`
objects, so `alembic revision --autogenerate` can diff the desired schema against a
live DB. Every query in db.py stays hand-written psycopg2 SQL, including the
concurrency-critical paths (_try_claim's SKIP LOCKED CTE, otp_lock's advisory lock,
retry_or_fail's single-statement CASE) which an ORM cannot express anyway.

This file must always describe the schema at alembic HEAD. If you add a migration,
update this file to match, then verify with:

    alembic revision --autogenerate -m "noop"

...which MUST produce an empty migration. If it doesn't, this file and the DB have
drifted — fix it before writing anything new. Delete the noop revision afterwards.

See docs/REVAMP_PLAN.md §3.
"""

from sqlalchemy import (
    ARRAY, BigInteger, Boolean, CheckConstraint, Column, Date, DateTime,
    ForeignKey, Index, Integer, MetaData, Numeric, Table, Text,
    UniqueConstraint, text,
)
from sqlalchemy.dialects.postgresql import JSONB

metadata = MetaData()

NOW = text("now()")


# ============================================================================
# Pre-existing tables (baseline, from db.py init_schema)
# ============================================================================

# The buyer's work queue AND the transaction record. `tasks` IS the transactions
# table — deliberately not renamed; ~200 call sites reference it.
#
# Slimmed by migration 003: card_no/month/cvv/email/first_name/last_name/name_used/
# password/rechecks moved out to cards/identities/quotas and are reached via FK.
# zip_code dropped by 004.
tasks = Table(
    "tasks", metadata,
    Column("id", BigInteger, primary_key=True),
    Column("corp_id", Text),
    Column("emp_id", Text),
    Column("status", Text, nullable=False, server_default="pending"),
    Column("ran_by", Integer),                      # instance id that owns/ran it
    Column("proxy_ip", Text),
    Column("duration_sec", Numeric),
    Column("error", Text),
    Column("transaction_id", Text),
    Column("claimed_at", DateTime(timezone=True)),
    Column("updated_at", DateTime(timezone=True), server_default=NOW),
    Column("retries", Integer, nullable=False, server_default="0"),
    Column("step", Text),                           # live progress: current step
    Column("step_at", DateTime(timezone=True)),     # ...and when it entered it
    Column("reassigned", Boolean, nullable=False, server_default=text("false")),
    # EMAIL MUTATION: an email that comes back "not eligible" is retried with a
    # mutated address. The identity's email stays canonical; updated_email holds the
    # one actually used. Kept pending review — the 1M identity pool may
    # make this unnecessary, but it is live behaviour in three buyers today.
    Column("updated_email", Text),
    Column("email_attempts", Integer, nullable=False, server_default="0"),

    # --- added by 002 ---
    # TRUE once this transaction has been handed to the reader (§6.5). The promoter
    # flips it; read_tasks.source_task_id is the real idempotency guarantee.
    Column("read_request", Boolean, nullable=False, server_default=text("false")),

    # --- added by 003: point at the inputs instead of copying them ---
    Column("card_id", BigInteger, ForeignKey("cards.id")),
    Column("identity_id", BigInteger, ForeignKey("identities.id")),
    Column("campaign_id", BigInteger, ForeignKey("campaigns.id")),

    Index("idx_tasks_status", "status"),
    Index("idx_tasks_emp", "emp_id"),
    # The promoter's hot path (§6.5): completed transactions not yet sent to read.
    Index("idx_tasks_readable", "id",
          postgresql_where=text("status = 'completed' AND read_request = false")),
    # THE hottest query in the new system — the daily quota gate (§6.1) runs on every
    # claim attempt, every instance, every server. Partial + ordered so it is a range
    # scan, not a full scan of a table growing 20k rows/month.
    Index("idx_tasks_settled_at", "updated_at",
          postgresql_where=text("status <> 'pending'")),
    # Transaction lookups from the dashboard / support.
    Index("idx_tasks_txid", "transaction_id",
          postgresql_where=text("transaction_id IS NOT NULL")),
    # Load-bearing: makes it structurally impossible to issue one card, or one
    # identity, to two transactions. Nothing prevents that today. Also the FK indexes.
    Index("uq_tasks_card", "card_id", unique=True,
          postgresql_where=text("card_id IS NOT NULL")),
    Index("uq_tasks_identity", "identity_id", unique=True,
          postgresql_where=text("identity_id IS NOT NULL")),
    # FK index — Postgres does not create these for you.
    Index("idx_tasks_campaign", "campaign_id"),
)


# One row per emp_id. consecutive_failures resets to 0 on an OTP success; the
# dashboard shows a red banner for any emp at/above the alert threshold.
otp_alerts = Table(
    "otp_alerts", metadata,
    Column("emp_id", Text, primary_key=True),
    Column("consecutive_failures", Integer, nullable=False, server_default="0"),
    Column("total_failures", Integer, nullable=False, server_default="0"),
    Column("last_failure", DateTime(timezone=True)),
    Column("updated_at", DateTime(timezone=True), server_default=NOW),
)


# The reader's work queue. Fed by the promoter from completed `tasks` (§6.5) once
# Phase 2 removes the readfile sheet.
read_tasks = Table(
    "read_tasks", metadata,
    Column("id", BigInteger, primary_key=True),
    Column("email", Text),
    Column("password", Text),                       # stamped from quotas.account_password
    Column("name_used", Text),
    Column("transaction_id", Text),
    Column("duration_sec", Numeric),
    Column("status", Text, nullable=False, server_default="pending"),
    Column("ran_by", Integer),
    Column("error", Text),
    Column("books_read", Integer, server_default="0"),
    Column("claimed_at", DateTime(timezone=True)),
    Column("updated_at", DateTime(timezone=True), server_default=NOW),
    Column("retries", Integer, nullable=False, server_default="0"),

    # --- added by 002 ---
    # Which transaction produced this account. Doubles as the promoter's idempotency
    # key and as the row's identity once Phase 2 drops sheet_row.
    Column("source_task_id", BigInteger, ForeignKey("tasks.id")),
    # Audit trail (§6.7): when bought, when read, from which IP.
    # transaction_date was TEXT (a raw sheet cell) and is replaced by transaction_at.
    Column("transaction_at", DateTime(timezone=True)),   # when the purchase happened
    Column("read_at", DateTime(timezone=True)),          # when reading finished
    Column("proxy_ip", Text),                            # which IP read it

    Index("idx_read_status", "status"),
    # One read_task per transaction, ever. Belt-and-braces with tasks.read_request:
    # read_request alone is not idempotent across a crash between INSERT and UPDATE.
    # Doubles as the FK index.
    #
    # NOT partial, deliberately: ON CONFLICT (source_task_id) cannot infer a partial
    # index, so the promoter (§6.5) would fail. NULLs are distinct in a Postgres
    # unique index anyway, so a WHERE clause would buy nothing.
    Index("uq_read_source", "source_task_id", unique=True),
    # Reader page sorts (§6.7): "read most recently", "bought on".
    Index("idx_read_read_at", "read_at"),
    Index("idx_read_transaction_at", "transaction_at"),
)


# Global flags. Every bot polls `paused` before claiming, so the operator can halt
# the fleet gracefully (running tasks finish, no new ones start).
system_state = Table(
    "system_state", metadata,
    Column("id", Integer, primary_key=True, autoincrement=False,
           server_default="1"),
    Column("paused", Boolean, nullable=False, server_default=text("false")),
    Column("reader_sync_paused", Boolean, nullable=False,
           server_default=text("false")),
    Column("note", Text),
    Column("updated_at", DateTime(timezone=True), server_default=NOW),
)


# ============================================================================
# Campaign-driven automation (migration 006) — see docs/REVAMP_PLAN.md §5, §6
# ============================================================================

# A CAMPAIGN is a monthly budget with a computed daily plan. budget is editable; the
# plan recomputes. campaign.budget is the cards target (cards never exceed it) and
# campaign_days.planned for TODAY is the daily transactions target the gate reads.
campaigns = Table(
    "campaigns", metadata,
    Column("id", BigInteger, primary_key=True),
    Column("name", Text, nullable=False),
    Column("budget", Integer, nullable=False),
    Column("buffer_days", Integer, nullable=False, server_default="5"),
    Column("start_date", Date, nullable=False),
    Column("end_date", Date, nullable=False),
    Column("status", Text, nullable=False, server_default="active"),  # active|paused|done
    Column("account_password", Text, nullable=False),
    # Alert when unused emails drop below this many DAYS of runway.
    Column("email_alert_days", Integer, nullable=False, server_default="2"),
    # Which employees this campaign runs on (added 007). corp_id is the corporate;
    # employee_ids are the primaries; backup_employee_ids are OTP-cooldown fallbacks.
    Column("corp_id", Text),
    Column("employee_ids", ARRAY(Text), nullable=False, server_default=text("'{}'")),
    Column("backup_employee_ids", ARRAY(Text), nullable=False,
           server_default=text("'{}'")),
    Column("created_at", DateTime(timezone=True), server_default=NOW),
    CheckConstraint("budget > 0", name="ck_campaigns_budget"),
    CheckConstraint("buffer_days >= 0", name="ck_campaigns_buffer"),
    CheckConstraint("end_date >= start_date", name="ck_campaigns_dates"),
    CheckConstraint("status IN ('active','paused','done')", name="ck_campaigns_status"),
    # One active campaign at a time — the gate needs an unambiguous "today's plan".
    Index("uq_campaign_active", "status", unique=True,
          postgresql_where=text("status = 'active'")),
)


# One row per date. planned = that day's target (editable). pinned = admin set it by
# hand, so rebalance leaves it and spreads the remaining budget over the other days.
campaign_days = Table(
    "campaign_days", metadata,
    Column("id", BigInteger, primary_key=True),
    Column("campaign_id", BigInteger,
           ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False),
    Column("day", Date, nullable=False),
    Column("planned", Integer, nullable=False, server_default="0"),
    Column("pinned", Boolean, nullable=False, server_default=text("false")),
    CheckConstraint("planned >= 0", name="ck_campaign_days_planned"),
    Index("uq_campaign_day", "campaign_id", "day", unique=True),
    Index("idx_campaign_days_day", "day"),
)


# Cards are pre-provisioned as SLOTS by a quota, then filled by the card_generation
# agent driving the MasterCard portal (§5.1). Setting a 20,000 quota inserts 20,000
# rows at status='requested' with card_no NULL — instant. Real numbers land later.
#
# status: requested -> generating -> unused -> reserved -> used | payment_failed
cards = Table(
    "cards", metadata,
    Column("id", BigInteger, primary_key=True),
    Column("campaign_id", BigInteger, ForeignKey("campaigns.id")),
    Column("card_no", Text),
    Column("expiry", Text),
    Column("cvv", Text),
    Column("max_amount", Numeric),
    Column("status", Text, nullable=False, server_default="requested"),
    Column("attempts", Integer, nullable=False, server_default="0"),
    # NO used_by_task column. "Which task used this card" is already expressed by
    # tasks.card_id + uq_tasks_card (unique), and is just as fast to query. A reverse
    # pointer here would be a second source of truth that can drift out of sync with
    # the first — and it created a circular FK dependency (cards -> tasks -> cards)
    # that SQLAlchemy cannot sort.
    Column("generated_at", DateTime(timezone=True)),
    Column("used_at", DateTime(timezone=True)),
    Column("claimed_at", DateTime(timezone=True)),
    Column("ran_by", Integer),
    Column("error", Text),
    Column("updated_at", DateTime(timezone=True), server_default=NOW),
    CheckConstraint(
        "status IN ('requested','generating','unused','reserved','used','payment_failed')",
        name="ck_cards_status"),
    Index("uq_cards_no", "card_no", unique=True,
          postgresql_where=text("card_no IS NOT NULL")),
    # Dashboard "pool health by status" groups on this.
    Index("idx_cards_status", "status"),
    Index("idx_cards_unused", "id", postgresql_where=text("status = 'unused'")),
    # The card_generation agent's claim path (§5.1).
    Index("idx_cards_requested", "id", postgresql_where=text("status = 'requested'")),
    # FK index — Postgres does not create these for you.
    Index("idx_cards_campaign", "campaign_id"),
)


emails = Table(
    "emails", metadata,
    Column("id", BigInteger, primary_key=True),
    Column("email", Text, nullable=False, unique=True),
    Column("campaign_id", BigInteger, ForeignKey("campaigns.id")),
    Column("password", Text),
    Column("status", Text, nullable=False, server_default="active"),  # active|burned|invalid
    Column("times_used", Integer, nullable=False, server_default="0"),
    Column("created_at", DateTime(timezone=True), server_default=NOW),
    CheckConstraint("status IN ('active','burned','invalid')", name="ck_emails_status"),
    Index("idx_emails_active", "times_used", postgresql_where=text("status = 'active'")),
    Index("idx_emails_campaign", "campaign_id"),
)


# ~1,000 each. 1000 x 1000 = 1,000,000 CAPACITY — not a table you build (§5.2).
first_names = Table(
    "first_names", metadata,
    Column("id", BigInteger, primary_key=True),
    Column("name", Text, nullable=False, unique=True),
)

last_names = Table(
    "last_names", metadata,
    Column("id", BigInteger, primary_key=True),
    Column("name", Text, nullable=False, unique=True),
)


# Materialised (first, last, email) triples — only as many as a quota needs, drawn
# from the 1M space. A 20,000 quota makes 20,000 rows, not 1,000,000 (§5.2).
identities = Table(
    "identities", metadata,
    Column("id", BigInteger, primary_key=True),
    Column("campaign_id", BigInteger, ForeignKey("campaigns.id")),
    Column("first_name", Text, nullable=False),
    Column("last_name", Text, nullable=False),
    Column("email_id", BigInteger, ForeignKey("emails.id"), nullable=False),
    Column("status", Text, nullable=False, server_default="unused"),  # unused|reserved|used
    Column("used_at", DateTime(timezone=True)),
    Column("created_at", DateTime(timezone=True), server_default=NOW),
    CheckConstraint("status IN ('unused','reserved','used')", name="ck_identities_status"),
    # The uniqueness guarantee: a name pair is never reused, across all quotas, forever.
    Index("uq_identity_pair", "first_name", "last_name", unique=True),
    Index("idx_identities_unused", "id", postgresql_where=text("status = 'unused'")),
    # FK indexes — Postgres does not create these for you.
    Index("idx_identities_campaign", "campaign_id"),
    Index("idx_identities_email", "email_id"),
)


# One row per transaction attempt against a card. This is why a retry doesn't destroy
# the history of why the previous attempt failed — cards.error alone is overwritten.
card_attempts = Table(
    "card_attempts", metadata,
    Column("id", BigInteger, primary_key=True),
    Column("card_id", BigInteger, ForeignKey("cards.id"), nullable=False),
    Column("task_id", BigInteger, ForeignKey("tasks.id")),
    # ambiguous => card is HELD in 'reserved' for the Needs Review queue (§6.4).
    # There is no automatic resolver; recheck.py does not exist and is not being written.
    Column("outcome", Text, nullable=False),   # success|soft_fail|hard_decline|ambiguous
    Column("error", Text),
    Column("created_at", DateTime(timezone=True), server_default=NOW),
    CheckConstraint(
        "outcome IN ('success','soft_fail','hard_decline','ambiguous')",
        name="ck_card_attempts_outcome"),
    # FK indexes — Postgres does not create these for you.
    Index("idx_card_attempts_card", "card_id"),
    Index("idx_card_attempts_task", "task_id"),
    # Needs Review queue (§6.4): the held-for-human rows, newest first.
    Index("idx_card_attempts_ambiguous", "created_at",
          postgresql_where=text("outcome = 'ambiguous'")),
)


# ============================================================================
# source pool (added by 008)
# ============================================================================

# One row per "run this URL N times" the operator submits from the Source page.
# Claims filter on status='active', the same way card claims filter on active
# campaigns — so pausing a batch is one UPDATE, and reversible.
source_batches = Table(
    "source_batches", metadata,
    Column("id", BigInteger, primary_key=True),
    Column("url", Text, nullable=False),
    Column("total", Integer, nullable=False),
    Column("status", Text, nullable=False, server_default="active"),  # active|stopped|done
    Column("note", Text),
    Column("created_at", DateTime(timezone=True), server_default=NOW),
    Column("updated_at", DateTime(timezone=True), server_default=NOW),
    Index("idx_source_batches_status", "status"),
)


# One row per unit of work — a 500-count batch is 500 rows. Every source instance on
# every server claims from this one pool (FOR UPDATE SKIP LOCKED), so the 500 are
# split across the fleet without double-runs, progress is a GROUP BY, and the slots
# go idle exactly when the last row leaves 'pending'.
source_tasks = Table(
    "source_tasks", metadata,
    Column("id", BigInteger, primary_key=True),
    Column("batch_id", BigInteger, ForeignKey("source_batches.id"), nullable=False),
    # denormalized from the batch so a claiming bot needs no join to know its URL
    Column("url", Text, nullable=False),
    Column("status", Text, nullable=False, server_default="pending"),  # pending|running|done|failed
    Column("ran_by", Integer),                      # global instance id that owns it
    Column("attempts", Integer, nullable=False, server_default="0"),
    Column("error", Text),
    Column("result", Text),
    Column("duration_sec", Numeric),
    Column("claimed_at", DateTime(timezone=True)),
    Column("updated_at", DateTime(timezone=True), server_default=NOW),
    # THE claim hot path — every instance, every server, every cycle.
    Index("idx_source_tasks_claim", "id", postgresql_where=text("status = 'pending'")),
    Index("idx_source_tasks_batch", "batch_id", "status"),
    # Crash recovery: find MY rows left 'running' after a restart.
    Index("idx_source_tasks_running", "ran_by", postgresql_where=text("status = 'running'")),
)


# ============================================================================
# nykaa pool (added by 009)
# ============================================================================

# One row per "make N accounts" submitted from the Nykaa page. Claims filter on
# status='active', so pausing a batch is one UPDATE and reversible.
nykaa_batches = Table(
    "nykaa_batches", metadata,
    Column("id", BigInteger, primary_key=True),
    Column("total", Integer, nullable=False),
    Column("status", Text, nullable=False, server_default="active"),  # active|stopped|done
    Column("note", Text),
    Column("created_at", DateTime(timezone=True), server_default=NOW),
    Column("updated_at", DateTime(timezone=True), server_default=NOW),
    Index("idx_nykaa_batches_status", "status"),
)


# One row per account to create. Every nykaa instance on every server claims from this
# one pool (FOR UPDATE SKIP LOCKED), so N is split across the fleet without
# double-creating, progress is a GROUP BY, and slots go idle when the last row settles.
nykaa_tasks = Table(
    "nykaa_tasks", metadata,
    Column("id", BigInteger, primary_key=True),
    Column("batch_id", BigInteger, ForeignKey("nykaa_batches.id"), nullable=False),
    Column("status", Text, nullable=False, server_default="pending"),  # pending|running|done|failed
    Column("ran_by", Integer),                      # global instance id that owns it
    Column("attempts", Integer, nullable=False, server_default="0"),
    Column("error", Text),
    Column("result", Text),                         # account detail the bot records
    Column("duration_sec", Numeric),
    Column("claimed_at", DateTime(timezone=True)),
    Column("updated_at", DateTime(timezone=True), server_default=NOW),
    Index("idx_nykaa_tasks_claim", "id", postgresql_where=text("status = 'pending'")),
    Index("idx_nykaa_tasks_batch", "batch_id", "status"),
    Index("idx_nykaa_tasks_running", "ran_by", postgresql_where=text("status = 'running'")),
)


# One row per created Nykaa account (added by 010). Replaces the Google Sheet + CSV:
# a sheet needs credentials on every box, rate-limits under a fleet, and joins against
# nothing. `mobile` is unique — the same number twice means a re-run, not a new account.
nykaa_accounts = Table(
    "nykaa_accounts", metadata,
    Column("id", BigInteger, primary_key=True),
    Column("mobile", Text, nullable=False),
    Column("name", Text),
    Column("email", Text),
    Column("session_file", Text),
    Column("provider", Text),                       # smsindia | techyindia
    Column("ran_by", Integer),                      # global instance id that made it
    Column("task_id", BigInteger),                  # nykaa_tasks.id, when queue-driven
    Column("created_at", DateTime(timezone=True), server_default=NOW),
    UniqueConstraint("mobile", name="uq_nykaa_accounts_mobile"),
    Index("idx_nykaa_accounts_created", "created_at"),
    Index("idx_nykaa_accounts_email", "email"),
)


# ---------------------------------------------------------------------------
# Telegram as an OTP provider (added by 011)
#
# smsindia/techyindia are stateless HTTP APIs — twenty instances can call them at once.
# Telegram is not: one Telethon session is one ACCOUNT is one chat, and two purchases
# cannot interleave in the same chat. So capacity comes from accounts, not from slots,
# and the two things are separate tables.
# ---------------------------------------------------------------------------

# CAPACITY. One account can fetch one number at a time.
telegram_accounts = Table(
    "telegram_accounts", metadata,
    Column("id", BigInteger, primary_key=True),
    Column("label", Text, nullable=False),              # "acct-A"
    Column("phone", Text, nullable=False),
    Column("api_id", Text),                             # my.telegram.org
    Column("api_hash", Text),
    # Login happens once and Telegram texts a code to that number — a human has to type
    # it. After that this file keeps the account signed in.
    Column("session_file", Text),
    Column("session_ok", Boolean, server_default=text("false")),
    Column("enabled", Boolean, server_default=text("true")),
    Column("busy_until", DateTime(timezone=True)),      # broker's lock
    Column("last_used_at", DateTime(timezone=True)),
    Column("last_error", Text),
    Column("note", Text),
    Column("created_at", DateTime(timezone=True), server_default=NOW),
    UniqueConstraint("label", name="uq_telegram_accounts_label"),
)

# VENDOR. Which bot/channel, and what its menu looks like.
telegram_sources = Table(
    "telegram_sources", metadata,
    Column("id", BigInteger, primary_key=True),
    Column("label", Text, nullable=False),              # "acct-A / ulotpbot"
    Column("account_id", BigInteger, ForeignKey("telegram_accounts.id"), nullable=False),
    Column("kind", Text, nullable=False, server_default="bot"),   # bot | channel
    Column("target", Text, nullable=False),             # @ulotpbot / channel id
    Column("service_command", Text),                    # /find_NYKAA
    # steps + buttons + keywords, i.e. what telegram_bot_scraper/config.py holds today.
    # JSON so a new vendor bot is a row, not a code change — every bot's menu differs.
    Column("profile", JSONB),
    Column("priority", Integer, server_default=text("100")),
    Column("enabled", Boolean, server_default=text("true")),
    Column("status", Text, server_default="idle"),
    Column("last_error", Text),
    Column("last_used_at", DateTime(timezone=True)),
    Column("created_at", DateTime(timezone=True), server_default=NOW),
    UniqueConstraint("label", name="uq_telegram_sources_label"),
    Index("idx_telegram_sources_pick", "enabled", "priority", "last_used_at"),
)
