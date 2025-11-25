"""
Main business logic for translation processing.
Handles upload and link-based translation.
"""

import cv2
import requests
import tempfile
import uuid
import os

from my_flask_app.models.context import Context


class TranslationService:
    """Orchestrates the translation workflow with reusable context."""

    def __init__(self, scraper_factory, ocr_processor, translator, typesetter):
        self.scraper_factory = scraper_factory
        self.ocr_processor = ocr_processor
        self.translator = translator
        self.typesetter = typesetter

    def process_upload(self, files, target_lang: str) -> str:
        try:
            image_paths = []
            for file_obj in files:
                temp_path = self._save_bytes_to_temp_file(file_obj.read())
                image_paths.append(temp_path)
            
            return self._process_images(image_paths, target_lang, uuid.uuid4())
            
        except Exception as e:
            return {"error": str(e), "results": []}

    def process_links(self, links: list[str], target_lang: str) -> str:
        try:
            all_image_paths = []
            context = None
            
            for link in links:
                scraper = self.scraper_factory.get_scraper(link)
                if not scraper:
                    continue

                image_urls = scraper.scrape(link)
                context = scraper.scrape_context(link)
                id = scraper.get_id(link) + "-" + target_lang
                
                for img_url in image_urls:
                    response = requests.get(img_url, timeout=10)
                    response.raise_for_status()
                    
                    temp_path = self._save_bytes_to_temp_file(response.content)
                    all_image_paths.append(temp_path)

            return self._process_images(all_image_paths, target_lang, id, context)
            
        except Exception as e:
            return {"error": str(e), "results": []}

    def _process_images(
        self,
        image_paths: list[str],
        target_lang: str,
        id: str,
        context: Context = None,
    ) -> str | None:
        """
        Core image processing pipeline.
        1. OCR ->  2. Translate -> 3. Typeset
        """
        for idx, image_path in enumerate(image_paths, start=1):
            try:
                ocr_results = self.ocr_processor.extract_text(image_path)
                
                translated_data = self.translator.translate(
                    ocr_results, 
                    target_lang=target_lang, 
                    context=context
                )

                self._apply_typesetting(image_path, translated_data, id, idx)

            except Exception as e:
                print(e)
                return None
        
        return id
    
    def _save_bytes_to_temp_file(self, image_bytes: bytes) -> str:
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_file.write(image_bytes)
            temp_path = temp_file.name

        test_image = cv2.imread(temp_path)
        if test_image is None:
            raise ValueError("Invalid image data")

        return temp_path

    def _image_path_to_bytes(self, image_path: str) -> bytes:
        try:
            with open(image_path, 'rb') as f:
                return f.read()
        except Exception:
            return b''

    def _apply_typesetting(self, image_path: str, translated_data: list[dict], id: str, page_number: int) -> str:
        directory = "uploads/" + id
        os.makedirs(directory, exist_ok=True)

        filename = f"page_{page_number}.png"
        out_path = os.path.join(directory, filename)

        self.typesetter.apply(image_path, translated_data, out_path)

        return out_path

    def get_processing_status(self, task_id: str = None):
        raise NotImplementedError
