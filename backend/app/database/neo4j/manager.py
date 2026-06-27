from neo4j import Driver, GraphDatabase

from app.core.config import get_settings


class Neo4jConnectionManager:
    """Manage Neo4j driver lifecycle and basic checks."""

    def __init__(self) -> None:
        self._driver: Driver | None = None

    @property
    def driver(self) -> Driver:
        if self._driver is None:
            settings = get_settings()
            if not settings.neo4j_uri:
                raise ValueError("NEO4J_URI is not configured")
            if not settings.neo4j_user or not settings.neo4j_password:
                raise ValueError("NEO4J_USER and NEO4J_PASSWORD must be configured")

            self._driver = GraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password),
            )
        return self._driver

    def health_check(self) -> bool:
        try:
            self.driver.verify_connectivity()
            with self.driver.session() as session:
                session.run("RETURN 1")
            return True
        except Exception:
            return False

    def close(self) -> None:
        if self._driver is not None:
            self._driver.close()


neo4j_manager = Neo4jConnectionManager()
