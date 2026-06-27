from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from app.core.constants import HEALTH_STATUS


def utc_timestamp() -> datetime:
    return datetime.now(UTC)


class RootResponse(BaseModel):
    message: str


class HealthResponse(BaseModel):
    service: str
    status: str = Field(default=HEALTH_STATUS)
    version: str
    dependencies: dict[str, str] | None = None


class SuccessResponse(BaseModel):
    success: Literal[True] = True
    message: str
    data: Any = None
    request_id: str
    timestamp: datetime = Field(default_factory=utc_timestamp)


class ErrorResponse(BaseModel):
    success: Literal[False] = False
    error: str
    request_id: str
    timestamp: datetime = Field(default_factory=utc_timestamp)
