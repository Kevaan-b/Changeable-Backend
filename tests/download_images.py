"""
Utility: Download and save all images from a MangaDex chapter locally.
"""

import os
import requests
from pathlib import Path
from my_flask_app.scrapers.mangadex_scraper import MangadexScraper


def download_chapter(chapter_url: str, save_dir: str = "./tests/chapter_images") -> list[str]:
    scraper = MangadexScraper()
    image_urls = scraper.scrape(chapter_url)
    if not image_urls:
        raise ValueError("No images found for the given chapter URL.")

    save_path = Path(save_dir)
    save_path.mkdir(parents=True, exist_ok=True)
    saved_files = []

    print(f"Downloading {len(image_urls)} pages to {save_path.resolve()}")

    for idx, url in enumerate(image_urls, start=1):
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()

            filename = save_path / f"page_{idx:02d}.jpg"
            filename.write_bytes(response.content)
            saved_files.append(str(filename))
            print(f"Saved page {idx} → {filename.name}")

        except Exception as e:
            print(f"Failed to download page {idx}: {e}")

    print(f"\nDownload complete. {len(saved_files)} pages saved to {save_path}")
    return saved_files


if __name__ == "__main__":
    #chapter_url = "https://mangadex.org/chapter/404de169-f8c1-4ff2-9ae4-9ef2f25940ae"
    #chapter_url = "https://mangadex.org/chapter/a2cde851-a4eb-4b73-94d3-514a2044a61b"
    chapter_url = "https://mangadex.org/chapter/5075698a-1e26-42cb-922e-673bd77c73c3"
    download_chapter(chapter_url)
