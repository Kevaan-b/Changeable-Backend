"""
Abstract base class for web scrapers.
"""
from abc import ABC, abstractmethod

class BaseScraper(ABC):
    """Abstract base class for website scrapers."""
    

    def can_handle(self, url):
        """Check if this scraper can handle the given URL."""
   

    def scrape(self, url):
        """Scrape images from the given URL."""

