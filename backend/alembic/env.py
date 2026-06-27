"""
Alembic migration environment for LinkOps.

This module configures the Alembic migration context for both offline
(SQL script generation) and online (live database) modes. It uses the
SQLAlchemy asyncpg driver and loads the database URL from application
settings so that ``.env`` files drive migration behaviour without
editing this file.

All models that should be included in autogenerate must have their
``Base.metadata`` discoverable here. Import any new model modules below
the ``# --- Model imports ---`` marker so their tables are registered.
"""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

# Alembic Config object — provides access to values in alembic.ini.
config = context.config

# Set up Python logging from the alembic.ini [loggers] section.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---------------------------------------------------------------------------
# Application imports
# ---------------------------------------------------------------------------
# Load application settings to source DATABASE_URL from the environment.
from app.core.config import get_settings  # noqa: E402

# Import the shared Base — this is the single metadata registry used by
# Alembic autogenerate.
from app.database.base import Base  # noqa: E402

# --- Model imports ---------------------------------------------------------
# Import every model module so SQLAlchemy registers their Table objects in
# Base.metadata before autogenerate runs.
import app.modules.documents.models  # noqa: F401, E402
# ---------------------------------------------------------------------------

settings = get_settings()

# Override sqlalchemy.url with the value from application settings so that
# alembic.ini does not need to be modified per environment.
config.set_main_option("sqlalchemy.url", settings.database_url)

# target_metadata is used by autogenerate to diff the current schema against
# the ORM models.
target_metadata = Base.metadata


def _to_async_url(url: str) -> str:
    """Convert a PostgreSQL URL to the asyncpg driver scheme."""
    if url.startswith("postgresql+psycopg"):
        return url.replace("postgresql+psycopg", "postgresql+asyncpg", 1)
    if "://" in url and not url.startswith("postgresql+asyncpg"):
        return "postgresql+asyncpg" + url[url.index("://"):]
    return url


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    In offline mode Alembic generates a SQL script rather than connecting
    to a live database. This is useful for reviewing migrations before
    applying them, or for applying them via a DBA.
    """
    url = settings.database_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """
    Execute migrations using an established synchronous connection wrapper.

    Args:
        connection: A synchronous ``Connection`` object, provided by the
            async runner after yielding from ``run_sync``.
    """
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    Run migrations in 'online' mode using the asyncpg driver.

    Creates a temporary async engine (separate from the application pool so
    migrations use ``NullPool``), connects, and delegates to
    ``do_run_migrations`` via ``run_sync``.
    """
    async_url = _to_async_url(settings.database_url)

    connectable = create_async_engine(
        async_url,
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """
    Entry point for online migration mode.

    Wraps the async migration runner in ``asyncio.run`` so Alembic's
    synchronous CLI can drive the async migration flow.
    """
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
