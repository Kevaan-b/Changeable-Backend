"""
Factory for creating appropriate scrapers based on URL.
"""
from my_flask_app.scrapers.sites.mangadex_scraper import MangadexScraper

class ScraperFactory:
    """Factory for creating website scrapers."""
    
    def __init__(self):
        pass
    
    def get_scraper(self, url):
        """Get appropriate scraper for URL."""
       
