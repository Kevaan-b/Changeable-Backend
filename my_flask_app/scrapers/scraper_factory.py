"""
Factory for creating appropriate scrapers based on URL.
"""

class ScraperFactory:
    """Factory for creating website scrapers."""
    
    def __init__(self):
        self.scrapers = [
            MangaDexScraper(),
            GenericScraper()  
        ]
    
    def get_MangaDexScraper(self):
        """Get MangaDex scraper."""
        return self.scrapers[0]
       
