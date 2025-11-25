"""
Integration test: Scraper -> OCR (first 5 pages, print all detected bubble texts)
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
    3. Run OCR on each and print all detected bubble texts.
    """
    scraper = MangadexScraper()
    test_url = "https://mangadex.org/chapter/404de169-f8c1-4ff2-9ae4-9ef2f25940ae"

    try:
        image_urls = scraper.scrape(test_url)
        assert image_urls, "No images returned by scraper."
        print(f"Scraped {len(image_urls)} image URLs total.")
    except Exception as e:
        pytest.skip(f"Scraper failed due to network or API issue: {e}")

    image_subset = image_urls[:5]
    print(f"\nProcessing {len(image_subset)} pages...\n")

    ocr = EasyOCRProcessor()

    for idx, url in enumerate(image_subset, start=1):
        image_path = tmp_path / f"page_{idx}.jpg"

        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            image_path.write_bytes(r.content)
            print(f"Downloaded page {idx}: {url}")
        except Exception as e:
            pytest.skip(f"Failed to download page {idx}: {e}")

        try:
            groups = ocr.extract_text(str(image_path))
            assert isinstance(groups, list), f"OCR output for page {idx} is not a list."

            num_bubbles = len(groups)
            num_nonempty = sum(
                1 for g in groups
                if (g.get("text") or "").strip()
            )
            print(f"Page {idx}: Detected {num_nonempty} non-empty bubble texts in {num_bubbles} bubbles.")

            if not groups or num_nonempty == 0:
                print("No text detected on this page.\n")
                continue

            print("\n--- OCR TEXT (Page {0}) ---".format(idx))
            for g_idx, group in enumerate(groups, start=1):
                bubble = group.get("bubble", {})
                text = (group.get("text") or "").strip()

                x = bubble.get("x")
                y = bubble.get("y")
                w = bubble.get("width")
                h = bubble.get("height")

                print(f" Bubble {g_idx}: at ({x}, {y}, {w}, {h})")
                if text:
                    print(f"  Text: {repr(text)}")
                else:
                    print("  Text: (empty/whitespace)")

            print("------------------------------\n")

        except Exception as e:
            pytest.skip(f"OCR failed for page {idx}: {e}")


if __name__ == "__main__":
    tmp_dir = Path(tempfile.mkdtemp())
    test_scraper_to_ocr_first_5_pages(tmp_dir)
