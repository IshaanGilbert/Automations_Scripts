"""telegram_accounts + telegram_sources — Telegram ko OTP provider banane ka config

Telegram baaki providers jaisa nahi hai. smsindia/techyindia stateless HTTP API hain,
inhe 20 instance ek saath call kar sakte hain. Telegram me ek Telethon session = ek
Telegram ACCOUNT = ek chat, aur us chat me do kaam ek saath nahi ho sakte. Isliye do
alag tables:

    telegram_accounts  -> CAPACITY. Ek account ek waqt me ek number laa sakta hai.
    telegram_sources   -> VENDOR. Kaun sa bot/channel, aur uska menu kaisa hai.

Ek account se do bot use ho sakte hain (do sources, same account) — par tab bhi wo
account ek waqt me ek hi kaam karega. Speed accounts badhane se aati hai, bots se nahi.

`profile` JSONB me bot ka poora menu flow rehta hai (steps, buttons, keywords) — wahi
jo abhi telegram_bot_scraper/config.py me hardcoded hai. JSON isliye ki naya vendor bot
jodna ek row daalna ho, code likhna nahi: har bot ka menu alag hota hai.

Revision ID: 0011
Revises: 0010
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0011"
down_revision: Union[str, Sequence[str], None] = "0010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "telegram_accounts",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("label", sa.Text(), nullable=False),          # "acct-A"
        sa.Column("phone", sa.Text(), nullable=False),          # +91...
        sa.Column("api_id", sa.Text()),                         # my.telegram.org se
        sa.Column("api_hash", sa.Text()),
        # Login ek baar hota hai aur Telegram us number par OTP bhejta hai — wo aadmi ko
        # daalna padta hai. Uske baad ye file ban jaati hai aur account chalta rehta hai.
        sa.Column("session_file", sa.Text()),
        sa.Column("session_ok", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("enabled", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("busy_until", sa.DateTime(timezone=True)),    # broker ka lock
        sa.Column("last_used_at", sa.DateTime(timezone=True)),
        sa.Column("last_error", sa.Text()),
        sa.Column("note", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("label", name="uq_telegram_accounts_label"),
    )

    op.create_table(
        "telegram_sources",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("label", sa.Text(), nullable=False),          # "acct-A / ulotpbot"
        sa.Column("account_id", sa.BigInteger(),
                  sa.ForeignKey("telegram_accounts.id"), nullable=False),
        # bot    = number bhi kharidta hai, OTP bhi deta hai (menu flow chahiye)
        # channel = number kahin aur se, yahan sirf OTP girta hai (parser chahiye)
        sa.Column("kind", sa.Text(), nullable=False, server_default="bot"),
        sa.Column("target", sa.Text(), nullable=False),         # @ulotpbot / channel id
        sa.Column("service_command", sa.Text()),                # /find_NYKAA
        sa.Column("profile", postgresql.JSONB()),               # steps/buttons/keywords
        sa.Column("priority", sa.Integer(), server_default=sa.text("100")),
        sa.Column("enabled", sa.Boolean(), server_default=sa.text("true")),
        # Balance khatam hone par broker ise khud band kar deta hai, warna har baar ek
        # slot ka waqt khaata hai.
        sa.Column("status", sa.Text(), server_default="idle"),
        sa.Column("last_error", sa.Text()),
        sa.Column("last_used_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("label", name="uq_telegram_sources_label"),
    )
    op.create_index("idx_telegram_sources_pick", "telegram_sources",
                    ["enabled", "priority", "last_used_at"])


def downgrade() -> None:
    op.drop_index("idx_telegram_sources_pick", table_name="telegram_sources")
    op.drop_table("telegram_sources")
    op.drop_table("telegram_accounts")
