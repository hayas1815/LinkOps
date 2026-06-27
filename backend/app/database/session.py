"""
Async database session manager.

Provides ``AsyncSessionManager``, a lifecycle-aware class that owns the
``async_sessionmaker`` factory. It exposes:

- ``session()`` — an async context manager yielding a managed
  ``AsyncSession`` with automatic commit/rollback/close semantics.

A module-level singleton ``session_manager`` is provided for direct use
where FastAPI dependency injection is not available (e.g., startup hooks,
background workers, Alembic online migrations).
"""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.database.engine import get_async_engine


class AsyncSessionManager:
    """
    Manages the SQLAlchemy async session factory for the application.

    The session factory (``async_sessionmaker``) is created lazily on the
    first access and reused for every request, keeping the engine connection
    pool shared across all sessions.

    Attributes:
        _factory: The underlying ``async_sessionmaker`` instance, created
            on first use via the ``factory`` property.
    """

    def __init__(self) -> None:
        self._factory: async_sessionmaker[AsyncSession] | None = None

    @property
    def factory(self) -> async_sessionmaker[AsyncSession]:
        """
        Return the async session factory, creating it on the first call.

        Returns:
            The ``async_sessionmaker`` configured with the shared engine.
        """
        if self._factory is None:
            self._factory = async_sessionmaker(
                bind=get_async_engine(),
                autocommit=False,
                autoflush=False,
                expire_on_commit=False,
                class_=AsyncSession,
            )
        return self._factory

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        """
        Provide a transactional async database session.

        Yields an ``AsyncSession`` that commits on successful exit and rolls
        back on any exception. The session is always closed in the finally
        block regardless of outcome.

        Yields:
            An active ``AsyncSession`` for database operations.

        Raises:
            Exception: Re-raises any exception after rolling back the session.

        Example::

            async with session_manager.session() as db:
                result = await db.execute(select(MyModel))
        """
        async with self.factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()


# Module-level singleton for use outside FastAPI DI context.
session_manager = AsyncSessionManager()
