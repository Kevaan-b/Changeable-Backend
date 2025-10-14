"""
Abstract base class and factory for OCR processors.
"""
from abc import ABC, abstractmethod
from my_flask_app.config.settings import Config

class BaseOCR(ABC):
    """Abstract base class for OCR processors."""
    
    @abstractmethod
    def extract_text(self, image_path: str):
        """Extract text and bounding boxes from image."""
        pass

class OCRFactory:
    """Factory for creating OCR processors."""
    
    @staticmethod
    def create():
        """Create OCR processor based on configuration."""
        ocr_type = Config.OCR_ENGINE
        
        if ocr_type == 'easyocr':
            from my_flask_app.processors.ocr.easyocr_processor import EasyOCRProcessor
            return EasyOCRProcessor()
        else:
            raise ValueError(f"Unknown OCR engine: {ocr_type}")
