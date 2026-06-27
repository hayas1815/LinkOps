"""
Pytest configuration and shared fixtures for Copilot module tests.
"""

from __future__ import annotations

import asyncio
from typing import Generator
from unittest.mock import MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """
    Create an instance of the default event loop for each test case.
    """
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_session() -> MagicMock:
    """
    Fixture returning a mocked SQLAlchemy AsyncSession.
    """
    return MagicMock(spec=AsyncSession)
