"""slim tasks — point at inputs (card_id/identity_id/quota_id) instead of copying them

`tasks` had accreted 28 columns. Most now duplicate cards/identities/quotas, or are
dead. It becomes a transaction RECORD that references its inputs.

  dropped: card_no, month, cvv   -> cards.card_no / expiry / cvv
           email                  -> identities -> emails.email
           first_name, last_name  -> identities
           name_used              -> pure derivation, buyer.py:1168 is
                                     f"{first_name} {last_name}"
           password               -> quotas.account_password (constant, once per quota)
           rechecks               -> only claim_unconfirmed_for_recheck incremented it,
                                     and recheck.py does not exist / is not being written

  kept:    corp_id, emp_id — _try_claim's least-loaded CTE (db.py:769-786) balances
                             across emp_id. Load-bearing, do not "clean up".
           step, step_at   — live progress (db.py:835)
           updated_email, email_attempts — email mutation is live in three buyers.
                             Kept pending the §3.2 review.

DATA LOSS — READ THIS
=====================
This migration DROPS columns holding transaction history. It is written for a FRESH
database (the agreed approach: the quota-driven system gets its own new DB; the old
sheet-era DB is left untouched).

The upgrade() therefore REFUSES TO RUN if `tasks` has any rows, rather than silently
destroying history. If you hit that guard, you are running this on the old DB by
mistake — see docs/REVAMP_PLAN.md §3.2 for the archive/backfill options that were
considered and consciously not taken.

Revision ID: 0003
Revises: 0002
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from alembic import context


revision: str = "0003"
down_revision: Union[str, Sequence[str], None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Columns removed by upgrade(), re-created by downgrade(). Order matters only for
# readability — it mirrors the original CREATE TABLE in 0001.
_DROPPED = [
    ("card_no", sa.Text()),
    ("month", sa.Text()),
    ("cvv", sa.Text()),
    ("email", sa.Text()),
    ("first_name", sa.Text()),
    ("last_name", sa.Text()),
    ("name_used", sa.Text()),
    ("password", sa.Text()),
]


def _guard_empty() -> None:
    """Refuse to destroy transaction history.

    Skipped in offline (--sql) mode, where there is no connection to count with.
    """
    if context.is_offline_mode():
        return
    n = op.get_bind().execute(sa.text("SELECT count(*) FROM tasks")).scalar()
    if n:
        raise RuntimeError(
            f"\n\n"
            f"  0003_slim_tasks REFUSED TO RUN: `tasks` has {n:,} rows.\n\n"
            f"  This migration drops card_no / month / cvv / email / first_name /\n"
            f"  last_name / name_used / password — columns that hold real transaction\n"
            f"  history. It is written for a FRESH database.\n\n"
            f"  You are probably pointed at the old sheet-era DB. Check the URL:\n"
            f"    ALEMBIC_DATABASE_URL / DATABASE_URL / config.json DB_*\n\n"
            f"  If you genuinely intend to migrate history, see REVAMP_PLAN.md §3.2 —\n"
            f"  archive-to-tasks_archive and backfill-into-cards were both considered.\n"
            f"  Neither is implemented, because the agreed plan is a new DB.\n"
        )


def upgrade() -> None:
    _guard_empty()

    # --- point at the inputs -------------------------------------------------
    op.add_column("tasks", sa.Column("card_id", sa.BigInteger()))
    op.add_column("tasks", sa.Column("identity_id", sa.BigInteger()))
    op.add_column("tasks", sa.Column("quota_id", sa.BigInteger()))
    op.create_foreign_key("fk_tasks_card", "tasks", "cards", ["card_id"], ["id"])
    op.create_foreign_key("fk_tasks_identity", "tasks", "identities", ["identity_id"], ["id"])
    op.create_foreign_key("fk_tasks_quota", "tasks", "quotas", ["quota_id"], ["id"])

    # Load-bearing: makes it STRUCTURALLY impossible to issue one card, or one
    # identity, to two transactions. Nothing prevents that today. These also serve
    # as the FK indexes (Postgres does not create those for you).
    op.create_index(
        "uq_tasks_card", "tasks", ["card_id"], unique=True,
        postgresql_where=sa.text("card_id IS NOT NULL"),
    )
    op.create_index(
        "uq_tasks_identity", "tasks", ["identity_id"], unique=True,
        postgresql_where=sa.text("identity_id IS NOT NULL"),
    )
    op.create_index("idx_tasks_quota", "tasks", ["quota_id"])

    # --- drop what is now duplicated or dead ---------------------------------
    for name, _type in _DROPPED:
        op.drop_column("tasks", name)
    op.drop_column("tasks", "rechecks")


def downgrade() -> None:
    # Re-created nullable with no default: the original data is gone either way, and
    # upgrade() only runs on an empty table, so there is nothing to restore.
    op.add_column("tasks", sa.Column("rechecks", sa.Integer(), nullable=False,
                                     server_default="0"))
    for name, type_ in reversed(_DROPPED):
        op.add_column("tasks", sa.Column(name, type_))

    op.drop_index("idx_tasks_quota", table_name="tasks")
    op.drop_index("uq_tasks_identity", table_name="tasks")
    op.drop_index("uq_tasks_card", table_name="tasks")
    op.drop_constraint("fk_tasks_quota", "tasks", type_="foreignkey")
    op.drop_constraint("fk_tasks_identity", "tasks", type_="foreignkey")
    op.drop_constraint("fk_tasks_card", "tasks", type_="foreignkey")
    op.drop_column("tasks", "quota_id")
    op.drop_column("tasks", "identity_id")
    op.drop_column("tasks", "card_id")
