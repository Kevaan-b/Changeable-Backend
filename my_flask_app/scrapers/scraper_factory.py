"""
Factory for creating appropriate scrapers based on URL.
"""
from sites.mangadex_scraper import MangadexScraper

import logging

logger = logging.getLogger(__name__)

class ScraperFactory:
    """Factory for creating website scrapers."""
    
    def __init__(self):
        self.scrapers = [
            MangadexScraper(),
            # Add more scrapers here as needed
        ]
    
    def get_scraper(self, url: str):
        """Get appropriate scraper for URL."""
        for scraper in self.scrapers:
            if scraper.can_handle(url):
                logger.info(f"Using {scraper.__class__.__name__} for {url}")
                return scraper
        
        logger.warning(f"No scraper available for URL: {url}")
        return None
    
    # Alias for backward compatibility
    def create_from_url(self, url: str):
        """Alias for get_scraper method."""
        return self.get_scraper(url)
