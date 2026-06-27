from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.health import router as health_router
from app.api.v1.root import router as root_router
from app.core.config import Settings, get_settings
from app.core.constants import BACKEND_SHUTDOWN_LOG_MESSAGE, BACKEND_STARTUP_LOG_MESSAGE
from app.core.logging import configure_logging, get_logger
from app.middleware.logging import RequestLoggingMiddleware
from app.middleware.request_id import RequestIDMiddleware
from app.shared.exceptions.handlers import register_exception_handlers


settings: Settings = get_settings()
configure_logging(settings)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    """Manage application lifecycle hooks."""
    logger.info(BACKEND_STARTUP_LOG_MESSAGE)
    application.state.settings = settings
    yield
    logger.info(BACKEND_SHUTDOWN_LOG_MESSAGE)


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=settings.app_description,
    docs_url=settings.docs_url,
    redoc_url=settings.redoc_url,
    openapi_url=settings.openapi_url,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=list(settings.cors_allow_methods),
    allow_headers=list(settings.cors_allow_headers),
)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RequestIDMiddleware)

register_exception_handlers(app)

# Public operational endpoints.
app.include_router(root_router)
app.include_router(health_router)

# Versioned API contract. These endpoints intentionally mirror the public
# bootstrap endpoints until feature modules are introduced.
app.include_router(root_router, prefix=settings.api_v1_prefix)
app.include_router(health_router, prefix=settings.api_v1_prefix)

# Feature Module Routers
from app.modules.documents.router import router as documents_router
from app.modules.search.router import router as search_router
from app.modules.copilot.router import router as copilot_router
from app.modules.conversations.router import router as conversations_router

app.include_router(documents_router)
app.include_router(search_router)
app.include_router(copilot_router)
app.include_router(conversations_router)
