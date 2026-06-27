from time import perf_counter

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import get_logger, set_request_context


logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log every HTTP request with request context and execution timing."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        started_at = perf_counter()
        status_code = 500

        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        except Exception:
            execution_time = f"{perf_counter() - started_at:.6f}s"
            set_request_context(
                status_code=status_code,
                execution_time=execution_time,
            )
            raise
        finally:
            execution_time = f"{perf_counter() - started_at:.6f}s"
            set_request_context(
                status_code=status_code,
                execution_time=execution_time,
            )
            logger.info("HTTP request completed")
