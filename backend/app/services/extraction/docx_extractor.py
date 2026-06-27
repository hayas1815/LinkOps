"""
DOCX document text extractor.
"""

from io import BytesIO
import docx

from app.services.extraction.extractor import BaseExtractor, ExtractionResult


class DOCXExtractor(BaseExtractor):
    """
    Extractor for Microsoft Word documents (.docx) using python-docx.
    """

    def extract(self, file_content: bytes) -> ExtractionResult:
        # Load the Word document from binary data
        doc = docx.Document(BytesIO(file_content))

        # Extract text paragraph by paragraph to preserve logical ordering
        text_parts = []
        for paragraph in doc.paragraphs:
            val = paragraph.text.strip()
            if val:
                text_parts.append(val)

        full_text = "\n\n".join(text_parts)

        return {
            "extracted_text": full_text.strip(),
            "page_count": 1,  # DOCX files do not have a deterministic pagination without rendering
            "extraction_method": "docx_paragraphs",
            "extraction_language": "en",  # Default fallback language
            "extraction_confidence": 1.0,
        }
