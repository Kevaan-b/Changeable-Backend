"""
Main business logic for translation processing.
Handles upload and link-based translation.
"""
import cv2
import logging
import requests
import tempfile

from scrapers.scraper_factory import ScraperFactory
from processors.ocr.easyocr_processor import EasyOCRProcessor
from processors.translation.gemini_translator import GeminiTranslator


class TranslationService:
    """Orchestrates the translation workflow."""

    def __init__(self):
        # Initialize components directly
        self.scraper_factory = ScraperFactory()
        self.ocr_processor = EasyOCRProcessor()
        self.translator = GeminiTranslator()
        # self.typesetter = OpenCVTypesetter() (To be implemented in future)

    def process_upload(self, files, source_lang: str, target_lang: str) -> dict:
        """
        Process uploaded images for translation.
        Args:
            files: list of file objects 
            source_lang: original language (e.g. 'ja')
            target_lang: target translation language (e.g. 'en')
        Returns:
            Results with translated images and metadata
        """
        try:
            image_paths = []
            for file_obj in files:
                temp_path = self._save_bytes_to_temp_file(file_obj.read())
                image_paths.append(temp_path)
            
            return self._process_images(image_paths, source_lang, target_lang)
            
        except Exception as e:
            return {"error": str(e), "results": []}

    def process_links(self, links: list[str], source_lang: str, target_lang: str) -> dict:
        """
        Process one or more chapter links (scrape + translate).
        Args:
            links: list of URLs (e.g., MangaDX chapter links)
            source_lang: original language
            target_lang: target translation language
        Returns:
            Results with translated images and metadata
        """
        try:
            all_image_paths = []
            
            for link in links:
                scraper = self.scraper_factory.get_scraper(link)
                if not scraper:
                    continue

                image_urls = scraper.scrape(link)
                
                for img_url in image_urls:
                    response = requests.get(img_url, timeout=10)
                    response.raise_for_status()
                    
                    temp_path = self._save_bytes_to_temp_file(response.content)
                    all_image_paths.append(temp_path)
                        

            return self._process_images(all_image_paths, source_lang, target_lang)
            
        except Exception as e:
            return {"error": str(e), "results": []}

    def _process_images(self, image_paths: list[str], source_lang: str, target_lang: str) -> dict:
        """
        Core image processing pipeline.
        1. OCR ->  2. Translate -> 3. Typeset
        Args:
            image_paths: list of image file paths
            source_lang: original language
            target_lang: target translation language
        Returns:
            Results with translated images and metadata
        """
        results = []
        
        for idx, image_path in enumerate(image_paths, start=1):
            try:
                
                ocr_results = self.ocr_processor.extract_text(image_path)
                
                if not ocr_results:
                    results.append({
                        'page_number': idx,
                        'original_image': image_path,
                        'processed_image': image_path,  # Return original if no text
                        'ocr_data': [],
                        'translation_data': [],
                        'status': 'no_text_detected'
                    })
                    continue


                translated_data = self.translator.translate(
                    ocr_results, 
                    source_lang=source_lang, 
                    target_lang=target_lang
                )

                
                processed_image_path = image_path
                

                # Convert processed image to bytes for response
                processed_image_bytes = self._image_path_to_bytes(processed_image_path)
                
                results.append({
                    'page_number': idx,
                    'original_image': image_path,
                    'processed_image': processed_image_path,
                    'processed_image_bytes': processed_image_bytes,
                    'ocr_data': ocr_results,
                    'translation_data': translated_data,
                    'text_count': len(ocr_results),
                    'status': 'success'
                })


            except Exception as e:
                results.append({
                    'page_number': idx,
                    'original_image': image_path,
                    'processed_image': image_path,  # Fallback to original
                    'ocr_data': [],
                    'translation_data': [],
                    'error': str(e),
                    'status': 'failed'
                })

        
        successful_pages = len([r for r in results if r['status'] == 'success'])
        total_text_regions = sum(r.get('text_count', 0) for r in results)
        
        return {
            'results': results,
            'summary': {
                'total_pages': len(image_paths),
                'successful_pages': successful_pages,
                'failed_pages': len(image_paths) - successful_pages,
                'total_text_regions': total_text_regions,
                'source_language': source_lang,
                'target_language': target_lang
            }
        }

    def _save_bytes_to_temp_file(self, image_bytes: bytes) -> str:
        """Save image bytes to a temporary file and return the path."""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                temp_file.write(image_bytes)
                temp_path = temp_file.name
            
            # Verify the image is valid
            test_image = cv2.imread(temp_path)
            if test_image is None:
                raise ValueError("Invalid image data")
            
            return temp_path
            
        except Exception as e:
            raise

    def _image_path_to_bytes(self, image_path: str) -> bytes:
        """Convert image file to bytes for API response."""
        try:
            with open(image_path, 'rb') as f:
                return f.read()
        except Exception as e:
            return b''

    def get_processing_status(self, task_id: str = None):
        """Get status of processing task (for future async implementation)."""
        pass
