"""
Health check endpoints for the LinkOps API.

Exposes two endpoints:

- ``GET /health`` — lightweight liveness check confirming the API is up.
- ``GET /health/db`` — database readiness check that executes a live
  ``SELECT 1`` via the async session dependency to confirm PostgreSQL
  is reachable.
"""

from fastapi import APIRouter, status
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
        http_status = status.HTTP_200_OK
    except Exception:
        db_status = HEALTH_STATUS_DEGRADED
        http_status = status.HTTP_503_SERVICE_UNAVAILABLE

    return HealthResponse(
        service=APP_SERVICE_NAME,
        status=db_status,
        version=settings.app_version,
        dependencies={"postgresql": db_status},
    ), http_status  # type: ignore[return-value]
