"""
PDF document text extractor with native text extraction and OCR fallback.
"""

import logging
import fitz  # PyMuPDF

from app.services.extraction.extractor import BaseExtractor, ExtractionResult
from app.services.extraction.image_extractor import ImageExtractor

logger = logging.getLogger(__name__)


class PDFExtractor(BaseExtractor):
    """
    Extractor for PDF documents using PyMuPDF (fitz).

    Attempts native text extraction first. If no text is found, falls back
    to rendering pages as images and running OCR.
    """

    def extract(self, file_content: bytes) -> ExtractionResult:
        # Open PDF from memory stream
        try:
            doc = fitz.open(stream=file_content, filetype="pdf")
        except Exception as e:
            logger.error("Failed to parse PDF with PyMuPDF: %s", e)
            raise ValueError(f"Invalid PDF file: {e}") from e

        page_count = len(doc)
        native_text_parts = []

        # 1. Native text extraction
        for page in doc:
            text = page.get_text().strip()
            if text:
                native_text_parts.append(text)

        full_native_text = "\n\n".join(native_text_parts).strip()

        # If we successfully extracted text natively, return it
        if full_native_text:
            return {
                "extracted_text": full_native_text,
                "page_count": page_count,
                "extraction_method": "native_pdf",
                "extraction_language": "en",
                "extraction_confidence": 1.0,
            }

        # 2. OCR Fallback if no text extracted natively
        logger.info("No native text found in PDF. Falling back to OCR page-by-page.")
        
        image_extractor = ImageExtractor()
        ocr_text_parts = []
        confidences = []

        for i, page in enumerate(doc):
            logger.debug("Running OCR on PDF page %s/%s", i + 1, page_count)
            try:
                # Render page to a pixmap (image)
                pix = page.get_pixmap(dpi=150)
                png_bytes = pix.tobytes("png")

                # Extract text from page image
                result = image_extractor.extract(png_bytes)
                if result["extracted_text"].strip():
                    ocr_text_parts.append(result["extracted_text"])
                
                confidences.append(result["extraction_confidence"])
            except Exception as e:
                logger.error("Failed to run OCR on PDF page %s: %s", i + 1, e)

        full_ocr_text = "\n\n".join(ocr_text_parts).strip()
        avg_conf = sum(confidences) / len(confidences) if confidences else 0.85

        return {
            "extracted_text": full_ocr_text,
            "page_count": page_count,
            "extraction_method": "ocr_pdf",
            "extraction_language": "en",
            "extraction_confidence": avg_conf,
        }
