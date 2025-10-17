"""
Base class and factory for translation processors.
"""
from abc import ABC

class BaseTranslator(ABC):
    """Base class for translation processors."""
    
    def translate(self, text_data, source_lang, target_lang):
        """Translate extracted text data."""
        raise NotImplementedError
