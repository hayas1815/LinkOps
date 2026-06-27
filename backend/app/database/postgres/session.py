"""
PostgreSQL async session dependency for repository injection.

Exposes ``get_db_session``, an async generator that yields a managed
``AsyncSession`` via ``PostgresConnectionManager.session_scope()``.
This is the low-level session provider for the postgres sub-package;
for FastAPI dependency injection prefer ``app.database.dependencies.get_db``.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgres.manager import postgres_manager


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Yield an async database session for repository usage.

    Delegates to ``postgres_manager.session_scope()`` so all
    commit/rollback/close semantics are handled consistently.

    Yields:
        An active ``AsyncSession`` for the current operation.
    """
    async with postgres_manager.session_scope() as session:
        yield session
