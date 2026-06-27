"""
Infrastructure dependency health report service.

Provides ``dependency_health_report``, which probes all backing services
(PostgreSQL, Neo4j, Redis, MinIO) and aggregates their statuses. The report
drives the ``/health`` and ``/health/db`` endpoints.

Also exposes ``warmup_infrastructure``, called during the application lifespan
startup to perform one-time setup tasks (pgvector extension, MinIO bucket
provisioning).
"""

from app.core.constants import HEALTH_STATUS, HEALTH_STATUS_DEGRADED
from app.database.neo4j import neo4j_manager
from app.database.postgres import postgres_manager
from app.database.redis import redis_manager
from app.database.storage import minio_storage


def _status(ok: bool) -> str:
    """
    Map a boolean health result to a status string.

    Args:
        ok: ``True`` if the dependency is healthy, ``False`` otherwise.

    Returns:
        ``HEALTH_STATUS`` if healthy, ``HEALTH_STATUS_DEGRADED`` otherwise.
    """
    return HEALTH_STATUS if ok else HEALTH_STATUS_DEGRADED


async def dependency_health_report() -> tuple[str, dict[str, str]]:
    """
    Probe all backing infrastructure services and return an aggregated report.

    Returns:
        A tuple of (overall_status, per_dependency_status_dict). The overall
        status is ``HEALTH_STATUS`` only when every dependency is healthy.
    """
    postgres_ok = await postgres_manager.health_check()
    neo4j_ok = neo4j_manager.health_check()
    redis_ok = await redis_manager.health_check()
    storage_ok = minio_storage.health_check()

    dependencies = {
        "backend": HEALTH_STATUS,
        "postgresql": _status(postgres_ok),
        "neo4j": _status(neo4j_ok),
        "redis": _status(redis_ok),
        "storage": _status(storage_ok),
    }

    overall = HEALTH_STATUS if all(
        item == HEALTH_STATUS
        for key, item in dependencies.items()
        if key != "backend"
    ) else HEALTH_STATUS_DEGRADED

    return overall, dependencies


async def warmup_infrastructure() -> None:
    """
    Perform one-time infrastructure setup tasks at application startup.

    Ensures the pgvector extension exists, MinIO buckets are provisioned,
    and backing services are reachable before the application accepts traffic.
    """
    await postgres_manager.ensure_pgvector_extension()
    minio_storage.ensure_buckets()
    await redis_manager.health_check()
    neo4j_manager.health_check()
