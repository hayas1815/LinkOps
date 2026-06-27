import logging
from contextvars import ContextVar
from logging.config import dictConfig
from typing import Any

from app.core.constants import DEFAULT_CONTEXT_VALUE, LOG_FORMAT
from app.core.settings import Settings


request_id_context: ContextVar[str] = ContextVar(
    "request_id", default=DEFAULT_CONTEXT_VALUE
)
request_method_context: ContextVar[str] = ContextVar(
    "request_method", default=DEFAULT_CONTEXT_VALUE
)
request_path_context: ContextVar[str] = ContextVar(
    "request_path", default=DEFAULT_CONTEXT_VALUE
)
status_code_context: ContextVar[str] = ContextVar(
    "status_code", default=DEFAULT_CONTEXT_VALUE
)
execution_time_context: ContextVar[str] = ContextVar(
    "execution_time", default=DEFAULT_CONTEXT_VALUE
)


class RequestContextFilter(logging.Filter):
    """Inject request-scoped fields into every log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "request_id"):
            record.request_id = request_id_context.get()
        if not hasattr(record, "method"):
            record.method = request_method_context.get()
        if not hasattr(record, "path"):
            record.path = request_path_context.get()
        if not hasattr(record, "status_code"):
            record.status_code = status_code_context.get()
        if not hasattr(record, "execution_time"):
            record.execution_time = execution_time_context.get()
        return True


def set_request_context(
    *,
    request_id: str | None = None,
    method: str | None = None,
    path: str | None = None,
    status_code: int | str | None = None,
    execution_time: str | None = None,
) -> None:
    if request_id is not None:
        request_id_context.set(request_id)
    if method is not None:
        request_method_context.set(method)
    if path is not None:
        request_path_context.set(path)
    if status_code is not None:
        status_code_context.set(str(status_code))
    if execution_time is not None:
        execution_time_context.set(execution_time)


def clear_request_context() -> None:
    request_id_context.set(DEFAULT_CONTEXT_VALUE)
    request_method_context.set(DEFAULT_CONTEXT_VALUE)
    request_path_context.set(DEFAULT_CONTEXT_VALUE)
    status_code_context.set(DEFAULT_CONTEXT_VALUE)
    execution_time_context.set(DEFAULT_CONTEXT_VALUE)


def configure_logging(settings: Settings) -> None:
    """Configure process-wide structured console logging."""
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {
                "request_context": {
                    "()": RequestContextFilter,
                }
            },
            "formatters": {
                "default": {
                    "format": LOG_FORMAT,
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "filters": ["request_context"],
                }
            },
            "root": {
                "handlers": ["console"],
                "level": settings.log_level.upper(),
            },
        }
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def get_log_extra(**values: Any) -> dict[str, Any]:
    return values
