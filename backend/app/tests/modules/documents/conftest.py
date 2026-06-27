"""
Pytest configuration and shared fixtures for Document module tests.
"""

import asyncio
from typing import Generator
from unittest.mock import MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.documents.repository import DocumentRepository
from app.modules.documents.service import DocumentService


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
    Fixture returning a mocked DocumentRepository.
    """
    repo = MagicMock(spec=DocumentRepository)
    repo.session = mock_session
    return repo


@pytest.fixture
def mock_service(mock_repository: MagicMock) -> MagicMock:
    """
    Fixture returning a mocked DocumentService.
    """
    return MagicMock(spec=DocumentService)
