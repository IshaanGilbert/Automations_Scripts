"""nykaa_accounts — the created accounts, in the DB instead of a Google Sheet

The flow used to append every account to a Google Sheet (gspread) with a local CSV as
a fallback. Both are gone: a sheet needs credentials on every box, rate-limits under a
fleet, and cannot be joined against anything. The CSV was worse — several slots on one
box appending to one file.

One row per created account. `mobile` is unique: the same number coming back twice
means something re-ran, and the DB should refuse rather than quietly duplicate.

Revision ID: 0010
Revises: 0009
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0010"
down_revision: Union[str, Sequence[str], None] = "0009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "nykaa_accounts",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("mobile", sa.Text(), nullable=False),
        sa.Column("name", sa.Text()),
        sa.Column("email", sa.Text()),
        sa.Column("session_file", sa.Text()),
        sa.Column("provider", sa.Text()),          # smsindia | techyindia
        sa.Column("ran_by", sa.Integer()),         # global instance id that made it
        sa.Column("task_id", sa.BigInteger()),     # nykaa_tasks.id, when queue-driven
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        # Same number twice = a re-run, not a second account. Let the DB say no.
        sa.UniqueConstraint("mobile", name="uq_nykaa_accounts_mobile"),
    )
    op.create_index("idx_nykaa_accounts_created", "nykaa_accounts", ["created_at"])
    op.create_index("idx_nykaa_accounts_email", "nykaa_accounts", ["email"])


def downgrade() -> None:
    op.drop_index("idx_nykaa_accounts_email", table_name="nykaa_accounts")
    op.drop_index("idx_nykaa_accounts_created", table_name="nykaa_accounts")
    op.drop_table("nykaa_accounts")
