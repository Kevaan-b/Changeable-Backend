import easyocr
import cv2
import numpy as np

from my_flask_app.processors.ocr.base_ocr import BaseOCR
from my_flask_app.config.settings import Config

from pathlib import Path


class EasyOCRProcessor(BaseOCR):
    def __init__(self):
        try:
            self.supported_languages = Config.EASYOCR_LANGUAGES
            self.reader = easyocr.Reader(
                self.supported_languages,
                gpu=Config.USE_GPU_OCR,
                verbose=False
            )
            self.confidence_threshold = Config.OCR_CONFIDENCE_THRESHOLD
            self.merge_x = 10
            self.merge_y = 10
        except Exception as e:
            raise RuntimeError(f"Failed to initialize EasyOCRProcessor: {e}")

    def rects_close(self, a, b):
        ax, ay, aw, ah = a
        bx, by, bw, bh = b
        ax1, ay1 = ax - self.merge_x, ay - self.merge_y
        ax2, ay2 = ax + aw + self.merge_x, ay + ah + self.merge_y
        bx1, by1 = bx - self.merge_x, by - self.merge_y
        bx2, by2 = bx + bw + self.merge_x, by + bh + self.merge_y
        return not (ax2 <= bx1 or bx2 <= ax1 or ay2 <= by1 or by2 <= ay1)

    def merge_rects(self, rects):
        rects = rects[:]
        changed = True
        while changed:
            changed = False
            merged = []
            for r in rects:
                for i, m in enumerate(merged):
                    if self.rects_close(r, m):
                        x1 = min(r[0], m[0])
                        y1 = min(r[1], m[1])
                        x2 = max(r[0] + r[2], m[0] + m[2])
                        y2 = max(r[1] + r[3], m[1] + m[3])
                        merged[i] = (x1, y1, x2 - x1, y2 - y1)
                        changed = True
                        break
                else:
                    merged.append(r)
            rects = merged
        return rects

    def assign(self, rects, bubbles):
        groups = {b: [] for b in bubbles}
        for i, r in enumerate(rects):
            cx = r[0] + r[2]//2
            cy = r[1] + r[3]//2
            def dist(b):
                bx = b[0] + b[2]//2
                by = b[1] + b[3]//2
                return abs(cx - bx) + abs(cy - by)
            groups[min(bubbles, key=dist)].append(i)
        return groups

    def sort_reading_order(self, rects, indices):
        return sorted(indices, key=lambda i: (rects[i][1], rects[i][0]))

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

            results = reader.readtext(crop)

            page_h, page_w = img.shape[:2]
            page_area = page_h * page_w

            for (bbox, text, conf) in results:
                xs = [int(p[0]) for p in bbox]
                ys = [int(p[1]) for p in bbox]
                x0, y0, x1, y1 = min(xs) + x, min(ys) + y, max(xs) + x, max(ys) + y

                w0 = max(xs) - min(xs)
                h0 = max(ys) - min(ys)
                bbox_area = w0 * h0

                if bbox_area > 0.10 * page_area:
                    continue

                results_all.append({
                    "text": text.strip(),
                    "confidence": conf,
                    "bbox": {"x": x0, "y": y0, "width": x1 - x0, "height": y1 - y0},
                    "original_bbox": bbox,
                })

        rects = [
            (r["bbox"]["x"], r["bbox"]["y"], r["bbox"]["width"], r["bbox"]["height"])
            for r in results_all
        ]

        if not rects:
            return []

        bubbles = self.merge_rects(rects)
        bubbles.reverse()
        groups = self.assign(rects, bubbles)

        structured = []
        for b in bubbles:
            ids = self.sort_reading_order(rects, groups[b])
            items = [results_all[i] for i in ids]

            # Concatenate text for each bubble in reading order
            bubble_text = " ".join(item["text"] for item in items if item["text"])

            structured.append({
                "bubble": {
                    "x": b[0],
                    "y": b[1],
                    "width": b[2],
                    "height": b[3],
                },
                "text": bubble_text,
            })

        print(structured)
        return structured

    def _detect_panels(self, image: np.ndarray) -> list[tuple[int, int, int, int]]:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blur, 50, 150)
        dilated = cv2.dilate(edges, np.ones((5, 5), np.uint8), iterations=2)

        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        panels = [
            (x, y, w, h)
            for (x, y, w, h) in [cv2.boundingRect(c) for c in contours]
            if w * h > 50000
        ]
        print(panels)
        return panels
