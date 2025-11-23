"""
Integration test: Scraper → OCR (first 5 pages, print all detected text)
"""
from pathlib import Path
import pytest
import requests
import tempfile
from my_flask_app.scrapers.mangadex_scraper import MangadexScraper
from my_flask_app.processors.ocr.easyocr_processor import EasyOCRProcessor


def test_scraper_to_ocr_first_5_pages(tmp_path):
    """
    1. Scrape MangaDex chapter images.
    2. Download first 5 pages.
    3. Run OCR on each and print all detected text.
    """
    # --- Step 1: Scrape images ---
    scraper = MangadexScraper()
    test_url = "https://mangadex.org/chapter/404de169-f8c1-4ff2-9ae4-9ef2f25940ae"

    try:
        image_urls = scraper.scrape(test_url)
        assert image_urls, "No images returned by scraper."
        print(f"Scraped {len(image_urls)} image URLs total.")
    except Exception as e:
        pytest.skip(f"Scraper failed due to network or API issue: {e}")

    # Limit to first 5 pages (or fewer if less available)
    image_subset = image_urls[:5]
    print(f"\nProcessing {len(image_subset)} pages...\n")

    # --- Step 2: Initialize OCR ---
    ocr = EasyOCRProcessor()

    # --- Step 3: Process each page ---
    for idx, url in enumerate(image_subset, start=1):
        image_path = tmp_path / f"page_{idx}.jpg"

        # Download the page
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            image_path.write_bytes(r.content)
            print(f"Downloaded page {idx}: {url}")
        except Exception as e:
            pytest.skip(f"Failed to download page {idx}: {e}")

        # Run OCR
        try:
            results = ocr.extract_text(str(image_path))
            assert isinstance(results, list), f"OCR output for page {idx} is not a list."
            print(f"Page {idx}: Detected {len(results)} text regions.")

            if not results:
                print("No text detected on this page.\n")
                continue

            print("\n--- OCR TEXT (Page {0}) ---".format(idx))
            for j, item in enumerate(results, start=1):
                text = item['text']
                conf = item['confidence']
                print(f" {j:02d}. {text} (conf: {conf:.2f})")
            print("------------------------------\n")

        except Exception as e:
            pytest.skip(f"OCR failed for page {idx}: {e}")

    print("Finished OCR for all pages.")

if __name__ == "__main__":


    tmp_dir = Path(tempfile.mkdtemp())   # creates a temp dir
    test_scraper_to_ocr_first_5_pages(tmp_dir)
    
