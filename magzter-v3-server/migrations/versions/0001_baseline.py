"""baseline — the schema as db.py:init_schema() built it

Reproduces exactly what db.py:163-272 created, including columns later migrations
remove (zip_code, password, card_no...). This is the BASELINE of what exists today,
not the target state — do not "improve" it here.

ON AN EXISTING SERVER, DO NOT RUN `upgrade`. Run:

    alembic stamp 0001

...which records this revision as applied without executing it, because the tables
are already there. `upgrade` would fail on the first CREATE TABLE.

On a fresh/empty database, `alembic upgrade head` runs this normally.

After this lands, db.py:init_schema() is deleted and `alembic upgrade head` becomes
the deploy step. See docs/REVAMP_PLAN.md §3.0.

Revision ID: 0001
Revises:
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tasks",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("sheet_row", sa.Integer(), unique=True),
        sa.Column("card_no", sa.Text()),
        sa.Column("month", sa.Text()),
        sa.Column("cvv", sa.Text()),
        sa.Column("email", sa.Text()),
        sa.Column("corp_id", sa.Text()),
        sa.Column("emp_id", sa.Text()),
        sa.Column("zip_code", sa.Text()),
        sa.Column("first_name", sa.Text()),
        sa.Column("last_name", sa.Text()),
        sa.Column("status", sa.Text(), nullable=False, server_default="pending"),
        sa.Column("ran_by", sa.Integer()),
        sa.Column("name_used", sa.Text()),
        sa.Column("proxy_ip", sa.Text()),
        sa.Column("duration_sec", sa.Numeric()),
        sa.Column("error", sa.Text()),
        sa.Column("transaction_id", sa.Text()),
        sa.Column("claimed_at", sa.DateTime(timezone=True)),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("synced_to_sheet", sa.Boolean(), nullable=False,
                  server_default=sa.text("true")),
        sa.Column("retries", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("step", sa.Text()),
        sa.Column("step_at", sa.DateTime(timezone=True)),
        sa.Column("reassigned", sa.Boolean(), nullable=False,
                  server_default=sa.text("false")),
        sa.Column("rechecks", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("password", sa.Text()),
        sa.Column("updated_email", sa.Text()),
        sa.Column("email_attempts", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index("idx_tasks_status", "tasks", ["status"])
    op.create_index("idx_tasks_emp", "tasks", ["emp_id"])
    op.create_index(
        "idx_tasks_unsynced", "tasks", ["synced_to_sheet"],
        postgresql_where=sa.text("synced_to_sheet = false"),
    )

    op.create_table(
        "otp_alerts",
        sa.Column("emp_id", sa.Text(), primary_key=True),
        sa.Column("consecutive_failures", sa.Integer(), nullable=False,
                  server_default="0"),
        sa.Column("total_failures", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_failure", sa.DateTime(timezone=True)),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "read_tasks",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("sheet_row", sa.Integer(), unique=True),
        sa.Column("email", sa.Text()),
        sa.Column("password", sa.Text()),
        sa.Column("name_used", sa.Text()),
        sa.Column("transaction_id", sa.Text()),
        sa.Column("transaction_date", sa.Text()),
        sa.Column("duration_sec", sa.Numeric()),
        sa.Column("status", sa.Text(), nullable=False, server_default="pending"),
        sa.Column("ran_by", sa.Integer()),
        sa.Column("error", sa.Text()),
        sa.Column("books_read", sa.Integer(), server_default="0"),
        sa.Column("claimed_at", sa.DateTime(timezone=True)),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("synced_to_sheet", sa.Boolean(), nullable=False,
                  server_default=sa.text("true")),
        sa.Column("retries", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index("idx_read_status", "read_tasks", ["status"])
    op.create_index(
        "idx_read_unsynced", "read_tasks", ["synced_to_sheet"],
        postgresql_where=sa.text("synced_to_sheet = false"),
    )

    op.create_table(
        "system_state",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=False,
                  server_default="1"),
        sa.Column("paused", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("reader_sync_paused", sa.Boolean(), nullable=False,
                  server_default=sa.text("false")),
        sa.Column("note", sa.Text()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    # The singleton row every bot polls before claiming (db.py:267).
    op.execute(
        "INSERT INTO system_state (id, paused) VALUES (1, FALSE) "
        "ON CONFLICT (id) DO NOTHING"
    )


def downgrade() -> None:
    op.drop_table("system_state")
    op.drop_index("idx_read_unsynced", table_name="read_tasks")
    op.drop_index("idx_read_status", table_name="read_tasks")
    op.drop_table("read_tasks")
    op.drop_table("otp_alerts")
    op.drop_index("idx_tasks_unsynced", table_name="tasks")
    op.drop_index("idx_tasks_emp", table_name="tasks")
    op.drop_index("idx_tasks_status", table_name="tasks")
    op.drop_table("tasks")
