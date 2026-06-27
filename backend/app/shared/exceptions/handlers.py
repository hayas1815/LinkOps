from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.constants import (
    DEFAULT_CONTEXT_VALUE,
    HTTP_ERROR_MESSAGE,
    HTTP_STATUS_INTERNAL_ERROR,
    HTTP_STATUS_VALIDATION_ERROR,
    INTERNAL_ERROR_MESSAGE,
    REQUEST_ID_HEADER,
    VALIDATION_ERROR_MESSAGE,
)
from app.core.logging import get_logger
from app.shared.responses import ErrorResponse


logger = get_logger(__name__)


def _request_id(request: Request) -> str:
    return getattr(request.state, "request_id", DEFAULT_CONTEXT_VALUE)


def _log_extra(request: Request, status_code: int) -> dict[str, str]:
    return {
        "request_id": _request_id(request),
        "method": request.method,
        "path": request.url.path,
        "status_code": str(status_code),
        "execution_time": DEFAULT_CONTEXT_VALUE,
    }


def _error_response(
    *,
    request: Request,
    status_code: int,
    error: str,
) -> JSONResponse:
    request_id = _request_id(request)
    payload = ErrorResponse(error=error, request_id=request_id)
    return JSONResponse(
        status_code=status_code,
        content=payload.model_dump(mode="json"),
        headers={REQUEST_ID_HEADER: request_id},
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    logger.warning(
        "%s: %s",
        VALIDATION_ERROR_MESSAGE,
        exc.errors(),
        extra=_log_extra(request, HTTP_STATUS_VALIDATION_ERROR),
    )
    return _error_response(
        request=request,
        status_code=HTTP_STATUS_VALIDATION_ERROR,
        error=VALIDATION_ERROR_MESSAGE,
    )


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    detail = exc.detail if isinstance(exc.detail, str) else HTTP_ERROR_MESSAGE
    return _error_response(
        request=request,
        status_code=exc.status_code,
        error=detail,
    )


async def unhandled_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    logger.error(
        "Unhandled application error",
        extra=_log_extra(request, HTTP_STATUS_INTERNAL_ERROR),
    )
    return _error_response(
        request=request,
        status_code=HTTP_STATUS_INTERNAL_ERROR,
        error=INTERNAL_ERROR_MESSAGE,
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
