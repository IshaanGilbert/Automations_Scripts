"""nykaa_batches + nykaa_tasks — the work pool for nykaa.py

Same shape as the `source` pool from 008, for the same reason: the operator asks for a
number of accounts, and that number has to be answerable at any moment ("how many of
the 500 are done?") no matter how many boxes are working on it.

  nykaa_batches   one row per "make N accounts" submitted from the dashboard.
                  status active | stopped | done. Claims filter on active, so pausing
                  a batch is one UPDATE and is reversible.
  nykaa_tasks     one row per account to create. status pending -> running -> done |
                  failed. Claimed one at a time with FOR UPDATE SKIP LOCKED, so every
                  instance on every server draws from the same N without collisions.

`result` holds whatever the bot wants to record about the account it made. It is TEXT
rather than typed columns because the account fields live inside nykaa_smsindia_flow
and are not settled yet — once they are, they get promoted to real columns.

Revision ID: 0009
Revises: 0008
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0009"
down_revision: Union[str, Sequence[str], None] = "0008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "nykaa_batches",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("total", sa.Integer(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False, server_default="active"),
        sa.Column("note", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("idx_nykaa_batches_status", "nykaa_batches", ["status"])

    op.create_table(
        "nykaa_tasks",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("batch_id", sa.BigInteger(), sa.ForeignKey("nykaa_batches.id"), nullable=False),
        sa.Column("status", sa.Text(), nullable=False, server_default="pending"),
        sa.Column("ran_by", sa.Integer()),          # global instance id that owns it
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error", sa.Text()),
        sa.Column("result", sa.Text()),             # account detail the bot records
        sa.Column("duration_sec", sa.Numeric()),
        sa.Column("claimed_at", sa.DateTime(timezone=True)),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    # THE claim hot path — every instance, every server, every cycle.
    op.create_index("idx_nykaa_tasks_claim", "nykaa_tasks", ["id"],
                    postgresql_where=sa.text("status = 'pending'"))
    op.create_index("idx_nykaa_tasks_batch", "nykaa_tasks", ["batch_id", "status"])
    # Crash recovery: find MY rows left 'running' after a restart.
    op.create_index("idx_nykaa_tasks_running", "nykaa_tasks", ["ran_by"],
                    postgresql_where=sa.text("status = 'running'"))


def downgrade() -> None:
    op.drop_index("idx_nykaa_tasks_running", table_name="nykaa_tasks")
    op.drop_index("idx_nykaa_tasks_batch", table_name="nykaa_tasks")
    op.drop_index("idx_nykaa_tasks_claim", table_name="nykaa_tasks")
    op.drop_table("nykaa_tasks")
    op.drop_index("idx_nykaa_batches_status", table_name="nykaa_batches")
    op.drop_table("nykaa_batches")
