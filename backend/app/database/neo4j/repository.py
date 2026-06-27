from neo4j import Driver

from app.database.neo4j.manager import neo4j_manager


class Neo4jRepositoryBase:
    """Base repository for future graph persistence adapters."""

    def __init__(self, driver: Driver | None = None) -> None:
        self.driver = driver or neo4j_manager.driver
