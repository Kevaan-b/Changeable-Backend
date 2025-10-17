"""
Abstract base class and factory for typesetting processors.
"""
from abc import ABC, abstractmethod
from my_flask_app.config.settings import Config

class BaseTypesetter(ABC):
    """Abstract base class for typesetting processors."""
    
    @abstractmethod
    def apply_translation(self, image_path: str, ocr_data: list[dict], 
                         translated_data: list[dict]) -> str:
        """Apply translated text to image, removing original text."""
        pass

class TypesetterFactory:
    """Factory for creating typesetting processors."""
    
    @staticmethod
    def create():
        """Create typesetter based on configuration."""
        pass