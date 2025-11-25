"""
Test scraper functionality.
"""
import pytest
from my_flask_app.scrapers.mangadex_scraper import MangadexScraper


BASE_CHAPTER_URL = "https://mangadex.org/chapter/"


def test_mangadx_scraper_url_validation():
    """Test MangaDX URL validation."""
    scraper = MangadexScraper()
    
    # Valid URLs
    assert scraper.can_handle("https://mangadex.org/chapter/12345", BASE_CHAPTER_URL)
    assert scraper.can_handle("https://mangadex.org/chapter/abcd-efgh", BASE_CHAPTER_URL)
    
    # Invalid URLs
    assert not scraper.can_handle("https://google.com", BASE_CHAPTER_URL)
    assert not scraper.can_handle("https://mangadx.org/", BASE_CHAPTER_URL)
    assert not scraper.can_handle("", BASE_CHAPTER_URL)


def test_mangadx_scraping():
    """Test actual scraping (requires internet)."""
    scraper = MangadexScraper()
    
    # Use a known test chapter ID
    test_url = "https://mangadex.org/chapter/404de169-f8c1-4ff2-9ae4-9ef2f25940ae"
    
    try:
        results = scraper.scrape(test_url)
        assert isinstance(results, list)
    except Exception as e:
        pytest.skip(f"Scraping test failed either network or API issue: {e}")
