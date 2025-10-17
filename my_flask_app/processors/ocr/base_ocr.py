"""
Abstract base class and factory for OCR processors.
"""
from abc import ABC, abstractmethod
from config.settings import Config
from ocr.easyocr_processor import EasyOCRProcessor

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
            return EasyOCRProcessor()
        else:
            raise ValueError(f"Unknown OCR engine: {ocr_type}")
