import cv2
from pathlib import Path
from my_flask_app.processors.typesetting.base_typesetter import Typesetter


class EasyOCRTypesetter(Typesetter):
    def __init__(
        self,
        font=cv2.FONT_HERSHEY_SIMPLEX,
        scale=0.7,
        thk=2,
        text_color=(0,0,0),
        bg_color=(255,255,255),
        padding=8,
        align="center",
        merge_x=10,
        merge_y=10,
    ):
        self.font = font
        self.scale = scale
        self.thk = thk
        self.text_color = text_color
        self.bg_color = bg_color
        self.padding = padding
        self.align = align
        self.merge_x = merge_x
        self.merge_y = merge_y

    def wrap(self, text, width, scale):
        words = text.split()
        line, out = [], []
        for w in words:
            test = line + [w]
            sz, _ = cv2.getTextSize(" ".join(test), self.font, scale, self.thk)
            if sz[0] <= width or not line:
                line = test
            else:
                out.append(" ".join(line))
                line = [w]
        if line:
            out.append(" ".join(line))
        return out

    def line_height(self, scale):
        sz, bl = cv2.getTextSize("Ag", self.font, scale, self.thk)
        return sz[1] + bl

    def wrap_and_scale(self, text, w, h):
        text = " ".join(text.split())
        scale = min(self.scale * 1.2, 1.2)
        while scale >= 0.3:
            lines = self.wrap(text, w, scale)
            lh = self.line_height(scale)
            if len(lines) * lh <= h:
                return lines, scale
            scale -= 0.1
        return [text], 0.3

    def align_x(self, line, x, w, avail_w, scale):
        sz, _ = cv2.getTextSize(line, self.font, scale, self.thk)
        tw = sz[0]
        left = x + self.padding
        if self.align == "right":
            return left + (avail_w - tw)
        if self.align == "center":
            return left + (avail_w - tw)//2
        return left

    def apply(self, image_path, ocr, out):
        img = cv2.imread(str(image_path))

        for group in ocr:
            bubble = group["bubble"]
            full_raw = group.get("text", "") or ""

            # Normalize whitespace
            full = " ".join(full_raw.split())
            if not full:
                continue  # nothing to draw

            x = bubble["x"]
            y = bubble["y"]
            w = bubble["width"]
            h = bubble["height"]

            # Cover existing text with background rectangle
            cv2.rectangle(img, (x, y), (x + w, y + h), self.bg_color, -1)

            # Available width/height inside bubble after padding
            aw, ah = w - 2 * self.padding, h - 2 * self.padding

            # Wrap and scale the concatenated bubble text
            lines, s = self.wrap_and_scale(full, aw, ah)
            lh = self.line_height(s)

            yc = y + self.padding + lh
            for line in lines:
                xc = self.align_x(line, x, w, aw, s)
                cv2.putText(img, line, (xc, yc), self.font, s, self.text_color, self.thk)
                yc += lh

        cv2.imwrite(str(out), img)
        return str(out)

