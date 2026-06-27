"""
Shared SQLAlchemy declarative base and common model mixins.

This module is the single source of truth for the ORM base class. All
domain models must inherit from ``Base`` defined here so that Alembic
autogenerate can discover every table via ``Base.metadata``.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    Project-wide SQLAlchemy declarative base.

    All ORM models must subclass ``Base`` so their table metadata is
    registered under ``Base.metadata`` for Alembic migrations.
    """

    pass


class UUIDPrimaryKeyMixin:
    """
    Mixin that adds a UUID primary key column named ``id``.

    Usage::

        class MyModel(UUIDPrimaryKeyMixin, Base):
            __tablename__ = "my_table"
    """

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )


class TimestampMixin:
    """
    Mixin that adds server-side ``created_at`` and ``updated_at`` timestamp
    columns to any model.

    Both columns are timezone-aware and default to the current UTC time via
    the database server. ``updated_at`` is automatically refreshed on every
    UPDATE.

    Usage::

        class MyModel(TimestampMixin, Base):
            __tablename__ = "my_table"
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
