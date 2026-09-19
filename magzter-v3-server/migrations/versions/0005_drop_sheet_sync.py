"""drop sheet sync — Google Sheets is gone

sheet_row and synced_to_sheet only ever existed to mirror rows to/from Google Sheets.
sync_tasks.py is deleted, gspread is out of requirements, and the DB is the only
source of truth — so these columns now describe a system that no longer exists.

Dropped here:
  tasks.sheet_row, tasks.synced_to_sheet      + idx_tasks_unsynced
  read_tasks.sheet_row, read_tasks.synced_to_sheet + idx_read_unsynced

read_tasks.sheet_row was the reader row's identity; source_task_id (added in 0002)
replaces it — db._to_read_task must read that instead, or the reader crashes on its
first claim after this runs.

REVERSIBLE, but only structurally: downgrade re-adds the columns empty. The Sheets
integration itself is not coming back.

Revision ID: 0005
Revises: 0004
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0005"
down_revision: Union[str, Sequence[str], None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Partial indexes over synced_to_sheet — meaningless without the column.
    op.drop_index("idx_tasks_unsynced", table_name="tasks")
    op.drop_index("idx_read_unsynced", table_name="read_tasks")

    op.drop_column("tasks", "synced_to_sheet")
    op.drop_column("tasks", "sheet_row")
    op.drop_column("read_tasks", "synced_to_sheet")
    op.drop_column("read_tasks", "sheet_row")


def downgrade() -> None:
    op.add_column("read_tasks", sa.Column("sheet_row", sa.Integer(), unique=True))
    op.add_column("read_tasks", sa.Column("synced_to_sheet", sa.Boolean(), nullable=False,
                                          server_default=sa.text("true")))
    op.add_column("tasks", sa.Column("sheet_row", sa.Integer(), unique=True))
    op.add_column("tasks", sa.Column("synced_to_sheet", sa.Boolean(), nullable=False,
                                     server_default=sa.text("true")))
    op.create_index("idx_read_unsynced", "read_tasks", ["synced_to_sheet"],
                    postgresql_where=sa.text("synced_to_sheet = false"))
    op.create_index("idx_tasks_unsynced", "tasks", ["synced_to_sheet"],
                    postgresql_where=sa.text("synced_to_sheet = false"))
