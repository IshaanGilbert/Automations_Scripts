"""source_batches + source_tasks — the work pool for source.py

`source` was registered as a job with NO work pool: the auto-scheduler filled its
slots unconditionally and nothing counted what it had finished. That makes "run this
URL 500 times across the fleet" unanswerable — there is no 500 anywhere, and the
slots never go idle because there is no pool to empty.

These two tables are that pool:

  source_batches   one row per "URL × count" the operator submits. status active |
                   stopped | done. Claims are filtered on status='active', exactly
                   like cards claims are filtered on active campaigns (db.py:1055),
                   so pausing a batch is one UPDATE and is reversible.
  source_tasks     one row per unit of work — 500 count = 500 rows. status
                   pending -> running -> done | failed. The bot claims one row at a
                   time with FOR UPDATE SKIP LOCKED, so every instance on every
                   server draws from the same 500 without collisions or double-runs.

Progress is then just a GROUP BY over source_tasks, and "when does everything go
idle" is answered by the pool hitting zero claimable rows: scheduler_pending()
reports source=0, node_agent stops refilling source slots, and each running bot
exits when its next claim comes back empty.

Revision ID: 0008
Revises: 0007
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0008"
down_revision: Union[str, Sequence[str], None] = "0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "source_batches",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("total", sa.Integer(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False, server_default="active"),
        sa.Column("note", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("idx_source_batches_status", "source_batches", ["status"])

    op.create_table(
        "source_tasks",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("batch_id", sa.BigInteger(), sa.ForeignKey("source_batches.id"), nullable=False),
        # denormalized from the batch so a claiming bot needs no join to know its URL
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False, server_default="pending"),
        sa.Column("ran_by", sa.Integer()),          # global instance id that owns it
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error", sa.Text()),
        sa.Column("result", sa.Text()),             # whatever the bot wants to record
        sa.Column("duration_sec", sa.Numeric()),
        sa.Column("claimed_at", sa.DateTime(timezone=True)),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    # THE claim hot path — every instance on every server hits this every cycle.
    # Partial + ordered so it stays an index scan as the table grows past the
    # pending rows it is looking for.
    op.create_index("idx_source_tasks_claim", "source_tasks", ["id"],
                    postgresql_where=sa.text("status = 'pending'"))
    # Progress: counts grouped per batch.
    op.create_index("idx_source_tasks_batch", "source_tasks", ["batch_id", "status"])
    # Crash recovery: find MY rows left 'running' after a restart.
    op.create_index("idx_source_tasks_running", "source_tasks", ["ran_by"],
                    postgresql_where=sa.text("status = 'running'"))


def downgrade() -> None:
    op.drop_index("idx_source_tasks_running", table_name="source_tasks")
    op.drop_index("idx_source_tasks_batch", table_name="source_tasks")
    op.drop_index("idx_source_tasks_claim", table_name="source_tasks")
    op.drop_table("source_tasks")
    op.drop_index("idx_source_batches_status", table_name="source_batches")
    op.drop_table("source_batches")
