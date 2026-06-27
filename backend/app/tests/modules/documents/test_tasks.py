"""
Unit tests for the document processing Celery task (S4-M4).

Tests cover:
- Status transition: PROCESSING on task start
- Status transition: TEXT_EXTRACTED on extraction completion
- Status transition: CHUNKING on chunking start
- Status transition: EMBEDDING on embedding start
- Status transition: PROCESSED on successful completion
- Status transition: FAILED after max retries
- Retry scheduling with exponential backoff
- Handling of missing document (graceful no-op)
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest

# Force the submodule to be loaded before any @patch decorators run,
# so that 'app.tasks.document_processing' is a resolvable attribute path.
import app.tasks.document_processing  # noqa: F401

from app.modules.documents.enums import DocumentStatus


# ---------------------------------------------------------------------------
# Constants for patch paths
# ---------------------------------------------------------------------------

PATCH_SYNC_SESSION = "app.tasks.document_processing._sync_get_db_session"
PATCH_UPDATE_STATUS = "app.tasks.document_processing._update_document_status"
PATCH_MINIO = "app.database.storage.minio.minio_storage"
PATCH_EXTRACTOR = "app.services.extraction.extractor.ExtractionService"
PATCH_CHUNKER = "app.ai.chunking.TextChunkingService"
PATCH_EMBEDDER = "app.ai.embeddings.EmbeddingService"
PATCH_CHUNK_REPO = "app.modules.document_chunks.repository.DocumentChunkRepository"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_document(doc_id: uuid.UUID, status: DocumentStatus = DocumentStatus.QUEUED):
    """Return a minimal mock Document object."""
    doc = MagicMock()
    doc.id = doc_id
    doc.status = status
    doc.storage_path = "2024/01/test-uuid_test.pdf"
    doc.mime_type = "application/pdf"
    doc.failure_reason = None
    doc.processing_started_at = None
    doc.processing_completed_at = None
    return doc


def _make_ctx_session(mock_doc):
    """Return a MagicMock session usable as a synchronous context manager."""
    mock_session = MagicMock()
    mock_session.__enter__ = MagicMock(return_value=mock_session)
    mock_session.__exit__ = MagicMock(return_value=False)
    mock_session.get = MagicMock(return_value=mock_doc)
    return mock_session


# ---------------------------------------------------------------------------
# Tests: _update_document_status
# ---------------------------------------------------------------------------


class TestUpdateDocumentStatus:
    """Tests for the synchronous _update_document_status helper."""

    @patch(PATCH_SYNC_SESSION)
    def test_updates_status_to_processing(self, mock_get_session):
        """_update_document_status sets status and commits."""
        from app.tasks.document_processing import _update_document_status

        doc_id = uuid.uuid4()
        mock_doc = _make_document(doc_id)
        mock_get_session.return_value = _make_ctx_session(mock_doc)

        started_at = datetime.now(UTC)
        _update_document_status(
            str(doc_id),
            DocumentStatus.PROCESSING,
            processing_started_at=started_at,
        )

        assert mock_doc.status == DocumentStatus.PROCESSING
        assert mock_doc.processing_started_at == started_at
        mock_get_session.return_value.commit.assert_called_once()

    @patch(PATCH_SYNC_SESSION)
    def test_updates_status_to_failed_with_reason(self, mock_get_session):
        """_update_document_status stores failure_reason when provided."""
        from app.tasks.document_processing import _update_document_status

        doc_id = uuid.uuid4()
        mock_doc = _make_document(doc_id)
        mock_get_session.return_value = _make_ctx_session(mock_doc)

        _update_document_status(
            str(doc_id),
            DocumentStatus.FAILED,
            failure_reason="Connection error",
        )

        assert mock_doc.status == DocumentStatus.FAILED
        assert mock_doc.failure_reason == "Connection error"
        mock_get_session.return_value.commit.assert_called_once()

    @patch(PATCH_SYNC_SESSION)
    def test_noop_when_document_not_found(self, mock_get_session):
        """_update_document_status does not commit if document is missing."""
        from app.tasks.document_processing import _update_document_status

        doc_id = uuid.uuid4()
        mock_get_session.return_value = _make_ctx_session(None)

        # Should not raise
        _update_document_status(str(doc_id), DocumentStatus.PROCESSING)

        mock_get_session.return_value.commit.assert_not_called()


# ---------------------------------------------------------------------------
# Tests: process_document task
# ---------------------------------------------------------------------------


class TestProcessDocumentTask:
    """Tests for the process_document Celery task."""

    def _apply_task(self, doc_id: str):
        """Execute the task synchronously using apply() (no broker needed)."""
        from app.tasks.document_processing import process_document

        return process_document.apply(args=[doc_id])

    @patch("app.modules.document_chunks.repository.DocumentChunkRepository")
    @patch("app.modules.document_chunks.models.DocumentChunk")
    @patch("app.ai.embeddings.EmbeddingService")
    @patch("app.ai.chunking.TextChunkingService")
    @patch(PATCH_MINIO)
    @patch(PATCH_EXTRACTOR)
    @patch(PATCH_SYNC_SESSION)
    @patch(PATCH_UPDATE_STATUS)
    def test_successful_processing_transitions(
        self,
        mock_update_status,
        mock_get_session,
        mock_extractor_service,
        mock_minio,
        mock_chunker_cls,
        mock_embedder_cls,
        mock_chunk_model,
        mock_repo_cls,
    ):
        """
        A successful task run calls _update_document_status five times:
          1. PROCESSING (with processing_started_at)
          2. TEXT_EXTRACTED (with extracted text metadata)
          3. CHUNKING
          4. EMBEDDING
          5. PROCESSED  (with processing_completed_at)
        """
        from unittest.mock import MagicMock
        doc_id = uuid.uuid4()
        mock_doc = _make_document(doc_id)
        mock_get_session.return_value = _make_ctx_session(mock_doc)

        mock_minio.download.return_value = b"mock file content"
        mock_extractor = MagicMock()
        mock_extractor.extract.return_value = {
            "extracted_text": "Extracted text content",
            "page_count": 5,
            "extraction_method": "test_mock",
            "extraction_language": "en",
            "extraction_confidence": 0.95,
        }
        mock_extractor_service.get_extractor_for_mime_type.return_value = mock_extractor

        # Chunker returns 2 fake chunks
        from app.ai.chunking import TextChunk
        fake_chunks = [
            TextChunk(chunk_index=0, text="chunk zero", char_start=0, char_end=10),
            TextChunk(chunk_index=1, text="chunk one", char_start=12, char_end=21),
        ]
        mock_chunker_instance = MagicMock()
        mock_chunker_instance.chunk.return_value = fake_chunks
        mock_chunker_cls.return_value = mock_chunker_instance

        # Embedder returns 2 fake 384-dim vectors
        mock_embedder_instance = MagicMock()
        mock_embedder_instance.embed_chunks.return_value = [
            [0.0] * 384,
            [0.1] * 384,
        ]
        mock_embedder_cls.return_value = mock_embedder_instance

        # Chunk repo mock
        mock_repo_instance = MagicMock()
        mock_repo_instance.delete_by_document_id.return_value = 0
        mock_repo_cls.return_value = mock_repo_instance

        result = self._apply_task(str(doc_id))

        assert result.successful()
        result_val = result.get()
        assert result_val["document_id"] == str(doc_id)
        assert result_val["status"] == DocumentStatus.PROCESSED

        calls = mock_update_status.call_args_list
        assert len(calls) == 5, f"Expected 5 status calls, got {len(calls)}: {calls}"

        # 1. PROCESSING
        assert calls[0][0][1] == DocumentStatus.PROCESSING
        assert calls[0][1].get("processing_started_at") is not None

        # 2. TEXT_EXTRACTED
        assert calls[1][0][1] == DocumentStatus.TEXT_EXTRACTED
        assert calls[1][1].get("extracted_text") == "Extracted text content"
        assert calls[1][1].get("page_count") == 5

        # 3. CHUNKING
        assert calls[2][0][1] == DocumentStatus.CHUNKING

        # 4. EMBEDDING
        assert calls[3][0][1] == DocumentStatus.EMBEDDING

        # 5. PROCESSED
        assert calls[4][0][1] == DocumentStatus.PROCESSED
        assert calls[4][1].get("processing_completed_at") is not None

    @patch(PATCH_MINIO)
    @patch(PATCH_EXTRACTOR)
    @patch(PATCH_SYNC_SESSION)
    @patch(PATCH_UPDATE_STATUS)
    def test_document_not_found_triggers_failure(
        self, mock_update_status, mock_get_session, mock_extractor_service, mock_minio
    ):
        """
        When document is missing from DB, the task exhausts retries and fails.
        """
        doc_id = uuid.uuid4()
        mock_get_session.return_value = _make_ctx_session(None)

        result = self._apply_task(str(doc_id))

        assert result.failed()

    @patch("app.modules.document_chunks.repository.DocumentChunkRepository")
    @patch("app.modules.document_chunks.models.DocumentChunk")
    @patch("app.ai.embeddings.EmbeddingService")
    @patch("app.ai.chunking.TextChunkingService")
    @patch(PATCH_MINIO)
    @patch(PATCH_EXTRACTOR)
    @patch(PATCH_SYNC_SESSION)
    @patch(PATCH_UPDATE_STATUS)
    def test_return_dict_has_correct_keys(
        self,
        mock_update_status,
        mock_get_session,
        mock_extractor_service,
        mock_minio,
        mock_chunker_cls,
        mock_embedder_cls,
        mock_chunk_model,
        mock_repo_cls,
    ):
        """Successful task returns dict with document_id and status keys."""
        from unittest.mock import MagicMock
        from app.ai.chunking import TextChunk

        doc_id = uuid.uuid4()
        mock_doc = _make_document(doc_id)
        mock_get_session.return_value = _make_ctx_session(mock_doc)

        mock_minio.download.return_value = b"mock file content"
        mock_extractor = MagicMock()
        mock_extractor.extract.return_value = {
            "extracted_text": "Extracted text content",
            "page_count": 1,
            "extraction_method": "test_mock",
            "extraction_language": "en",
            "extraction_confidence": 0.95,
        }
        mock_extractor_service.get_extractor_for_mime_type.return_value = mock_extractor

        fake_chunks = [TextChunk(chunk_index=0, text="only chunk", char_start=0, char_end=10)]
        mock_chunker_cls.return_value.chunk.return_value = fake_chunks
        mock_embedder_cls.return_value.embed_chunks.return_value = [[0.0] * 384]
        mock_repo_cls.return_value.delete_by_document_id.return_value = 0

        result = self._apply_task(str(doc_id))
        val = result.get()

        assert "document_id" in val
        assert "status" in val
        assert val["status"] == "PROCESSED"


# ---------------------------------------------------------------------------
# Tests: on_failure hook
# ---------------------------------------------------------------------------


class TestDocumentProcessingTaskOnFailure:
    """Tests for the DocumentProcessingTask.on_failure lifecycle hook."""

    @patch(PATCH_UPDATE_STATUS)
    def test_on_failure_marks_document_failed(self, mock_update_status):
        """on_failure must call _update_document_status with FAILED status."""
        from app.tasks.document_processing import DocumentProcessingTask

        task_instance = DocumentProcessingTask()
        doc_id = str(uuid.uuid4())

        task_instance.on_failure(
            exc=RuntimeError("disk full"),
            task_id="fake-task-id",
            args=(doc_id,),
            kwargs={},
            einfo=None,
        )

        mock_update_status.assert_called_once_with(
            doc_id,
            DocumentStatus.FAILED,
            failure_reason="disk full",
        )

    @patch(PATCH_UPDATE_STATUS)
    def test_on_failure_uses_kwargs_when_no_args(self, mock_update_status):
        """on_failure extracts document_id from kwargs if args is empty."""
        from app.tasks.document_processing import DocumentProcessingTask

        task_instance = DocumentProcessingTask()
        doc_id = str(uuid.uuid4())

        task_instance.on_failure(
            exc=ValueError("bad data"),
            task_id="fake-task-id",
            args=(),
            kwargs={"document_id": doc_id},
            einfo=None,
        )

        mock_update_status.assert_called_once_with(
            doc_id,
            DocumentStatus.FAILED,
            failure_reason="bad data",
        )
