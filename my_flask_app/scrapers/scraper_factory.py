"""
Factory for creating appropriate scrapers based on URL.
"""
from sites import mangadex_scraper;
class ScraperFactory:
    """Factory for creating website scrapers."""
    
    def __init__(self):
        self.scrapers = [
            mangadex_scraper.MangaDexScraper(),
            GenericScraper()  
        ]
    
    def get_MangaDexScraper(self):
        """Get MangaDex scraper."""
        return self.scrapers[0]
       
