"""
API endpoints for handling translation requests.
"""
from flask import Blueprint, request, jsonify, send_file
from io import BytesIO
import zipfile
from scrapers import scraper_factory
from services import translation_service

api_bp = Blueprint('api', __name__)

class TranslationController:
    def __init__(self):
        self.translation_service = translation_service.TranslationService()
        self.scraper_factory = scraper_factory.ScraperFactory()

    
    def translate_raw(self, images: list, language: str) -> list:
        """translate raw to given language"""
        pass

    def get_raw(self, url: str, site: str) -> list:
        if site == 'mangadex':
            self.scraper_factory[0].scrape(url)
        
    def translate_upload(self):
        """Handle image upload and translation."""
        pass
    

    @api_bp.route('/translate/mangadex', methods=['POST'])
    def translate_link(self):
        """
        Body (JSON):
        - chapter_url: str (required)
        - language: str (required)
        - site: str (required)
        Returns: ZIP containing all translated pages as 001.png, 002.png, ...
        """
        payload = request.get_json(silent=True) or {}
        chapter_url = payload.get("chapter_url")
        language = payload.get("language")
        site = payload.get("site")
        
        if not chapter_url:
            return jsonify({"ok": False, "error": "Missing 'chapter_url'"}), 400
        if not language:
            return jsonify({"ok": False, "error": "Missing 'language'"}), 400
        if not site:
            return jsonify({"ok": False, "error": "Missing 'site'"}), 400

        try:
            # Get all translated page images (bytes)
            raw = self.get_raw(chapter_url, site)
            pages = list(self.translate_raw(raw, language))  # in case it's a generator

            if not pages:
                return jsonify({"ok": False, "error": "No translated pages produced"}), 502


            buf = BytesIO()
            with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_STORED) as z:
                for i, img_bytes in enumerate(pages, 1):
                    # If you output JPEGs, change the extension accordingly
                    z.writestr(f"{i:03d}.png", img_bytes)
            buf.seek(0)

            return send_file(
                buf,
                mimetype="application/vnd.comicbook+zip",
                as_attachment=True,
                download_name="translated_chapter.cbz",
            )
        except Exception as e:
            return jsonify({"ok": False, "error": str(e)}), 500

    def translate_scrape(self):
        """Handle link scraping and translation."""
        pass
    
