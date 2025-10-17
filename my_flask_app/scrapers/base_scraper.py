"""
Base class for web scrapers.
"""
from abc import ABC

class BaseScraper(ABC):
    """Base class for website scrapers."""
    

    def can_handle(self, url):
        """Check if this scraper can handle the given URL."""
        raise NotImplementedError
   

    def scrape(self, url):
        """Scrape images from the given URL."""
        raise NotImplementedError

