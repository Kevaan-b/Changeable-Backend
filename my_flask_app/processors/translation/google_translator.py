from google.cloud import translate_v2 as translate
from my_flask_app.processors.translation.base_translator import BaseTranslator
from config.settings import Config

class GoogleTranslator(BaseTranslator):
    """Translation processor using Google Translate API."""
    
    def __init__(self):
        """Initialize Google Translate client."""
        try:
            self.client = translate.Client(
                credentials=Config.GOOGLE_TRANSLATE_CREDENTIALS
            )
            
        except Exception as e:
            raise e
    
    def translate(self, text_data: list[dict], source_lang: str, 
                 target_lang: str) -> list[dict]:
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
            texts = [item['text'] for item in text_data]
            
            results = self.client.translate(
                texts,
                source_language=source_lang,
                target_language=target_lang
            )
            
            translated_data = []
            for i, (original, result) in enumerate(zip(text_data, results)):
                translated_data.append({
                    **original,
                    'translated_text': result['translatedText'],
                    'translation_confidence': 0.8, 
                    'detected_language': result.get('detectedSourceLanguage', source_lang)
                })
            
            return translated_data
            
        except Exception as e:
            return [{**item, 'translated_text': item['text'], 'translation_confidence': 0.0} 
                   for item in text_data]
