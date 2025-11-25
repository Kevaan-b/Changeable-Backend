from abc import ABC

class BaseTranslator(ABC):
    """Base class for translation processors."""
    
    def translate(self, text_data, target_lang):
        """Translate extracted text data."""
        raise NotImplementedError
