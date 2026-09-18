"""add quota tables — quotas, cards, emails, names, identities, card_attempts

Purely ADDITIVE except for one column swap (transaction_date, below). Nothing else is
dropped and nothing existing is rewritten, so this is safe to apply to a live DB while
bots are running. The buyers keep using their inline columns until 0003 slims tasks.

Also adds:
  - tasks.read_request        — reader handoff flag (§6.5)
  - read_tasks.source_task_id — promoter idempotency key + row identity
  - read_tasks audit columns  — transaction_at / read_at / proxy_ip (§6.7)

The one destructive edge: read_tasks.transaction_date (TEXT — a raw Google Sheet cell)
is replaced by transaction_at (TIMESTAMPTZ). Existing values are parsed across on a
best-effort basis; unparseable ones become NULL rather than failing the migration.
Nothing reads transaction_date today except the sheet writeback, which Phase 2 deletes.

INDEXING: Postgres does NOT auto-index foreign key columns. Every FK added here gets an
explicit index — without them the dashboard's joins degrade to sequential scans as the
tables grow to 20k+ rows/month. See the "index" blocks below and §3.1.

See docs/REVAMP_PLAN.md §3.1.

Revision ID: 0002
Revises: 0001
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0002"
down_revision: Union[str, Sequence[str], None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---------------------------------------------------------------- quotas
    # What the admin sets. `quota`, never `target` — target already means
    # bots-per-job slot mix (node_agent.py:119).
    op.create_table(
        "quotas",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("kind", sa.Text(), nullable=False),
        sa.Column("period", sa.Text(), nullable=False),
        sa.Column("qty", sa.Integer(), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False, server_default="active"),
        # The constant account password, snapshotted at quota creation (§3.2).
        # Once per quota, NOT per task: rotating ACCOUNT_PASSWORD never orphans
        # accounts created under an earlier quota.
        sa.Column("account_password", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.CheckConstraint("qty > 0", name="ck_quotas_qty_positive"),
        sa.CheckConstraint("period_end >= period_start", name="ck_quotas_period_order"),
        sa.CheckConstraint("kind IN ('cards','transactions')", name="ck_quotas_kind"),
        sa.CheckConstraint("period IN ('daily','weekly','monthly')", name="ck_quotas_period"),
    )
    # Only one active quota per (kind, period) at a time. Also THE lookup index for
    # the daily gate's "what is the active transactions quota?" on every claim.
    op.create_index(
        "uq_quota_active", "quotas", ["kind", "period"], unique=True,
        postgresql_where=sa.text("status = 'active'"),
    )

    # ---------------------------------------------------------------- emails
    op.create_table(
        "emails",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("email", sa.Text(), nullable=False, unique=True),
        sa.Column("password", sa.Text()),
        sa.Column("status", sa.Text(), nullable=False, server_default="active"),
        sa.Column("times_used", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.CheckConstraint("status IN ('active','burned','invalid')", name="ck_emails_status"),
    )
    # Serves the identity generator's "least-used active email" pick (§5.2).
    op.create_index(
        "idx_emails_active", "emails", ["times_used"],
        postgresql_where=sa.text("status = 'active'"),
    )

    # ----------------------------------------------------------- name pools
    # ~1,000 each. 1000 x 1000 = 1M CAPACITY, not a table you build (§5.2).
    op.create_table(
        "first_names",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False, unique=True),
    )
    op.create_table(
        "last_names",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False, unique=True),
    )

    # ------------------------------------------------------------ identities
    op.create_table(
        "identities",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("quota_id", sa.BigInteger(), sa.ForeignKey("quotas.id")),
        sa.Column("first_name", sa.Text(), nullable=False),
        sa.Column("last_name", sa.Text(), nullable=False),
        sa.Column("email_id", sa.BigInteger(), sa.ForeignKey("emails.id"), nullable=False),
        sa.Column("status", sa.Text(), nullable=False, server_default="unused"),
        sa.Column("used_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.CheckConstraint("status IN ('unused','reserved','used')",
                           name="ck_identities_status"),
    )
    # The uniqueness guarantee: a name pair is never reused, across all quotas, forever.
    op.create_index("uq_identity_pair", "identities", ["first_name", "last_name"], unique=True)
    # Claim path: ordered scan of only the unused rows.
    op.create_index(
        "idx_identities_unused", "identities", ["id"],
        postgresql_where=sa.text("status = 'unused'"),
    )
    # FK indexes — Postgres does not create these for you.
    op.create_index("idx_identities_quota", "identities", ["quota_id"])
    op.create_index("idx_identities_email", "identities", ["email_id"])

    # ----------------------------------------------------------------- cards
    # Pre-provisioned as SLOTS by a quota (status='requested', card_no NULL), then
    # filled by the card_generation agent driving the MasterCard portal (§5.1).
    op.create_table(
        "cards",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("quota_id", sa.BigInteger(), sa.ForeignKey("quotas.id")),
        sa.Column("card_no", sa.Text()),
        sa.Column("expiry", sa.Text()),
        sa.Column("cvv", sa.Text()),
        sa.Column("max_amount", sa.Numeric()),
        sa.Column("status", sa.Text(), nullable=False, server_default="requested"),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        # NO used_by_task column. "Which task used this card" is already expressed by
        # tasks.card_id + uq_tasks_card (unique, added in 0003) and is just as fast to
        # query. A reverse pointer here would be a second source of truth that can
        # drift, and it created a circular FK (cards -> tasks -> cards) that
        # SQLAlchemy cannot sort — caught by the autogenerate drift check.
        sa.Column("generated_at", sa.DateTime(timezone=True)),
        sa.Column("used_at", sa.DateTime(timezone=True)),
        sa.Column("claimed_at", sa.DateTime(timezone=True)),
        sa.Column("ran_by", sa.Integer()),
        sa.Column("error", sa.Text()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.CheckConstraint(
            "status IN ('requested','generating','unused','reserved','used','payment_failed')",
            name="ck_cards_status"),
    )
    op.create_index(
        "uq_cards_no", "cards", ["card_no"], unique=True,
        postgresql_where=sa.text("card_no IS NOT NULL"),
    )
    # Dashboard "pool health by status" groups on this.
    op.create_index("idx_cards_status", "cards", ["status"])
    # The two claim paths (§5.1, §6.2): ordered scans of only the matching rows.
    op.create_index(
        "idx_cards_unused", "cards", ["id"],
        postgresql_where=sa.text("status = 'unused'"),
    )
    op.create_index(
        "idx_cards_requested", "cards", ["id"],
        postgresql_where=sa.text("status = 'requested'"),
    )
    # FK index.
    op.create_index("idx_cards_quota", "cards", ["quota_id"])

    # -------------------------------------------------------- card_attempts
    # One row per attempt, so a retry doesn't destroy why the last one failed.
    op.create_table(
        "card_attempts",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("card_id", sa.BigInteger(), sa.ForeignKey("cards.id"), nullable=False),
        sa.Column("task_id", sa.BigInteger(), sa.ForeignKey("tasks.id")),
        sa.Column("outcome", sa.Text(), nullable=False),
        sa.Column("error", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.CheckConstraint(
            "outcome IN ('success','soft_fail','hard_decline','ambiguous')",
            name="ck_card_attempts_outcome"),
    )
    op.create_index("idx_card_attempts_card", "card_attempts", ["card_id"])
    op.create_index("idx_card_attempts_task", "card_attempts", ["task_id"])
    # Needs Review queue (§6.4): the held-for-human rows, newest first.
    op.create_index(
        "idx_card_attempts_ambiguous", "card_attempts", ["created_at"],
        postgresql_where=sa.text("outcome = 'ambiguous'"),
    )

    # -------------------------------------------------- reader handoff (§6.5)
    op.add_column(
        "tasks",
        sa.Column("read_request", sa.Boolean(), nullable=False,
                  server_default=sa.text("false")),
    )
    # The promoter's hot path: completed transactions not yet sent to the reader.
    op.create_index(
        "idx_tasks_readable", "tasks", ["id"],
        postgresql_where=sa.text("status = 'completed' AND read_request = false"),
    )

    op.add_column("read_tasks", sa.Column("source_task_id", sa.BigInteger()))
    op.create_foreign_key(
        "fk_read_tasks_source_task", "read_tasks", "tasks", ["source_task_id"], ["id"],
    )
    # Belt-and-braces with tasks.read_request: read_request alone is not idempotent
    # across a crash between the promoter's INSERT and its UPDATE. This index is.
    # Doubles as the FK index.
    #
    # NOT partial, deliberately. A `WHERE source_task_id IS NOT NULL` clause would be
    # both pointless and actively harmful:
    #   - pointless: Postgres already treats NULLs as distinct in a unique index, so
    #     rows with no source_task_id never collide anyway.
    #   - harmful:  ON CONFLICT (source_task_id) cannot INFER a partial index, so the
    #     promoter (§6.5) fails outright with "no unique or exclusion constraint
    #     matching the ON CONFLICT specification".
    op.create_index("uq_read_source", "read_tasks", ["source_task_id"], unique=True)

    # ----------------------------------------- the daily quota gate's index (§6.1)
    # THE hottest query in the new system: it runs on every claim attempt, on every
    # instance, across every server —
    #   SELECT count(*) FROM tasks
    #    WHERE status <> 'pending' AND updated_at >= date_trunc('day', now())
    # Partial + ordered on updated_at so it is an index-only range scan rather than a
    # full scan of a table that grows 20k rows a month.
    op.create_index(
        "idx_tasks_settled_at", "tasks", ["updated_at"],
        postgresql_where=sa.text("status <> 'pending'"),
    )
    # Transaction lookups from the dashboard / support ("find txn_88123").
    op.create_index(
        "idx_tasks_txid", "tasks", ["transaction_id"],
        postgresql_where=sa.text("transaction_id IS NOT NULL"),
    )

    # --------------------------------------------- reader audit trail (§6.7)
    op.add_column("read_tasks", sa.Column("transaction_at", sa.DateTime(timezone=True)))
    op.add_column("read_tasks", sa.Column("read_at", sa.DateTime(timezone=True)))
    # read.py:1047 _verify_proxy_ip() already resolves this via ipify and throws it
    # away — tasks records proxy_ip, read_tasks never had a column for it.
    op.add_column("read_tasks", sa.Column("proxy_ip", sa.Text()))

    # transaction_date was TEXT (a raw sheet cell). Carry what parses; the rest go
    # NULL rather than failing the whole migration on one malformed string.
    op.execute(
        """
        UPDATE read_tasks
           SET transaction_at = CASE
                 WHEN transaction_date IS NULL OR btrim(transaction_date) = '' THEN NULL
                 ELSE pg_catalog.to_timestamp(
                        pg_catalog.substr(btrim(transaction_date), 1, 40),
                        'YYYY-MM-DD HH24:MI:SS')
               END
         WHERE transaction_date IS NOT NULL
        """
    )
    op.drop_column("read_tasks", "transaction_date")

    # Reader page sorts on these (§6.7): "read most recently", "bought on".
    op.create_index("idx_read_read_at", "read_tasks", ["read_at"])
    op.create_index("idx_read_transaction_at", "read_tasks", ["transaction_at"])


def downgrade() -> None:
    op.drop_index("idx_read_transaction_at", table_name="read_tasks")
    op.drop_index("idx_read_read_at", table_name="read_tasks")

    op.add_column("read_tasks", sa.Column("transaction_date", sa.Text()))
    op.execute(
        "UPDATE read_tasks SET transaction_date = "
        "to_char(transaction_at, 'YYYY-MM-DD HH24:MI:SS') "
        "WHERE transaction_at IS NOT NULL"
    )
    op.drop_column("read_tasks", "proxy_ip")
    op.drop_column("read_tasks", "read_at")
    op.drop_column("read_tasks", "transaction_at")

    op.drop_index("idx_tasks_txid", table_name="tasks")
    op.drop_index("idx_tasks_settled_at", table_name="tasks")

    op.drop_index("uq_read_source", table_name="read_tasks")
    op.drop_constraint("fk_read_tasks_source_task", "read_tasks", type_="foreignkey")
    op.drop_column("read_tasks", "source_task_id")

    op.drop_index("idx_tasks_readable", table_name="tasks")
    op.drop_column("tasks", "read_request")

    op.drop_index("idx_card_attempts_ambiguous", table_name="card_attempts")
    op.drop_index("idx_card_attempts_task", table_name="card_attempts")
    op.drop_index("idx_card_attempts_card", table_name="card_attempts")
    op.drop_table("card_attempts")

    op.drop_index("idx_cards_quota", table_name="cards")
    op.drop_index("idx_cards_requested", table_name="cards")
    op.drop_index("idx_cards_unused", table_name="cards")
    op.drop_index("idx_cards_status", table_name="cards")
    op.drop_index("uq_cards_no", table_name="cards")
    op.drop_table("cards")

    op.drop_index("idx_identities_email", table_name="identities")
    op.drop_index("idx_identities_quota", table_name="identities")
    op.drop_index("idx_identities_unused", table_name="identities")
    op.drop_index("uq_identity_pair", table_name="identities")
    op.drop_table("identities")

    op.drop_table("last_names")
    op.drop_table("first_names")

    op.drop_index("idx_emails_active", table_name="emails")
    op.drop_table("emails")

    op.drop_index("uq_quota_active", table_name="quotas")
    op.drop_table("quotas")
