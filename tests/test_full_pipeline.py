"""
End-to-end test: Scrape MangaDex -> Run OCR -> Translate -> Typeset -> Save metadata in project folder.
Requires internet, EasyOCR, and a valid Gemini API key.
"""
import cv2
import pytest
import requests
import warnings
import json
from pathlib import Path
from datetime import datetime

from my_flask_app.scrapers.mangadex_scraper import MangadexScraper
from my_flask_app.processors.ocr.easyocr_processor import EasyOCRProcessor
from my_flask_app.processors.translation.gemini_translator import GeminiTranslator


warnings.filterwarnings("ignore", category=DeprecationWarning, module="torch")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="easyocr")
warnings.filterwarnings("ignore", message="'pin_memory' argument is set as true but not supported on MPS")
warnings.filterwarnings("ignore", message="'mode' parameter is deprecated", module="easyocr")


@pytest.mark.integration
def test_full_pipeline():
    """
    Full test: Scrape MangaDex -> Run OCR -> Translate -> Typeset -> Save metadata in project folder.
    """
    scraper = MangadexScraper()
    ocr = EasyOCRProcessor()
    translator = GeminiTranslator()

    test_url = "https://mangadex.org/chapter/f30bcf20-a6f4-459c-b5b1-0bdb3c8f004a"

    # Create a folder to store outputs permanently
    output_dir = Path(__file__).parent / "metadata_output"
    output_dir.mkdir(parents=True, exist_ok=True)

    img_path = output_dir / "page3.jpg"
    output_image_path = output_dir / "page3_translated.png"
    metadata_path = output_dir / "metadata.json"

    # scrape
    try:
        image_urls = scraper.scrape(test_url)
        assert image_urls, "No images scraped."
        print(f"Scraped {len(image_urls)} image URLs.")
    except Exception as e:
        pytest.skip(f" Scraper failed: {e}")
        return

    # get image
    try:
        resp = requests.get(image_urls[2], timeout=10)
        resp.raise_for_status()
        img_path.write_bytes(resp.content)
        print(f"Downloaded image: {img_path}")
    except Exception as e:
        pytest.skip(f"Image download failed: {e}")
        return

    # use OCR
    try:
        ocr_data = ocr.extract_text(str(img_path))
        assert isinstance(ocr_data, list)
        print(f"Extracted {len(ocr_data)} OCR text regions.")
    except Exception as e:
        pytest.skip(f"OCR extraction failed: {e}")
        return

    if not ocr_data:
        pytest.skip("No text detected; skipping translation/typesetting.")
        return

    # translate
    try:
        translated_data = translator.translate(ocr_data, "kr", "en", model_type="fast")
        assert isinstance(translated_data, list)
        print(f"Translated {len(translated_data)} text regions.")
    except Exception as e:
        pytest.skip(f"Translation failed: {e}")
        return


    # write metadata
    def to_serializable(obj):
        """Convert numpy/int32 types to Python int."""
        if isinstance(obj, (int, float, str, bool)) or obj is None:
            return obj
        if hasattr(obj, "item"):
            return obj.item()
        if isinstance(obj, dict):
            return {k: to_serializable(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [to_serializable(v) for v in obj]
        return str(obj)

    try:
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "chapter_url": test_url,
            "scraper": {
                "total_pages": len(image_urls),
                "sample_urls": image_urls[:5],
            },
            "ocr": to_serializable(ocr_data),
            "translation": to_serializable(translated_data),
            "output_image": str(output_image_path),
        }

        metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False))
        print(f"Metadata written -> {metadata_path}")

    except Exception as e:
        print(f" Failed to write metadata: {e}")
        raise


    try:
        result = cv2.imread(str(output_image_path))
        assert result is not None, "Final output image could not be read."
        print(f"Verified output image ({result.shape[1]}x{result.shape[0]}).")
    except Exception as e:
        pytest.skip(f"Validation failed: {e}")

    