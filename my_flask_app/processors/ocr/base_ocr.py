"""
Base class and factory for OCR processors.
"""
from abc import ABC 

class BaseOCR(ABC):
    """Base class for OCR processors."""
    
    def extract_text(self, image_path: str):
        """Extract text and bounding boxes from image."""
        raise NotImplementedError

