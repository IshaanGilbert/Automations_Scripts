"""campaign_employees — which employee IDs a campaign runs on, + backups

The buyer runs transactions under an employee ID (tasks.emp_id / corp_id). Which
employees to use, and which to fall back to when one's OTPs start failing, used to
live in global config (BACKUP_EMPLOYEES). The spec puts them ON THE CAMPAIGN so each
campaign runs on its own chosen employees.

  corp_id              the corporate the employees belong to (one per campaign)
  employee_ids         primary employees the engine assigns transactions to
  backup_employee_ids  fallbacks the OTP-cooldown shifts a dying employee's work to

TEXT[] arrays: small, ordered, editable as a whole. No join table needed for a
handful of ids per campaign.

Revision ID: 0007
Revises: 0006
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0007"
down_revision: Union[str, Sequence[str], None] = "0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("campaigns", sa.Column("corp_id", sa.Text()))
    op.add_column("campaigns", sa.Column(
        "employee_ids", postgresql.ARRAY(sa.Text()),
        nullable=False, server_default="{}"))
    op.add_column("campaigns", sa.Column(
        "backup_employee_ids", postgresql.ARRAY(sa.Text()),
        nullable=False, server_default="{}"))


def downgrade() -> None:
    op.drop_column("campaigns", "backup_employee_ids")
    op.drop_column("campaigns", "employee_ids")
    op.drop_column("campaigns", "corp_id")
