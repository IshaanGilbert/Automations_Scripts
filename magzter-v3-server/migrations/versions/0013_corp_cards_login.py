"""per-corporate card generation: tag each card with its corporate, store a card-gen
portal login per corporate. Also self-heals the tasks.email / tasks.name_used columns
the runtime engine relies on (dropped by 0003, re-added by hand in prod) so a fresh
migrate is self-consistent.

  cards.corp_id             which corporate (login) generated this card
  corporates.portal_username / portal_password   the MasterCard-portal login for THAT
                            corporate's cards (card_generation.py uses it per batch)

Revision ID: 0013
Revises: 0012
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0013"
down_revision: Union[str, Sequence[str], None] = "0012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("cards", sa.Column("corp_id", sa.Text()))
    op.create_index("idx_cards_corp", "cards", ["corp_id"])
    op.add_column("corporates", sa.Column("portal_username", sa.Text()))
    op.add_column("corporates", sa.Column("portal_password", sa.Text()))
    # self-heal the runtime-engine columns (see 0003_slim_tasks): IF NOT EXISTS so this
    # is a no-op where prod already added them by hand.
    op.execute("ALTER TABLE tasks ADD COLUMN IF NOT EXISTS email text")
    op.execute("ALTER TABLE tasks ADD COLUMN IF NOT EXISTS name_used text")


def downgrade() -> None:
    op.drop_column("corporates", "portal_password")
    op.drop_column("corporates", "portal_username")
    op.drop_index("idx_cards_corp", table_name="cards")
    op.drop_column("cards", "corp_id")
    # leave tasks.email / name_used in place — other code depends on them.
