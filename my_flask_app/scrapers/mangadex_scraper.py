from .base_scraper import BaseScraper
import requests
class MangadexScraper(BaseScraper):

    base_url = 'https://mangadex.org/chapter/'
    image_url = 'https://api.mangadex.org/at-home/server/'
    attempts = 3
    
    def can_handle(self, url: str) -> bool:
        """Returns true if the mangadex url is valid"""
        return url.startswith(self.base_url) and len(url) > len(self.base_url)
   
    def get_json(self, url: str) -> dict:
        """Given url, return json"""
        for i in range(self.attempts):
            r = requests.get(url)
        
            if r.ok:
                return r.json()
        
        return []


    def scrape(self, url: str) -> list[str]:
        """Return an array of image links from the particular site (url)"""

        if not self.can_handle(url):
            return []

        char_list = url.split('/')
        if char_list[-1] == '/':
            char_list.pop()
        

        chapter_id = char_list[-1]
        chapter_data = self.get_json(self.image_url + chapter_id)
        chapter_images = []
        for i in range(len(chapter_data['chapter']['data'])):
            chapter_images.append(
                'https://uploads.mangadex.org/data/' +
                chapter_data['chapter']['hash'] + '/' +
                chapter_data['chapter']['data'][i]
            )

        return chapter_images
