"""
Base extractor interfaces and ExtractionService dispatcher.
"""

from abc import ABC, abstractmethod
from typing import TypedDict, Type


class ExtractionResult(TypedDict):
    """
    Structured result returned by all document text extractors.
    """
    extracted_text: str
    page_count: int
    extraction_method: str
    extraction_language: str
    extraction_confidence: float


class BaseExtractor(ABC):
    """
    Abstract base class for all file-specific text extractors.
    """

    @abstractmethod
    def extract(self, file_content: bytes) -> ExtractionResult:
        """
        Extract textual content and metadata from raw file bytes.

        Args:
            file_content: The raw binary content of the file.

        Returns:
            An ExtractionResult dictionary.
        """
        pass


class PlainTextExtractor(BaseExtractor):
    """
    Extractor for plain text files (text/plain).
    """

    def extract(self, file_content: bytes) -> ExtractionResult:
        # Decode text content with fallback encoding detection
        try:
            text = file_content.decode("utf-8")
        except UnicodeDecodeError:
            text = file_content.decode("latin-1", errors="replace")

        return {
            "extracted_text": text.strip(),
            "page_count": 1,
            "extraction_method": "plain_text",
            "extraction_language": "en",  # Default fallback language
            "extraction_confidence": 1.0,
        }


class ExtractionService:
    """
    Service registry and dispatcher for document text extraction.
    """

    _registry: dict[str, Type[BaseExtractor]] = {}

    @classmethod
    def register(cls, mime_type: str, extractor_class: Type[BaseExtractor]) -> None:
        """
        Register an extractor class for a specific MIME type.
        """
        cls._registry[mime_type.lower()] = extractor_class

    @classmethod
    def get_extractor_for_mime_type(cls, mime_type: str) -> BaseExtractor:
        """
        Return an instance of the appropriate extractor for the given MIME type.

        Raises:
            ValueError: If no extractor is registered for the MIME type.
        """
        # Lazy imports to avoid circular dependency issues
        from app.services.extraction.pdf_extractor import PDFExtractor
        from app.services.extraction.docx_extractor import DOCXExtractor
        from app.services.extraction.image_extractor import ImageExtractor

        # Register standard extractors on demand if registry is empty
        if not cls._registry:
            cls.register("application/pdf", PDFExtractor)
            cls.register(
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                DOCXExtractor,
            )
            cls.register("image/png", ImageExtractor)
            cls.register("image/jpeg", ImageExtractor)
            cls.register("image/jpg", ImageExtractor)
            cls.register("text/plain", PlainTextExtractor)

        mime_lower = mime_type.lower()
        extractor_class = cls._registry.get(mime_lower)
        if not extractor_class:
            raise ValueError(f"No extractor registered for MIME type: {mime_type}")

        return extractor_class()
