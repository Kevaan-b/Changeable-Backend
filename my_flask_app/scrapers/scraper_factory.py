"""
Factory for creating appropriate scrapers based on URL.
"""
from scrapers.mangadex_scraper import MangadexScraper

class ScraperFactory:
    """Factory for creating website scrapers."""
    
    def __init__(self):
        self.scrapers = [
            MangadexScraper(),
        ]
    
    def get_scraper(self, url: str):
        """Get appropriate scraper for URL."""
        for scraper in self.scrapers:
            if scraper.can_handle(url):
                return scraper
        
        return None
    
    def create_from_url(self, url: str):
        """Alias for get_scraper method."""
        return self.get_scraper(url)
