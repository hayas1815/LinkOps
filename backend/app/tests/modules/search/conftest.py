"""
Pytest configuration and shared fixtures for Search module tests.
"""

from __future__ import annotations

import asyncio
from typing import Generator
from unittest.mock import MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.search.repository import SearchRepository
from app.modules.search.service import SearchService


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


@pytest.fixture
def mock_repository(mock_session: MagicMock) -> MagicMock:
    """
    Fixture returning a mocked SearchRepository.
    """
    repo = MagicMock(spec=SearchRepository)
    repo.session = mock_session
    return repo


@pytest.fixture
def mock_service(mock_repository: MagicMock) -> MagicMock:
    """
    Fixture returning a mocked SearchService.
    """
    return MagicMock(spec=SearchService)
