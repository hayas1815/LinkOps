"""
FastAPI database dependency injection providers.

This module exposes:

- ``get_db`` — an async generator dependency that yields a managed
  ``AsyncSession`` per request.
- ``DatabaseSession`` — an ``Annotated`` type alias for clean injection
  in route signatures.

Usage in a router::

    from app.database.dependencies import DatabaseSession

    @router.get("/items")
    async def list_items(db: DatabaseSession) -> list[ItemResponse]:
        repo = ItemRepository(db)
        return await repo.list()
"""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import session_manager


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides a per-request ``AsyncSession``.

    Opens a session via ``AsyncSessionManager.session()``, which commits on
    success and rolls back on any unhandled exception. The session is closed
    once the request completes.

    Yields:
        An active ``AsyncSession`` bound to the current request lifecycle.
    """
    async with session_manager.session() as session:
        yield session


# Annotated shorthand for injecting the database session into route handlers.
DatabaseSession = Annotated[AsyncSession, Depends(get_db)]
