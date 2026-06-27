"""
Image text extractor using OCR (PaddleOCR with Tesseract fallback).
"""

import io
import logging
from PIL import Image
import pytesseract

from app.services.extraction.extractor import BaseExtractor, ExtractionResult

logger = logging.getLogger(__name__)


class ImageExtractor(BaseExtractor):
    """
    Extractor for image files (PNG, JPEG) using OCR.

    Prioritises PaddleOCR, falling back to Tesseract OCR (pytesseract) if unavailable.
    """

    def __init__(self) -> None:
        self.paddle_ocr_client = None
        self._initialized_paddle = False

    def _init_paddle_ocr(self) -> None:
        """
        Attempt to initialize PaddleOCR. If it is not installed or fails,
        leaves client as None.
        """
        if self._initialized_paddle:
            return

        self._initialized_paddle = True
        try:
            from paddleocr import PaddleOCR
            # Initialize with English language support by default
            self.paddle_ocr_client = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
            logger.info("PaddleOCR successfully initialized.")
        except (ImportError, Exception) as e:
            logger.warning("PaddleOCR initialization failed, will fallback to Tesseract: %s", e)
            self.paddle_ocr_client = None

    def extract(self, file_content: bytes) -> ExtractionResult:
        self._init_paddle_ocr()

        # Open image using Pillow
        try:
            image = Image.open(io.BytesIO(file_content))
            image.load()  # Ensure image data is loaded
        except Exception as e:
            logger.error("Failed to parse image with Pillow: %s", e)
            raise ValueError(f"Invalid image file: {e}") from e

        # 1. Attempt PaddleOCR
        if self.paddle_ocr_client is not None:
            try:
                # PaddleOCR expects a file path, numpy array, or PIL image (or we pass bytes)
                # For safety, pass the image object or file content
                result = self.paddle_ocr_client.ocr(file_content, cls=True)
                
                texts = []
                confidences = []
                
                if result and result[0]:
                    for line in result[0]:
                        # line is [[box], (text, confidence)]
                        text_val = line[1][0]
                        conf_val = float(line[1][1])
                        texts.append(text_val)
                        confidences.append(conf_val)
                
                full_text = " ".join(texts).strip()
                avg_conf = sum(confidences) / len(confidences) if confidences else 1.0

                return {
                    "extracted_text": full_text,
                    "page_count": 1,
                    "extraction_method": "paddle_ocr",
                    "extraction_language": "en",
                    "extraction_confidence": avg_conf,
                }
            except Exception as e:
                logger.warning("PaddleOCR extraction failed, falling back to Tesseract: %s", e)

        # 2. Fallback to Tesseract OCR
        try:
            # Extract raw string
            text = pytesseract.image_to_string(image).strip()

            # Attempt to extract confidence
            try:
                data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
                conf_list = [
                    float(c)
                    for c in data.get("conf", [])
                    if c is not None and str(c).strip() != "" and float(c) >= 0
                ]
                if conf_list:
                    # Tesseract reports confidence as 0-100; scale to 0.0-1.0
                    avg_conf = (sum(conf_list) / len(conf_list)) / 100.0
                else:
                    avg_conf = 0.85
            except Exception as e:
                logger.debug("Failed to calculate Tesseract confidence details: %s", e)
                avg_conf = 0.85

            return {
                "extracted_text": text,
                "page_count": 1,
                "extraction_method": "tesseract_ocr",
                "extraction_language": "en",
                "extraction_confidence": avg_conf,
            }
        except Exception as e:
            logger.error("Tesseract OCR extraction failed: %s", e)
            # If Tesseract is not installed on the system, return empty instead of failing completely,
            # allowing local environment testing to proceed.
            return {
                "extracted_text": "",
                "page_count": 1,
                "extraction_method": "failed_ocr_fallback",
                "extraction_language": "en",
                "extraction_confidence": 0.0,
            }
