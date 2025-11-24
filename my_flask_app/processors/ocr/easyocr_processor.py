import easyocr
import cv2
import numpy as np

from .base_ocr import BaseOCR
from my_flask_app.config.settings import Config


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
            raise RuntimeError(f"Failed to initialize EasyOCRProcessor: {e}")
    
    def extract_text(self, image_path: str) -> list[dict]:

        reader = easyocr.Reader(["en"], gpu=False, verbose=False)
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Failed to read image: {image_path}")
        h, w = img.shape[:2]

        panels = self._detect_panels(img)

        results_all = []
        for (x, y, w_p, h_p) in panels:
            crop = img[y:y + h_p, x:x + w_p]

            # results = reader.readtext(
            #     crop,
            #     detail=1,
            #     paragraph=False,
            #     width_ths=0.001,
            #     height_ths=0.001,
            # )

            results = reader.readtext(crop) # Using default parameters for better accuracy

            page_h, page_w = img.shape[:2]
            page_area = page_h * page_w

            for (bbox, text, conf) in results:
                if conf <= 0.2 or not text.strip():
                    continue
                xs = [int(p[0]) for p in bbox]
                ys = [int(p[1]) for p in bbox]
                x0, y0, x1, y1 = min(xs) + x, min(ys) + y, max(xs) + x, max(ys) + y  # re offset

                w0 = max(xs) - min(xs)
                h0 = max(ys) - min(ys)
                bbox_area = w0 * h0

                # Absolute limits to ignore huge text boxes
                if bbox_area > 0.10 * page_area:      # > 10% of full page
                    continue

                results_all.append({
                    "text": text.strip(),
                    "confidence": conf,
                    "bbox": {"x": x0, "y": y0, "width": x1 - x0, "height": y1 - y0},
                    "original_bbox": bbox,
                })

        return results_all

    def _detect_panels(self, image: np.ndarray) -> list[tuple[int, int, int, int]]:
        """Detect possible manga panels using edge-based segmentation."""
        #gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(image, (5, 5), 0)
        edges = cv2.Canny(blur, 50, 150)
        dilated = cv2.dilate(edges, np.ones((5, 5), np.uint8), iterations=2)

        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        panels = [
            (x, y, w, h)
            for (x, y, w, h) in [cv2.boundingRect(c) for c in contours]
            if w * h > 50000  # Ignore small areas
        ]
        print(panels)
        return panels