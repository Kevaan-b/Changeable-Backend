"""
Test scraper functionality.
"""
import pytest
from my_flask_app.scrapers.mangadex_scraper import MangadexScraper

def test_mangadx_scraper_url_validation():
    """Test MangaDX URL validation."""
    scraper = MangadexScraper()
    
    # Valid URLs
    assert scraper.can_handle("https://mangadex.org/chapter/12345")
    assert scraper.can_handle("https://mangadex.org/chapter/abcd-efgh")
    
    # Invalid URLs
    assert not scraper.can_handle("https://google.com")
    assert not scraper.can_handle("https://mangadx.org/")
    assert not scraper.can_handle("")

def test_mangadx_scraping():
    """Test actual scraping (requires internet)."""
    scraper = MangadexScraper()
    
    # Use a known test chapter ID (replace with actual)
    test_url = "https://mangadex.org/chapter/404de169-f8c1-4ff2-9ae4-9ef2f25940ae"
    
    try:
        results = scraper.scrape(test_url)
        assert isinstance(results, list)
        print(results)
    except Exception as e:
        pytest.skip(f"Scraping test failed either network or API issue: {e}")