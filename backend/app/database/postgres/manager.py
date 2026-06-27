"""
PostgreSQL async connection manager.

Provides ``PostgresConnectionManager``, a lifecycle-aware manager that owns
the ``AsyncEngine`` and ``async_sessionmaker`` for the PostgreSQL database.
It is the low-level counterpart to ``app.database.session.AsyncSessionManager``
and is primarily used by the infrastructure health service and startup hooks.

A module-level singleton ``postgres_manager`` is exported for use throughout
the application.
"""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings


def _to_async_url(database_url: str) -> str:
    """
    Normalise a PostgreSQL URL to use the ``asyncpg`` driver scheme.

    Args:
        database_url: A PostgreSQL connection string, potentially using
            the psycopg or plain postgresql scheme.

    Returns:
        A connection string prefixed with ``postgresql+asyncpg``.
    """
    if database_url.startswith("postgresql+psycopg"):
        return database_url.replace("postgresql+psycopg", "postgresql+asyncpg", 1)
    if "://" in database_url and not database_url.startswith("postgresql+asyncpg"):
        return "postgresql+asyncpg" + database_url[database_url.index("://"):]
    return database_url


class PostgresConnectionManager:
    """
    Manage the PostgreSQL async engine lifecycle and session factory.

    This class lazily constructs the ``AsyncEngine`` on first access and
    caches it for reuse. It provides convenience methods for health checks,
    pgvector extension setup, and transaction-scoped session management.

    Attributes:
        _engine: The ``AsyncEngine`` instance, created on first access.
        _session_factory: The ``async_sessionmaker`` bound to the engine.
    """

    def __init__(self) -> None:
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None

    def _create_engine(self) -> AsyncEngine:
        """
        Build a new ``AsyncEngine`` from current application settings.

        Returns:
            A configured ``AsyncEngine`` using the asyncpg driver.

        Raises:
            ValueError: If ``DATABASE_URL`` is not set in settings.
        """
        settings = get_settings()
        if not settings.database_url:
            raise ValueError("DATABASE_URL is not configured")

        async_url = _to_async_url(settings.database_url)
        return create_async_engine(
            async_url,
            pool_pre_ping=True,
            future=True,
        )

    @property
    def engine(self) -> AsyncEngine:
        """
        Return the async engine, creating it on the first call.

        Returns:
            The cached ``AsyncEngine`` instance.
        """
        if self._engine is None:
            self._engine = self._create_engine()
        return self._engine

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        """
        Return the async session factory, creating it on the first call.

        Returns:
            The ``async_sessionmaker`` bound to the engine.
        """
        if self._session_factory is None:
            self._session_factory = async_sessionmaker(
                bind=self.engine,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False,
                class_=AsyncSession,
            )
        return self._session_factory

    @asynccontextmanager
    async def session_scope(self) -> AsyncIterator[AsyncSession]:
        """
        Provide a transactional async session context manager.

        Commits on success, rolls back on exception, and always closes the
        session on exit.

        Yields:
            An ``AsyncSession`` for performing database operations.

        Raises:
            Exception: Re-raises any exception after rolling back.
        """
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def ensure_pgvector_extension(self) -> None:
        """
        Create the pgvector extension in the database if it does not exist.

        Requires the PostgreSQL server to have the ``vector`` extension
        available (shipped with ``pgvector``).
        """
        async with self.engine.begin() as conn:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))

    async def health_check(self) -> bool:
        """
        Verify that the database is reachable by executing ``SELECT 1``.

        Returns:
            ``True`` if the database responds successfully, ``False`` otherwise.
        """
        try:
            conn: AsyncConnection
            async with self.engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    async def dispose(self) -> None:
        """
        Dispose of the engine connection pool.

        Should be called during application shutdown to cleanly close all
        pooled database connections.
        """
        if self._engine is not None:
            await self._engine.dispose()


postgres_manager = PostgresConnectionManager()
