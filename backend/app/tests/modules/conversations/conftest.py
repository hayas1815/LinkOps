"""
Shared fixtures for Conversations module tests.
"""
from __future__ import annotations
import asyncio
from typing import Generator
from unittest.mock import MagicMock
import pytest
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_session() -> MagicMock:
    return MagicMock(spec=AsyncSession)
