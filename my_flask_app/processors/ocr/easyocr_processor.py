"""
EasyOCR implementation for text extraction.
"""
import easyocr
import cv2
import numpy as np
from typing import List, Dict, Tuple
import logging
from my_flask_app.processors.ocr.base_ocr import BaseOCR
from my_flask_app.config.settings import Config

logger = logging.getLogger(__name__)

class EasyOCRProcessor(BaseOCR):
    """OCR processor using EasyOCR library."""
    
    def __init__(self):
        """Initialize EasyOCR with configured languages."""
        try:
            # Initialize with multiple language support
            self.supported_languages = Config.EASYOCR_LANGUAGES
            self.reader = easyocr.Reader(
                self.supported_languages,
                gpu=Config.USE_GPU_OCR,
                verbose=False
            )
            self.confidence_threshold = Config.OCR_CONFIDENCE_THRESHOLD
            logger.info(f"EasyOCR initialized with languages: {self.supported_languages}")
        except Exception as e:
            logger.error(f"Failed to initialize EasyOCR: {e}")
            raise
    
    def extract_text(self, image_path: str) -> List[Dict]:
        """
        Extract text and bounding boxes from image.
        
        Returns:
            List of dictionaries with 'text', 'bbox', 'confidence'
        """
        try:
            # Read and preprocess image
            #image = self._preprocess_image(image_path)
            
            # Perform OCR
            results = self.reader.readtext(
                image_path,
                detail=1,  # Return bounding box coordinates
                paragraph=False,  # Don't merge text into paragraphs
                width_ths=0.7,  # Text width threshold
                height_ths=0.7,  # Text height threshold
            )
            
            # Process and filter results
            extracted_data = []
            for (bbox, text, confidence) in results:
                if confidence >= self.confidence_threshold and text.strip():
                    extracted_data.append({
                        'text': text.strip(),
                        'bbox': self._normalize_bbox(bbox),
                        'confidence': confidence,
                        'original_bbox': bbox
                    })
            
            logger.info(f"Extracted {len(extracted_data)} text elements from {image_path}")
            return extracted_data
            
        except Exception as e:
            logger.error(f"OCR extraction failed for {image_path}: {e}")
            return []
    
    def _preprocess_image(self, image_path: str) -> np.ndarray:
        """Preprocess image for better OCR results."""
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not read image: {image_path}")
            
            # Convert to RGB (EasyOCR expects RGB)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Optional: Apply image enhancements
            if Config.OCR_ENHANCE_IMAGE:
                image = self._enhance_image(image)
            
            return image
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            raise
    
    def _enhance_image(self, image: np.ndarray) -> np.ndarray:
        """Apply image enhancement techniques."""
        # Convert to grayscale for processing
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Apply adaptive threshold
        enhanced = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Convert back to RGB
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2RGB)
        
        return enhanced
    
    def _normalize_bbox(self, bbox: List[List[int]]) -> Dict[str, int]:
        """Convert EasyOCR bbox format to normalized format."""
        # EasyOCR returns [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
        # Convert to {x, y, width, height}
        xs = [point[0] for point in bbox]
        ys = [point[1] for point in bbox]
        
        return {
            'x': min(xs),
            'y': min(ys),
            'width': max(xs) - min(xs),
            'height': max(ys) - min(ys)
        }
