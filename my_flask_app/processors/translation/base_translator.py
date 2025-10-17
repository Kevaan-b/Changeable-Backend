"""
Abstract base class and factory for translation processors.
"""
from abc import ABC, abstractmethod
from my_flask_app.config.settings import Config

class BaseTranslator(ABC):
    """Abstract base class for translation processors."""
    
    @abstractmethod
    def translate(self, text_data, source_lang, target_lang):
        """Translate extracted text data."""
        pass

class TranslatorFactory:
    """Factory for creating translation processors."""
    
    @staticmethod
    def create(fallback: bool = True):
        """Create translator based on configuration."""
        translator_type = Config.TRANSLATOR_ENGINE
        
        try:
            if translator_type == 'gemini':
                from my_flask_app.processors.translation.gemini_translator import GeminiTranslator
                return GeminiTranslator()
            elif translator_type == 'google':
                from my_flask_app.processors.translation.google_translator import GoogleTranslator
                return GoogleTranslator()
            else:
                raise ValueError(f"Unknown translator: {translator_type}")
                
        except Exception as e:
            if fallback and translator_type != 'google':
                # Fallback to Google Translate
                try:
                    from my_flask_app.processors.translation.google_translator import GoogleTranslator
                    return GoogleTranslator()
                except Exception:
                    pass
            raise e
