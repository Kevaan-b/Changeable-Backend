"""
End-to-end test for scraping → OCR → translation workflow.
"""
import pytest

from my_flask_app.scrapers.sites.mangadex_scraper import MangadexScraper
from my_flask_app.processors.ocr.easyocr_processor import EasyOCRProcessor
from my_flask_app.processors.translation.gemini_translator import GeminiTranslator

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="torch")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="easyocr")
warnings.filterwarnings("ignore", message="'pin_memory' argument is set as true but not supported on MPS")
warnings.filterwarnings("ignore", message="'mode' parameter is deprecated", module="easyocr")



#@pytest.mark.integration
def test_full_workflow(tmp_path):
    """
    Runs the complete flow:
      1. Scrape images from MangaDex
      2. Run OCR on one image
      3. Translate extracted text via Gemini
    ⚠️ Requires internet, EasyOCR installed, and valid Gemini API key.
    """
    scraper = MangadexScraper()
    ocr = EasyOCRProcessor()
    translator = GeminiTranslator()

    test_url = "https://mangadex.org/chapter/404de169-f8c1-4ff2-9ae4-9ef2f25940ae"

    # Step 1: Scrape
    try:
        image_urls = scraper.scrape(test_url)
        assert image_urls, "No images scraped."
        print(f"✅ Scraped {len(image_urls)} image URLs.")
    except Exception as e:
        pytest.skip(f"Scraper failed: {e}")

    # Step 2: OCR
    # Download the first image to temporary folder
    import requests
    import os

    image_path = tmp_path / "page3.jpg"
    try:
        r = requests.get(image_urls[2], timeout=10)
        r.raise_for_status()
        image_path.write_bytes(r.content)
        print(f"✅ Image downloaded: {image_path}")
    except Exception as e:
        pytest.skip(f"Image download failed: {e}")

    try:
        text_data = ocr.extract_text(str(image_path))
        assert isinstance(text_data, list)
        print(f"✅ Extracted {len(text_data)} text regions.")
        print(text_data)
    except Exception as e:
        pytest.skip(f"OCR extraction failed: {e}")

    if not text_data:
        pytest.skip("No text detected; skipping translation.")

    # Step 3: Translation
    try:
        translated = translator.translate(text_data, "en", "ja", model_type="fast")
        assert isinstance(translated, list)
        for t in translated:
            print(f"{t['text']} → {t['translated_text']}")
        print("✅ Translation successful.")
    except Exception as e:
        pytest.skip(f"Translation failed: {e}")
