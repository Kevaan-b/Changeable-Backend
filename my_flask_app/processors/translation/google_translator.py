"""
Google Translate fallback implementation.
"""
from google.cloud import translate_v2 as translate
from typing import List, Dict
import logging
from processors.translation.base_translator import BaseTranslator
from config.settings import Config

logger = logging.getLogger(__name__)

class GoogleTranslator(BaseTranslator):
    """Translation processor using Google Translate API."""
    
    def __init__(self):
        """Initialize Google Translate client."""
        try:
            self.client = translate.Client(
                credentials=Config.GOOGLE_TRANSLATE_CREDENTIALS
            )
            logger.info("Google Translator initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Google Translator: {e}")
            raise
    
    def translate(self, text_data: List[Dict], source_lang: str, 
                 target_lang: str) -> List[Dict]:
        """
        Translate text data using Google Translate.
        
        Args:
            text_data: List of text elements with bbox and confidence
            source_lang: Source language code
            target_lang: Target language code
        
        Returns:
            List of translated text elements
        """
        if not text_data:
            return []
        
        try:
            # Extract texts for translation
            texts = [item['text'] for item in text_data]
            
            # Batch translate
            results = self.client.translate(
                texts,
                source_language=source_lang,
                target_language=target_lang
            )
            
            # Merge results with original data
            translated_data = []
            for i, (original, result) in enumerate(zip(text_data, results)):
                translated_data.append({
                    **original,
                    'translated_text': result['translatedText'],
                    'translation_confidence': 0.8,  # Google Translate is reliable
                    'detected_language': result.get('detectedSourceLanguage', source_lang)
                })
            
            logger.info(f"Successfully translated {len(translated_data)} elements using Google Translate")
            return translated_data
            
        except Exception as e:
            logger.error(f"Google Translate failed: {e}")
            # Return original data as fallback
            return [{**item, 'translated_text': item['text'], 'translation_confidence': 0.0} 
                   for item in text_data]
