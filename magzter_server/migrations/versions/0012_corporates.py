"""corporates + corp_employees — multiple corporates, each with its own employees,
each independently active/inactive, switched at RUNTIME.

Until now a campaign carried ONE corp_id + a flat employee_ids array, so running a
different corporate meant editing the campaign. The operator has several corporates
(e.g. marcadeo, streakads), each with its OWN employee ids, and wants to choose which
run at any moment:

  * corporates.active      -> is this corporate running right now?
  * corp_employees.active  -> is this individual employee in play?

The runtime engine (db.generate_campaign_tasks) unions the ACTIVE employees of every
ACTIVE corporate and mints tasks across that pool — each task stamped with that
employee's OWN corp_id. Both corps active => both run; one active => only that one.
When the table is empty the engine falls back to the campaign's own corp_id/
employee_ids, so existing single-corp setups are unaffected.

Revision ID: 0012
Revises: 0011
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0012"
down_revision: Union[str, Sequence[str], None] = "0011"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "corporates",
        sa.Column("corp_id", sa.Text(), primary_key=True),
        sa.Column("label", sa.Text()),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("note", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "corp_employees",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("corp_id", sa.Text(),
                  sa.ForeignKey("corporates.corp_id", ondelete="CASCADE"),
                  nullable=False),
        sa.Column("emp_id", sa.Text(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("note", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("corp_id", "emp_id", name="uq_corp_emp"),
    )
    op.create_index("idx_corp_emp_active", "corp_employees", ["corp_id", "active"])


def downgrade() -> None:
    op.drop_index("idx_corp_emp_active", table_name="corp_employees")
    op.drop_table("corp_employees")
    op.drop_table("corporates")
