"""drop zip_code — it was already dead at the last mile

zip_code was plumbed all the way through (sheet -> sync_tasks -> tasks.zip_code ->
_to_task -> task['zip_code']) and then only PRINTED. The form-fill that actually used
it is commented out in all three buyers:

    buyer.py:1460-1483          "TEMPORARILY DISABLED (zip code skip)"
    buyer_gologin.py:1492-1523
    buyer_hdfc.py:1500-1523

So this is subtraction, not surgery — nothing that reads the column feeds anything.

Reversible: downgrade re-adds the column nullable. The DEFAULT_ZIPS / ZIP_ERROR_MSGS
retry machinery is deleted from the buyers in the same commit; if you ever need ZIP
back, restore it from git rather than from this downgrade.

See docs/REVAMP_PLAN.md §3.3.

Revision ID: 0004
Revises: 0003
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0004"
down_revision: Union[str, Sequence[str], None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("tasks", "zip_code")


def downgrade() -> None:
    op.add_column("tasks", sa.Column("zip_code", sa.Text()))
