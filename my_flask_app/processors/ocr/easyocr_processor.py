import easyocr
import cv2
import numpy as np

from ocr.base_ocr import BaseOCR
from config.settings import Config


class EasyOCRProcessor(BaseOCR):
    """OCR processor using EasyOCR library."""
    
    def __init__(self):
        """Initialize EasyOCR with configured languages."""
        try:
            self.supported_languages = Config.EASYOCR_LANGUAGES
            self.reader = easyocr.Reader(
                self.supported_languages,
                gpu=Config.USE_GPU_OCR,
                verbose=False
            )
            self.confidence_threshold = Config.OCR_CONFIDENCE_THRESHOLD
        except Exception as e:
            raise
    
    def extract_text(self, image_path: str) -> list[dict]:
        """
        Extract text and bounding boxes from image.
        
        Returns:
            List of dictionaries with 'text', 'bbox', 'confidence'
        """
        try:

            results = self.reader.readtext(
                image_path,
                detail=1,  
                paragraph=False,  
                width_ths=0.7, 
                height_ths=0.7,  
            )
            
            extracted_data = []
            for (bbox, text, confidence) in results:
                if confidence >= self.confidence_threshold and text.strip():
                    extracted_data.append({
                        'text': text.strip(),
                        'bbox': self._normalize_bbox(bbox),
                        'confidence': confidence,
                        'original_bbox': bbox
                    })
            
            return extracted_data
            
        except Exception as e:
            return []
    
    def _preprocess_image(self, image_path: str) -> np.ndarray:
        """Preprocess image for better OCR results."""
        try:
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not read image: {image_path}")
            
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            if Config.OCR_ENHANCE_IMAGE:
                image = self._enhance_image(image)
            
            return image
            
        except Exception as e:
            raise
    
    def _enhance_image(self, image: np.ndarray) -> np.ndarray:
        """Apply image enhancement techniques."""
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        enhanced = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
    
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2RGB)
        
        return enhanced
    
    def _normalize_bbox(self, bbox: list[list[int]]) -> dict[str, int]:
        """Convert EasyOCR bbox format to normalized format."""
        xs = [point[0] for point in bbox]
        ys = [point[1] for point in bbox]
        
        return {
            'x': min(xs),
            'y': min(ys),
            'width': max(xs) - min(xs),
            'height': max(ys) - min(ys)
        }
