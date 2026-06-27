"""
Document processing Celery task.

Implements the asynchronous document processing pipeline:

    UPLOADED → QUEUED → PROCESSING → TEXT_EXTRACTED → CHUNKING → EMBEDDING → PROCESSED
                                   ↘ FAILED  (on unrecoverable error)

Each stage is committed to the database immediately so that the API
can surface status changes in real-time.
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from celery import Task
from celery.exceptions import MaxRetriesExceededError

from app.core.celery import celery_app
from app.modules.documents.enums import DocumentStatus


logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sync_get_db_session():
    """
    Create a *synchronous* SQLAlchemy session suitable for use inside the
    Celery worker process, which runs in a plain synchronous context.

    We intentionally avoid the async session because Celery tasks run inside
    a regular thread, not an asyncio event loop.
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from app.core.settings import get_settings

    settings = get_settings()

    # Normalise async driver prefix so the sync engine does not break
    db_url: str = settings.database_url
    for async_prefix, sync_prefix in (
        ("postgresql+asyncpg", "postgresql+psycopg"),
        ("postgresql+asyncpg", "postgresql"),
    ):
        if db_url.startswith(async_prefix):
            db_url = db_url.replace(async_prefix, sync_prefix, 1)
            break

    engine = create_engine(db_url, echo=False)
    return Session(engine)


def _update_document_status(
    document_id: str,
    status: DocumentStatus,
    *,
    failure_reason: str | None = None,
    processing_started_at: datetime | None = None,
    processing_completed_at: datetime | None = None,
    extracted_text: str | None = None,
    page_count: int | None = None,
    extraction_method: str | None = None,
    extraction_language: str | None = None,
    extraction_confidence: float | None = None,
    extracted_at: datetime | None = None,
) -> None:
    """
    Persist a document status change using a synchronous DB session.

    Args:
        document_id: String UUID of the document to update.
        status: Target DocumentStatus value.
        failure_reason: Optional failure description stored on the model.
        processing_started_at: Timestamp for when processing began.
        processing_completed_at: Timestamp for when processing finished.
        extracted_text: Extracted textual content.
        page_count: Page count of the document.
        extraction_method: Tool used to extract text.
        extraction_language: Detected language of document.
        extraction_confidence: Accuracy confidence of extracted text.
        extracted_at: Timestamp when extraction finished.
    """
    from app.modules.documents.models import Document

    doc_uuid = uuid.UUID(document_id)
    with _sync_get_db_session() as session:
        document = session.get(Document, doc_uuid)
        if document is None:
            logger.warning(
                "Document %s not found when attempting status update to %s.",
                document_id,
                status,
            )
            return

        document.status = status
        if failure_reason is not None:
            document.failure_reason = failure_reason
        if processing_started_at is not None:
            document.processing_started_at = processing_started_at
        if processing_completed_at is not None:
            document.processing_completed_at = processing_completed_at

        # S4-M3 extraction metadata fields
        if extracted_text is not None:
            document.extracted_text = extracted_text
        if page_count is not None:
            document.page_count = page_count
        if extraction_method is not None:
            document.extraction_method = extraction_method
        if extraction_language is not None:
            document.extraction_language = extraction_language
        if extraction_confidence is not None:
            document.extraction_confidence = extraction_confidence
        if extracted_at is not None:
            document.extracted_at = extracted_at

        session.commit()
        logger.info(
            "Document %s status updated to %s.",
            document_id,
            status,
        )


# ---------------------------------------------------------------------------
# Celery Task
# ---------------------------------------------------------------------------


class DocumentProcessingTask(Task):  # type: ignore[misc]
    """
    Custom Celery Task base class for document processing.

    Provides structured failure handling with automatic FAILED status
    persistence when the task is exhausted of retries.
    """

    abstract = True
    name = "app.tasks.document_processing.process_document"

    def on_failure(
        self,
        exc: BaseException,
        task_id: str,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        einfo: Any,
    ) -> None:
        """
        Called by Celery after all retries are exhausted or on unrecoverable error.

        Transitions the document status to FAILED and stores the exception
        message as ``failure_reason``.
        """
        document_id: str = args[0] if args else kwargs.get("document_id", "")
        if document_id:
            _update_document_status(
                document_id,
                DocumentStatus.FAILED,
                failure_reason=str(exc),
            )
            logger.error(
                "Document %s processing permanently FAILED: %s",
                document_id,
                exc,
            )


@celery_app.task(
    bind=True,
    base=DocumentProcessingTask,
    name="app.tasks.document_processing.process_document",
    max_retries=3,
    default_retry_delay=30,
    acks_late=True,
)
def process_document(self: DocumentProcessingTask, document_id: str) -> dict[str, str]:
    """
    Asynchronously process a document through the ingestion pipeline.

    Implements the following lifecycle transitions inside a Celery worker:

        UPLOADED → PROCESSING → TEXT_EXTRACTED → PROCESSED
                             ↘ FAILED  (after max retries exhausted)

    Note:
        The QUEUED transition happens *before* this task is dispatched
        (see :func:`~app.modules.documents.service.DocumentService.ingest_document`).

    Args:
        document_id: String UUID of the document to process.

    Returns:
        A dict with ``document_id`` and ``status`` keys on success.

    Raises:
        Retry: Propagated by Celery on transient failures up to ``max_retries``.
    """
    logger.info(
        "Starting processing for document %s (attempt %s/%s).",
        document_id,
        self.request.retries + 1,
        self.max_retries + 1,
    )

    # ── 1. Transition → PROCESSING ────────────────────────────────────────
    processing_started_at = datetime.now(UTC)
    _update_document_status(
        document_id,
        DocumentStatus.PROCESSING,
        processing_started_at=processing_started_at,
    )

    try:
        # ── 2. Load Document Metadata ──────────────────────────────────────
        from app.modules.documents.models import Document

        doc_uuid = uuid.UUID(document_id)
        with _sync_get_db_session() as session:
            document = session.get(Document, doc_uuid)
            if document is None:
                raise ValueError(f"Document {document_id} not found in database.")

            storage_path: str | None = document.storage_path
            mime_type: str | None = document.mime_type
            logger.info(
                "Loaded document metadata: id=%s, status=%s, storage_path=%s, mime=%s.",
                document_id,
                document.status,
                storage_path,
                mime_type,
            )

        # ── 3. Retrieve File from MinIO and Extract Text ──────────────────
        extracted_text: str | None = None
        if storage_path:
            logger.info(
                "Document %s file located at storage path: %s. Downloading from MinIO...",
                document_id,
                storage_path,
            )
            from app.database.storage.minio import minio_storage
            file_content = minio_storage.download(bucket="documents", object_name=storage_path)

            from app.services.extraction.extractor import ExtractionService
            extractor = ExtractionService.get_extractor_for_mime_type(mime_type or "application/pdf")
            logger.info(
                "Selected extractor %s for mime_type %s",
                extractor.__class__.__name__,
                mime_type,
            )

            # Perform text extraction
            res = extractor.extract(file_content)
            extracted_text = res["extracted_text"]

            # ── 4. Transition → TEXT_EXTRACTED ─────────────────────────────
            _update_document_status(
                document_id,
                DocumentStatus.TEXT_EXTRACTED,
                extracted_text=extracted_text,
                page_count=res["page_count"],
                extraction_method=res["extraction_method"],
                extraction_language=res["extraction_language"],
                extraction_confidence=res["extraction_confidence"],
                extracted_at=datetime.now(UTC),
            )
            logger.info("Successfully extracted text and updated status to TEXT_EXTRACTED")
        else:
            logger.warning(
                "Document %s has no storage_path; skipping file retrieval & text extraction.",
                document_id,
            )

        # ── 5. Transition → CHUNKING ───────────────────────────────────────
        if storage_path and extracted_text:
            _update_document_status(document_id, DocumentStatus.CHUNKING)
            logger.info("Document %s transitioning to CHUNKING.", document_id)

            from app.ai.chunking import TextChunkingService  # noqa: PLC0415
            chunker = TextChunkingService()
            chunks = chunker.chunk(extracted_text)
            logger.info(
                "Document %s split into %d chunks.", document_id, len(chunks)
            )

            # ── 6. Transition → EMBEDDING ──────────────────────────────────
            _update_document_status(document_id, DocumentStatus.EMBEDDING)
            logger.info("Document %s transitioning to EMBEDDING.", document_id)

            from app.ai.embeddings import EmbeddingService  # noqa: PLC0415
            embedder = EmbeddingService()
            embeddings = embedder.embed_chunks(chunks)

            # ── 7. Persist chunks + embeddings ─────────────────────────────
            doc_uuid = uuid.UUID(document_id)
            from app.modules.document_chunks.models import DocumentChunk  # noqa: PLC0415
            from app.modules.document_chunks.repository import DocumentChunkRepository  # noqa: PLC0415

            with _sync_get_db_session() as session:
                repo = DocumentChunkRepository(session)
                # Remove any prior chunks if re-processing
                deleted = repo.delete_by_document_id(doc_uuid)
                if deleted:
                    logger.info(
                        "Removed %d stale chunks for document %s.",
                        deleted,
                        document_id,
                    )

                chunk_rows = [
                    DocumentChunk(
                        document_id=doc_uuid,
                        chunk_index=chunk.chunk_index,
                        text=chunk.text,
                        char_start=chunk.char_start,
                        char_end=chunk.char_end,
                        token_estimate=chunk.token_estimate,
                        embedding=embeddings[i],
                    )
                    for i, chunk in enumerate(chunks)
                ]
                repo.bulk_create(chunk_rows)
                session.commit()

            logger.info(
                "Document %s: %d chunks with embeddings persisted.",
                document_id,
                len(chunk_rows),
            )

        # ── 8. Transition → PROCESSED ──────────────────────────────────────
        processing_completed_at = datetime.now(UTC)
        _update_document_status(
            document_id,
            DocumentStatus.PROCESSED,
            processing_completed_at=processing_completed_at,
        )

        logger.info(
            "Document %s successfully PROCESSED in %.3fs.",
            document_id,
            (processing_completed_at - processing_started_at).total_seconds(),
        )

        return {"document_id": document_id, "status": DocumentStatus.PROCESSED}

    except Exception as exc:  # noqa: BLE001  (broad catch is intentional here)
        logger.warning(
            "Document %s processing attempt %s failed: %s. Retrying with backoff.",
            document_id,
            self.request.retries + 1,
            exc,
        )
        # Exponential backoff: 30s, 90s, 270s
        backoff_delay = 30 * (3 ** self.request.retries)
        try:
            raise self.retry(exc=exc, countdown=backoff_delay)
        except MaxRetriesExceededError:
            # on_failure will handle the FAILED transition
            raise
