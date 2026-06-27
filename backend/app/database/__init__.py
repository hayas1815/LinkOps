"""
Database adapter boundary.

Exposes the shared infrastructure primitives used across the application:

- ``Base`` — SQLAlchemy declarative base for all ORM models.
- ``get_async_engine`` — async engine factory.
- ``session_manager`` — async session lifecycle manager.
- ``get_db`` / ``DatabaseSession`` — FastAPI dependency injection.
- ``postgres_manager`` — low-level PostgreSQL connection manager.
"""

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.database.dependencies import DatabaseSession, get_db
from app.database.engine import get_async_engine
from app.database.session import AsyncSessionManager, session_manager

__all__ = [
    "Base",
    "TimestampMixin",
    "UUIDPrimaryKeyMixin",
    "get_async_engine",
    "AsyncSessionManager",
    "session_manager",
    "get_db",
    "DatabaseSession",
]
