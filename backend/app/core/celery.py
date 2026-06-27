"""
Celery application configuration for the LinkOps platform.

Configures a Celery application instance backed by Redis for task
brokering and result storage.  All settings are sourced from the
application Settings object so there are no hardcoded values.
"""

from __future__ import annotations

import logging
from celery import Celery
from celery.signals import setup_logging

from app.core.settings import get_settings

logger = logging.getLogger(__name__)

_settings = get_settings()


def _build_celery_app() -> Celery:
    """
    Construct and configure the Celery application instance.

    Returns:
        Celery: A fully configured Celery application ready for use.
    """
    app = Celery(
        "linkops",
        broker=_settings.redis_url,
        backend=_settings.redis_url,
        include=[
            "app.tasks.document_processing",
        ],
    )

    app.conf.update(
        # ── Serialisation ─────────────────────────────────────────
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        # ── Timezone ──────────────────────────────────────────────
        timezone="UTC",
        enable_utc=True,
        # ── Reliability ───────────────────────────────────────────
        task_acks_late=True,
        task_reject_on_worker_lost=True,
        # ── Result TTL ────────────────────────────────────────────
        result_expires=3600,
        # ── Worker concurrency ────────────────────────────────────
        worker_prefetch_multiplier=1,
        # ── Retry defaults (overridable per task) ─────────────────
        task_default_retry_delay=30,          # seconds
        task_max_retries=3,
        # ── Queues ────────────────────────────────────────────────
        task_default_queue="documents",
        task_queues={
            "documents": {
                "exchange": "documents",
                "routing_key": "documents",
            },
        },
    )

    logger.info("Celery application initialised (broker=%s)", _settings.redis_url)
    return app


@setup_logging.connect
def _configure_logging(**kwargs: object) -> None:  # type: ignore[misc]
    """
    Hook called by Celery to configure logging.

    Delegates to the application logging configuration so that Celery
    does not override the structured logging set up by the FastAPI app.
    """
    import logging.config  # noqa: PLC0415  (deferred import is intentional)

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                    "datefmt": "%Y-%m-%dT%H:%M:%S",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                }
            },
            "root": {
                "level": get_settings().log_level.upper(),
                "handlers": ["console"],
            },
        }
    )


# Module-level singleton used by the rest of the application.
celery_app: Celery = _build_celery_app()
