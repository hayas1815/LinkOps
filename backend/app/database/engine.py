"""
SQLAlchemy 2.0 async engine factory for PostgreSQL.

This module creates and caches a single ``AsyncEngine`` instance for the
lifetime of the process. The engine uses the ``asyncpg`` driver and applies
production-ready connection pool settings sourced from application settings.

Pool defaults:
    - pool_size: 10 — persistent connections kept alive.
    - max_overflow: 20 — additional burst connections beyond pool_size.
    - pool_pre_ping: True — validate connections before checkout.
    - pool_recycle: 3600 — recycle connections after 1 hour to avoid
      stale connections dropped by the database or load balancer.
"""

from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.core.config import get_settings

# Default pool tuning constants.
DEFAULT_POOL_SIZE: int = 10
DEFAULT_MAX_OVERFLOW: int = 20
DEFAULT_POOL_RECYCLE: int = 3600  # seconds


def _build_async_url(database_url: str) -> str:
    """
    Convert a synchronous PostgreSQL URL to an asyncpg-compatible URL.

    Replaces ``postgresql+psycopg`` or bare ``postgresql`` scheme with
    ``postgresql+asyncpg`` so that SQLAlchemy routes all I/O through
    the asyncpg driver.

    Args:
        database_url: A PostgreSQL connection string, potentially using
            the psycopg or plain postgresql scheme.

    Returns:
        A connection string with the ``postgresql+asyncpg`` scheme.
    """
    if database_url.startswith("postgresql+psycopg"):
        return database_url.replace("postgresql+psycopg", "postgresql+asyncpg", 1)
    if database_url.startswith("postgresql://") or database_url.startswith(
        "postgresql+psycopg2"
    ):
        return "postgresql+asyncpg" + database_url[database_url.index("://"):]
    # Already asyncpg or unknown scheme — return unchanged.
    return database_url


@lru_cache(maxsize=1)
def get_async_engine() -> AsyncEngine:
    """
    Create and cache the project-wide SQLAlchemy async engine.

    The engine is created once at the first call and reused for every
    subsequent call. Pool settings are sourced from application settings
    if available, falling back to module-level defaults.

    Returns:
        The cached ``AsyncEngine`` instance.

    Raises:
        ValueError: If ``DATABASE_URL`` is not configured in settings.
    """
    settings = get_settings()
    if not settings.database_url:
        raise ValueError(
            "DATABASE_URL is not configured. "
            "Set the DATABASE_URL environment variable."
        )

    async_url = _build_async_url(settings.database_url)

    return create_async_engine(
        async_url,
        echo=settings.debug,
        pool_size=DEFAULT_POOL_SIZE,
        max_overflow=DEFAULT_MAX_OVERFLOW,
        pool_pre_ping=True,
        pool_recycle=DEFAULT_POOL_RECYCLE,
        future=True,
    )
