from fastapi import APIRouter

from app.api.dependencies import SettingsDependency
from app.core.constants import (
    APP_ROUTER_TAG_HEALTH,
    APP_SERVICE_NAME,
    HEALTH_STATUS,
)
from app.shared.responses import HealthResponse


router = APIRouter(tags=[APP_ROUTER_TAG_HEALTH])


@router.get("/health", response_model=HealthResponse)
async def health_check(settings: SettingsDependency) -> HealthResponse:
    return HealthResponse(
        service=APP_SERVICE_NAME,
        status=HEALTH_STATUS,
        version=settings.app_version,
    )
