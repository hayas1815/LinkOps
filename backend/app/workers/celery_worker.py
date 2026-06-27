"""
Celery worker entrypoint for the LinkOps platform.

Usage
-----
Run from the ``backend/`` directory:

    celery -A app.workers.celery_worker:celery_app worker \\
        --loglevel=info \\
        --queues=documents \\
        --concurrency=4

Or via the convenience script defined in the Makefile / docker-compose:

    make worker
"""

from __future__ import annotations

# Re-export the application singleton so Celery's CLI discovery finds it.
from app.core.celery import celery_app as celery_app  # noqa: F401

# Ensure all tasks are registered when the worker imports this module.
import app.tasks.document_processing  # noqa: F401
