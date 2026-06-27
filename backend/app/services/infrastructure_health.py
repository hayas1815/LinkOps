from app.core.constants import HEALTH_STATUS, HEALTH_STATUS_DEGRADED
from app.database.neo4j import neo4j_manager
from app.database.postgres import postgres_manager
from app.database.redis import redis_manager
from app.database.storage import minio_storage


def _status(ok: bool) -> str:
    return HEALTH_STATUS if ok else HEALTH_STATUS_DEGRADED


async def dependency_health_report() -> tuple[str, dict[str, str]]:
    postgres_ok = postgres_manager.health_check()
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
    postgres_manager.ensure_pgvector_extension()
    minio_storage.ensure_buckets()
    await redis_manager.health_check()
    neo4j_manager.health_check()
