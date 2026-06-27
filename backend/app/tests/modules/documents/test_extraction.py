"""
Unit tests for the document text extraction layer (S4-M3).
"""

from unittest.mock import MagicMock, patch
import pytest

from app.services.extraction.extractor import ExtractionService, PlainTextExtractor
from app.services.extraction.pdf_extractor import PDFExtractor
from app.services.extraction.docx_extractor import DOCXExtractor
from app.services.extraction.image_extractor import ImageExtractor


def test_extraction_service_selection():
    """ExtractionService should select correct extractor by MIME type."""
    # PDF
    pdf_ext = ExtractionService.get_extractor_for_mime_type("application/pdf")
    assert isinstance(pdf_ext, PDFExtractor)

    # DOCX
    docx_ext = ExtractionService.get_extractor_for_mime_type(
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    assert isinstance(docx_ext, DOCXExtractor)

    # Images
    png_ext = ExtractionService.get_extractor_for_mime_type("image/png")
    assert isinstance(png_ext, ImageExtractor)
    jpg_ext = ExtractionService.get_extractor_for_mime_type("image/jpeg")
    assert isinstance(jpg_ext, ImageExtractor)

    # Plain text
    txt_ext = ExtractionService.get_extractor_for_mime_type("text/plain")
    assert isinstance(txt_ext, PlainTextExtractor)

    # Unsupported
    with pytest.raises(ValueError, match="No extractor registered"):
        ExtractionService.get_extractor_for_mime_type("application/zip")


def test_plain_text_extractor():
    """PlainTextExtractor should decode and return clean text."""
    extractor = PlainTextExtractor()
    content = b"Hello, this is a plain text file."
    res = extractor.extract(content)
    assert res["extracted_text"] == "Hello, this is a plain text file."
    assert res["page_count"] == 1
    assert res["extraction_method"] == "plain_text"
    assert res["extraction_confidence"] == 1.0


@patch("app.services.extraction.pdf_extractor.fitz.open")
def test_pdf_extractor_native_success(mock_fitz_open):
    """PDFExtractor should extract text natively if present."""
    mock_doc = MagicMock()
    mock_page_1 = MagicMock()
    mock_page_1.get_text.return_value = "Page 1 content"
    mock_page_2 = MagicMock()
    mock_page_2.get_text.return_value = "  Page 2 content  "
    mock_doc.__iter__.return_value = [mock_page_1, mock_page_2]
    mock_doc.__len__.return_value = 2
    mock_fitz_open.return_value = mock_doc

    extractor = PDFExtractor()
    res = extractor.extract(b"fake pdf content")

    assert res["extracted_text"] == "Page 1 content\n\nPage 2 content"
    assert res["page_count"] == 2
    assert res["extraction_method"] == "native_pdf"
    assert res["extraction_confidence"] == 1.0


@patch("app.services.extraction.pdf_extractor.ImageExtractor")
@patch("app.services.extraction.pdf_extractor.fitz.open")
def test_pdf_extractor_ocr_fallback(mock_fitz_open, mock_image_extractor_class):
    """PDFExtractor should fallback to OCR if no native text is found."""
    # Native text is empty/whitespace
    mock_doc = MagicMock()
    mock_page = MagicMock()
    mock_page.get_text.return_value = "   "
    mock_pixmap = MagicMock()
    mock_pixmap.tobytes.return_value = b"fake-png-bytes"
    mock_page.get_pixmap.return_value = mock_pixmap
    mock_doc.__iter__.return_value = [mock_page]
    mock_doc.__len__.return_value = 1
    mock_fitz_open.return_value = mock_doc

    # Mock the ImageExtractor results
    mock_img_ext = mock_image_extractor_class.return_value
    mock_img_ext.extract.return_value = {
        "extracted_text": "Extracted OCR Text",
        "page_count": 1,
        "extraction_method": "tesseract_ocr",
        "extraction_language": "en",
        "extraction_confidence": 0.9,
    }

    extractor = PDFExtractor()
    res = extractor.extract(b"fake pdf content")

    assert res["extracted_text"] == "Extracted OCR Text"
    assert res["page_count"] == 1
    assert res["extraction_method"] == "ocr_pdf"
    assert res["extraction_confidence"] == 0.9


@patch("app.services.extraction.docx_extractor.docx.Document")
def test_docx_extractor(mock_docx_doc):
    """DOCXExtractor should extract paragraphs preserving order."""
    mock_doc_instance = MagicMock()
    mock_p1 = MagicMock()
    mock_p1.text = "First paragraph."
    mock_p2 = MagicMock()
    mock_p2.text = "   "  # Empty paragraph
    mock_p3 = MagicMock()
    mock_p3.text = "Second paragraph."
    mock_doc_instance.paragraphs = [mock_p1, mock_p2, mock_p3]
    mock_docx_doc.return_value = mock_doc_instance

    extractor = DOCXExtractor()
    res = extractor.extract(b"fake docx content")

    assert res["extracted_text"] == "First paragraph.\n\nSecond paragraph."
    assert res["page_count"] == 1
    assert res["extraction_method"] == "docx_paragraphs"
    assert res["extraction_confidence"] == 1.0


@patch("app.services.extraction.image_extractor.pytesseract.image_to_string")
@patch("app.services.extraction.image_extractor.pytesseract.image_to_data")
@patch("app.services.extraction.image_extractor.Image.open")
def test_image_extractor_tesseract_fallback(mock_image_open, mock_to_data, mock_to_string):
    """ImageExtractor should use pytesseract as fallback if PaddleOCR is unavailable."""
    # Ensure PaddleOCR is disabled/not found
    extractor = ImageExtractor()
    extractor.paddle_ocr_client = None
    extractor._initialized_paddle = True

    mock_image_instance = MagicMock()
    mock_image_open.return_value = mock_image_instance
    mock_to_string.return_value = "Image Text content"
    mock_to_data.return_value = {
        "conf": [90, 80, -1, 95]
    }

    res = extractor.extract(b"fake image content")

    assert res["extracted_text"] == "Image Text content"
    assert res["page_count"] == 1
    assert res["extraction_method"] == "tesseract_ocr"
    # avg of [90, 80, 95] / 100 = 0.8833...
    assert 0.88 <= res["extraction_confidence"] <= 0.89
