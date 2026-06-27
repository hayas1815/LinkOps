"""
Health check endpoints for the LinkOps API.

Exposes four endpoints:

- ``GET /health`` — lightweight liveness check confirming the API is up.
- ``GET /health/db`` — database readiness check that executes a live
  ``SELECT 1`` via the async session dependency to confirm PostgreSQL
  is reachable.
- ``GET /health/infra`` — full infrastructure readiness check that probes
  PostgreSQL, Redis, Neo4j, and MinIO, returning per-service status.
- ``GET /health/worker`` — Celery worker readiness check that pings the
  Redis broker and inspects active workers.
"""

import logging

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api.dependencies import SettingsDependency
from app.core.constants import (
    APP_ROUTER_TAG_HEALTH,
    APP_SERVICE_NAME,
    HEALTH_STATUS,
    HEALTH_STATUS_DEGRADED,
)
from app.database.dependencies import DatabaseSession
from app.shared.responses import HealthResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=[APP_ROUTER_TAG_HEALTH])


@router.get("/health", response_model=HealthResponse)
async def health_check(settings: SettingsDependency) -> HealthResponse:
    """
    Liveness check.

    Returns a simple healthy response confirming the API process is running.
    Does not probe any backing services.

    Args:
        settings: Injected application settings.

    Returns:
        A ``HealthResponse`` with status ``healthy``.
    """
    return HealthResponse(
        service=APP_SERVICE_NAME,
        status=HEALTH_STATUS,
        version=settings.app_version,
    )


@router.get(
    "/health/db",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
)
async def database_health_check(
    settings: SettingsDependency,
    db: DatabaseSession,
) -> HealthResponse:
    """
    Database readiness check.

    Executes ``SELECT 1`` against PostgreSQL via the async session dependency.
    Returns HTTP 200 with status ``healthy`` on success, or HTTP 503 with
    status ``degraded`` if the database is unreachable.

    Args:
        settings: Injected application settings.
        db: Injected async database session.

    Returns:
        A ``HealthResponse`` indicating database connectivity status.
    """
    try:
        await db.execute(text("SELECT 1"))
        db_status = HEALTH_STATUS
    except Exception:
        db_status = HEALTH_STATUS_DEGRADED

    response = HealthResponse(
        service=APP_SERVICE_NAME,
        status=db_status,
        version=settings.app_version,
        dependencies={"postgresql": db_status},
    )
    http_code = (
        status.HTTP_200_OK
        if db_status == HEALTH_STATUS
        else status.HTTP_503_SERVICE_UNAVAILABLE
    )
    return JSONResponse(content=response.model_dump(mode="json"), status_code=http_code)


@router.get(
    "/health/infra",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
)
async def infrastructure_health_check(
    settings: SettingsDependency,
) -> HealthResponse:
    """
    Full infrastructure readiness check.

    Probes all backing services (PostgreSQL, Redis, Neo4j, MinIO) via their
    respective connection managers and returns an aggregated status report.

    Returns HTTP 200 when all services are healthy, or HTTP 503 when any
    service is degraded.

    Response shape::

        {
            "service": "LinkOps Backend",
            "status": "healthy",
            "version": "1.0.0",
            "dependencies": {
                "postgres": "healthy",
                "redis": "healthy",
                "neo4j": "healthy",
                "minio": "healthy"
            }
        }

    Args:
        settings: Injected application settings.

    Returns:
        A ``HealthResponse`` with per-service dependency statuses.
    """
    from app.database.postgres import postgres_manager
    from app.database.redis import redis_manager
    from app.database.neo4j import neo4j_manager
    from app.database.storage import minio_storage

    def _status(ok: bool) -> str:
        return HEALTH_STATUS if ok else HEALTH_STATUS_DEGRADED

    # Probe each service independently, catching exceptions per-service
    # so one failure does not prevent reporting on the others.
    try:
        postgres_ok = await postgres_manager.health_check()
    except Exception:
        logger.warning("PostgreSQL health check failed", exc_info=True)
        postgres_ok = False

    try:
        redis_ok = await redis_manager.health_check()
    except Exception:
        logger.warning("Redis health check failed", exc_info=True)
        redis_ok = False

    try:
        neo4j_ok = neo4j_manager.health_check()
    except Exception:
        logger.warning("Neo4j health check failed", exc_info=True)
        neo4j_ok = False

    try:
        storage_ok = minio_storage.health_check()
    except Exception:
        logger.warning("MinIO health check failed", exc_info=True)
        storage_ok = False

    dependencies = {
        "postgres": _status(postgres_ok),
        "redis": _status(redis_ok),
        "neo4j": _status(neo4j_ok),
        "minio": _status(storage_ok),
    }

    all_healthy = all(v == HEALTH_STATUS for v in dependencies.values())
    overall = HEALTH_STATUS if all_healthy else HEALTH_STATUS_DEGRADED

    response = HealthResponse(
        service=APP_SERVICE_NAME,
        status=overall,
        version=settings.app_version,
        dependencies=dependencies,
    )
    http_code = (
        status.HTTP_200_OK
        if all_healthy
        else status.HTTP_503_SERVICE_UNAVAILABLE
    )
    return JSONResponse(content=response.model_dump(mode="json"), status_code=http_code)


@router.get(
    "/health/worker",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
)
async def worker_health_check(
    settings: SettingsDependency,
) -> HealthResponse:
    """
    Celery worker readiness check.

    Pings the Redis broker and runs a Celery ``inspect ping`` to detect
    live workers registered on the ``documents`` queue.

    Returns HTTP 200 when at least one worker responds, or HTTP 503 when
    no workers are reachable or the broker is unavailable.

    Response shape::

        {
            "service": "LinkOps Backend",
            "status": "healthy",
            "version": "1.0.0",
            "dependencies": {
                "redis_broker": "healthy",
                "celery_workers": "healthy"
            }
        }

    Args:
        settings: Injected application settings.

    Returns:
        A ``HealthResponse`` with broker and worker statuses.
    """
    import asyncio  # noqa: PLC0415

    # ── 1. Ping Redis broker ──────────────────────────────────────────────
    redis_broker_ok = False
    try:
        import redis as redis_lib  # noqa: PLC0415

        r = redis_lib.from_url(settings.redis_url, socket_connect_timeout=2)
        await asyncio.to_thread(r.ping)
        redis_broker_ok = True
    except Exception:
        logger.warning("Redis broker ping failed", exc_info=True)

    # ── 2. Inspect active Celery workers ─────────────────────────────────
    workers_ok = False
    try:
        from app.core.celery import celery_app as _celery  # noqa: PLC0415

        inspector = _celery.control.inspect(timeout=2)
        pong = await asyncio.to_thread(inspector.ping)
        workers_ok = bool(pong)
    except Exception:
        logger.warning("Celery worker inspection failed", exc_info=True)

    def _status(ok: bool) -> str:
        return HEALTH_STATUS if ok else HEALTH_STATUS_DEGRADED

    dependencies = {
        "redis_broker": _status(redis_broker_ok),
        "celery_workers": _status(workers_ok),
    }

    all_healthy = all(v == HEALTH_STATUS for v in dependencies.values())
    overall = HEALTH_STATUS if all_healthy else HEALTH_STATUS_DEGRADED

    response = HealthResponse(
        service=APP_SERVICE_NAME,
        status=overall,
        version=settings.app_version,
        dependencies=dependencies,
    )
    http_code = (
        status.HTTP_200_OK
        if all_healthy
        else status.HTTP_503_SERVICE_UNAVAILABLE
    )
    return JSONResponse(content=response.model_dump(mode="json"), status_code=http_code)
