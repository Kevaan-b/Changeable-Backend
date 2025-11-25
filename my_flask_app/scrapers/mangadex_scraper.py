import requests

from my_flask_app.scrapers.base_scraper import BaseScraper
from my_flask_app.models.context import Context

class MangadexScraper(BaseScraper):

    attempts = 3
    
    def can_handle(self, url: str) -> bool:
        """Returns true if the mangadex url is valid"""
        base_url = 'https://mangadex.org/chapter/'
        return url.startswith(base_url) and len(url) > len(base_url)
   
    def get_json(self, url: str) -> dict:
        """Given url, return json"""
        for _ in range(self.attempts):
            r = requests.get(url)
        
            if r.ok:
                return r.json()
        
        return []


    def scrape(self, url: str) -> list[str]:
        """Return an array of image links from the particular site (url)"""
        base_url = 'https://mangadex.org/chapter/'
        image_url = 'https://api.mangadex.org/at-home/server/'


        if not self.can_handle(url):
            return []

        chapter_id = url.split("/chapter/")[1].split("/")[0]
        chapter_data = self.get_json(image_url + chapter_id)
        chapter_images = []
        for i in range(len(chapter_data['chapter']['data'])):
            chapter_images.append(
                'https://uploads.mangadex.org/data/' +
                chapter_data['chapter']['hash'] + '/' +
                chapter_data['chapter']['data'][i]
            )

        return chapter_images


    def scrape_context(self, url: str) -> Context:
        """Return a context object for the given URL"""
        base_url = 'https://mangadex.org/chapter/'
        api_url = 'https://api.mangadex.org'

        if not self.can_handle(url):
            return None

        chapter_id = url.split("/chapter/")[1].split("/")[0]

        chapter_data = self.get_json(f"{api_url}/chapter/{chapter_id}?includes[]=manga")
        data = chapter_data.get("data")

        if not data:
            return None

        if isinstance(data, list):
            data = data[0] if data else None

        if not isinstance(data, dict):
            return None

        relationships = data.get("relationships", [])

        manga_rel = next(
            (r for r in relationships
            if r.get("type") == "manga" and r.get("related") in (None, "manga")),
            None
        )

        if not manga_rel:
            return None

        manga_id = manga_rel['id']

        manga_data = self.get_json(f"{api_url}/manga/{manga_id}?includes[]=tags")
        attributes = manga_data['data']['attributes']

        title = attributes['title'].get('en') or next(iter(attributes['title'].values()))
        alt_titles = [
            v.get("en") or next(iter(v.values())) for v in attributes.get("altTitles", []) if isinstance(v, dict)
        ]
        description = (
            attributes.get("description", {}).get("en") or next(iter(attributes.get("description", {}).values()), "")
        )
        tags = [
            t["attributes"]["name"].get("en") or next(iter(t["attributes"]["name"].values())) for t in attributes.get("tags", [])
        ]

        demographic = attributes.get("publicationDemographic")
        publication_demographic = [demographic] if demographic else []
        year = attributes.get("year", None)

        return Context(
            title=title,
            alt_titles=alt_titles,
            description=description,
            tags=tags,
            publication_demographic=publication_demographic,
            year=year
        )

    def scrape_context_manga(self, url: str) -> Context:
        """Return a context object for the given Manga URL"""
        base_url = 'https://mangadex.org/title/'
        api_url = 'https://api.mangadex.org'

        if not self.can_handle(url):
            return None

        manga_id = url.rstrip('/').split('/')[-1]

        manga_data = self.get_json(f"{api_url}/manga/{manga_id}?includes[]=tags")
        if not manga_data or manga_data.get("result") != "ok":
            print("Invalid manga response:", manga_data)
            return None

        attributes = manga_data["data"]["attributes"]

        title = attributes["title"].get("en") or next(iter(attributes["title"].values()))

        alt_titles = [
            v.get("en") or next(iter(v.values()))
            for v in attributes.get("altTitles", [])
            if isinstance(v, dict)
        ]

        description = (
            attributes.get("description", {}).get("en")
            or next(iter(attributes.get("description", {}).values()), "")
        )

        tags = [
            t["attributes"]["name"].get("en")
            or next(iter(t["attributes"]["name"].values()))
            for t in attributes.get("tags", [])
        ]

        demographic = attributes.get("publicationDemographic")
        publication_demographic = [demographic] if demographic else []

        year = attributes.get("year")

        return Context(
            title=title,
            alt_titles=alt_titles,
            description=description,
            tags=tags,
            publication_demographic=publication_demographic,
            year=year,
        )

    def get_id(self, url: str):
        return "mangadex-" + url.split("/chapter/")[1].split("/")[0]
