"""
Abstract base class and factory for translation processors.
"""
from abc import ABC, abstractmethod
from config.settings import Config
from processors.translation.gemini_translator import GeminiTranslator
from processors.translation.google_translator import GoogleTranslator

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
                return GeminiTranslator()
            elif translator_type == 'google':
                return GoogleTranslator()
            else:
                raise ValueError(f"Unknown translator: {translator_type}")
                
        except Exception as e:
            if fallback and translator_type != 'google':
                # Fallback to Google Translate
                try:
                    return GoogleTranslator()
                except Exception:
                    pass
            raise e
