"""reader proof screenshot: when a read finds NO order id on my_orders, the reader saves
a full-page screenshot as proof and records where it lives, so the operator can see the
evidence right on that row.

  read_tasks.proof_shot   relative path of the proof screenshot under the runner's
                          screenshots/ dir (e.g. 'instance5/NOORDER_foo.png')
  read_tasks.proof_node   which node/server holds that file (NODE_NAME), so the dashboard
                          can fetch it via the screenshot proxy; 'local' = the controller

Revision ID: 0014
Revises: 0013
"""

from typing import Sequence, Union

from alembic import op


revision: str = "0014"
down_revision: Union[str, Sequence[str], None] = "0013"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # IF NOT EXISTS so a prod DB that already got these by hand is a no-op.
    op.execute("ALTER TABLE read_tasks ADD COLUMN IF NOT EXISTS proof_shot text")
    op.execute("ALTER TABLE read_tasks ADD COLUMN IF NOT EXISTS proof_node text")


def downgrade() -> None:
    op.execute("ALTER TABLE read_tasks DROP COLUMN IF EXISTS proof_node")
    op.execute("ALTER TABLE read_tasks DROP COLUMN IF EXISTS proof_shot")
