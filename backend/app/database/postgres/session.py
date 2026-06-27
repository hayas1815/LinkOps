from collections.abc import Generator

from sqlalchemy.orm import Session

from app.database.postgres.manager import postgres_manager


def get_db_session() -> Generator[Session, None, None]:
    """Yield a database session for future repository usage."""
    with postgres_manager.session_scope() as session:
        yield session
