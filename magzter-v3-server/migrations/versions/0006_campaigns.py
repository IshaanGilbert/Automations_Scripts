"""campaigns — monthly budget + daily plan, replacing the flat quotas model

The spec grew: a target is no longer a single number. A CAMPAIGN is a monthly budget
with a computed daily plan (a per-date row of how many to do that day), a 4-5 day
buffer, and its own uploaded email list. Cards, identities and transactions belong to
a campaign.

  campaigns       one per month. budget is editable; the plan recomputes.
  campaign_days   one row per date — planned target for that day, editable + pinnable.

`quotas` is replaced entirely: campaign.budget IS the cards target (cards never exceed
it), and campaign_days.planned for today IS the daily transactions target. So the
quota_id FKs become campaign_id and quotas is dropped.

DATA NOTE: written for the fresh campaign DB. On dev it drops the seed's quota links;
seed_dev.py is rewritten to create a campaign. No prod data exists — the old sheet-era
stack runs on its own untouched DB.

Revision ID: 0006
Revises: 0005
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0006"
down_revision: Union[str, Sequence[str], None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# The pool tables and their existing (autonamed) quota FK — see
# `SELECT conname FROM pg_constraint WHERE conname LIKE '%quota%'`.
_QUOTA_FK = {
    "cards": "0000000000000000",
    "identities": "identities_quota_id_fkey",
    "tasks": "fk_tasks_quota",
}


def upgrade() -> None:
    op.create_table(
        "campaigns",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("budget", sa.Integer(), nullable=False),      # editable monthly target
        sa.Column("buffer_days", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),       # month end
        sa.Column("status", sa.Text(), nullable=False, server_default="active"),
        # Constant account password, snapshotted per campaign (as it was per quota):
        # rotating it never orphans accounts made under an earlier campaign.
        sa.Column("account_password", sa.Text(), nullable=False),
        # Alert when unused emails drop below this many DAYS of runway (§email alert).
        sa.Column("email_alert_days", sa.Integer(), nullable=False, server_default="2"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.CheckConstraint("budget > 0", name="ck_campaigns_budget"),
        sa.CheckConstraint("buffer_days >= 0", name="ck_campaigns_buffer"),
        sa.CheckConstraint("end_date >= start_date", name="ck_campaigns_dates"),
        sa.CheckConstraint("status IN ('active','paused','done')", name="ck_campaigns_status"),
    )
    # One active campaign at a time — the daily gate needs an unambiguous "today's plan".
    op.create_index("uq_campaign_active", "campaigns", ["status"], unique=True,
                    postgresql_where=sa.text("status = 'active'"))

    op.create_table(
        "campaign_days",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("campaign_id", sa.BigInteger(),
                  sa.ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False),
        sa.Column("day", sa.Date(), nullable=False),
        sa.Column("planned", sa.Integer(), nullable=False, server_default="0"),
        # pinned = admin set this day by hand; rebalance leaves it and spreads the
        # remaining budget across the other future days.
        sa.Column("pinned", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.CheckConstraint("planned >= 0", name="ck_campaign_days_planned"),
    )
    op.create_index("uq_campaign_day", "campaign_days", ["campaign_id", "day"], unique=True)
    op.create_index("idx_campaign_days_day", "campaign_days", ["day"])

    # ---- repoint the pool tables from quota -> campaign ----------------------
    for tbl in ("cards", "identities", "tasks"):
        op.add_column(tbl, sa.Column("campaign_id", sa.BigInteger()))
        op.create_foreign_key(f"fk_{tbl}_campaign", tbl, "campaigns", ["campaign_id"], ["id"])
        op.create_index(f"idx_{tbl}_campaign", tbl, ["campaign_id"])

    # Emails belong to a campaign (upload is per-campaign). Nullable so a legacy address
    # without a campaign is still valid.
    op.add_column("emails", sa.Column("campaign_id", sa.BigInteger()))
    op.create_foreign_key("fk_emails_campaign", "emails", "campaigns", ["campaign_id"], ["id"])
    op.create_index("idx_emails_campaign", "emails", ["campaign_id"])

    # ---- drop the quotas model ----------------------------------------------
    for tbl in ("cards", "identities", "tasks"):
        op.drop_constraint(_QUOTA_FK[tbl], tbl, type_="foreignkey")
        op.drop_column(tbl, "quota_id")
    op.drop_index("uq_quota_active", table_name="quotas")
    op.drop_table("quotas")


def downgrade() -> None:
    op.create_table(
        "quotas",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("kind", sa.Text(), nullable=False),
        sa.Column("period", sa.Text(), nullable=False),
        sa.Column("qty", sa.Integer(), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False, server_default="active"),
        sa.Column("account_password", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("uq_quota_active", "quotas", ["kind", "period"], unique=True,
                    postgresql_where=sa.text("status = 'active'"))
    # Re-add quota_id AND its FK index. Postgres auto-dropped these indexes when
    # upgrade() dropped the columns, so without recreating them here the 0005 state
    # isn't fully restored and 0003's downgrade (which drops idx_tasks_quota) fails.
    _quota_idx = {"cards": "0000000000000000", "identities": "idx_identities_quota",
                  "tasks": "idx_tasks_quota"}
    for tbl in ("cards", "identities", "tasks"):
        op.add_column(tbl, sa.Column("quota_id", sa.BigInteger()))
        op.create_foreign_key(_QUOTA_FK[tbl], tbl, "quotas", ["quota_id"], ["id"])
        op.create_index(_quota_idx[tbl], tbl, ["quota_id"])

    op.drop_index("idx_emails_campaign", table_name="emails")
    op.drop_constraint("fk_emails_campaign", "emails", type_="foreignkey")
    op.drop_column("emails", "campaign_id")
    for tbl in ("cards", "identities", "tasks"):
        op.drop_index(f"idx_{tbl}_campaign", table_name=tbl)
        op.drop_constraint(f"fk_{tbl}_campaign", tbl, type_="foreignkey")
        op.drop_column(tbl, "campaign_id")

    op.drop_index("idx_campaign_days_day", table_name="campaign_days")
    op.drop_index("uq_campaign_day", table_name="campaign_days")
    op.drop_table("campaign_days")
    op.drop_index("uq_campaign_active", table_name="campaigns")
    op.drop_table("campaigns")
