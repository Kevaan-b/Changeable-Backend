"""
Abstract base class and factory for OCR processors.
"""


class BaseOCR(ABC):
    """Abstract base class for OCR processors."""
    
    def extract_text(self, image_path):
        """Extract text and bounding boxes from image."""
    

class OCRFactory:
    """Factory for creating OCR processors."""
    

    def create():
        """Create OCR processor based on configuration."""
       