"""Alembic environment.

Resolves the DB URL with the same precedence db.py uses, so alembic always talks to
the database the bots talk to. See docs/REVAMP_PLAN.md §3.0.

URL precedence:
  1. ALEMBIC_DATABASE_URL  — override, for testing against a throwaway DB. Never set
                             this in production; it exists so you can round-trip
                             migrations locally without touching config.json.
  2. DATABASE_URL          — same env var db.py:88 honours.
  3. config.json DB_* keys — the normal path, plus the .db_local marker (db.py:101)
                             that forces 127.0.0.1 on the controller box where
                             Postgres is local and NAT hairpin blocks the public IP.
"""

import json
import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine import URL

# schema.py lives at the repo root, one level up from this package.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schema import metadata as target_metadata  # noqa: E402

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE = os.path.join(REPO_ROOT, "config.json")


def _normalise(url: str) -> str:
    """postgres:// and postgresql:// -> postgresql+psycopg2:// (SQLAlchemy needs the driver)."""
    if url.startswith("postgres://"):
        return "postgresql+psycopg2://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        return "postgresql+psycopg2://" + url[len("postgresql://"):]
    return url


def _url_from_config() -> str:
    if not os.path.exists(CONFIG_FILE):
        raise RuntimeError(
            f"config.json not found at {CONFIG_FILE} and neither ALEMBIC_DATABASE_URL "
            f"nor DATABASE_URL is set — alembic has no database to talk to."
        )
    with open(CONFIG_FILE) as fh:
        cfg = json.load(fh)

    if cfg.get("DATABASE_URL"):
        return _normalise(cfg["DATABASE_URL"])

    host = (cfg.get("DB_HOST") or "").strip()
    # Mirrors db.py:101 — on the controller, Postgres is local and the public
    # DB_HOST is unreachable via NAT hairpin.
    if os.path.exists(os.path.join(REPO_ROOT, ".db_local")):
        host = "127.0.0.1"

    return URL.create(
        "postgresql+psycopg2",
        username=cfg.get("DB_USER"),
        password=cfg.get("DB_PASSWORD"),
        host=host or "127.0.0.1",
        port=int(cfg.get("DB_PORT") or 5432),
        database=cfg.get("DB_NAME"),
    ).render_as_string(hide_password=False)


def get_url() -> str:
    if os.environ.get("ALEMBIC_DATABASE_URL"):
        return _normalise(os.environ["ALEMBIC_DATABASE_URL"])
    if os.environ.get("DATABASE_URL"):
        return _normalise(os.environ["DATABASE_URL"])
    return _url_from_config()


def run_migrations_offline() -> None:
    """Render SQL to stdout without a DB — `alembic upgrade head --sql`.

    Lets you review exactly what will run against production before it does.
    """
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    section = config.get_section(config.config_ini_section, {})
    section["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        section, prefix="sqlalchemy.", poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # Both matter for the §3.0 "autogenerate must be empty" check — without
            # them, type and server-default drift goes undetected and the check
            # passes falsely.
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
