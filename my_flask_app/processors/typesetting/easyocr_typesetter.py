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
        layout="flow",
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
        self.layout = layout
        self.align = align
        self.merge_x = merge_x
        self.merge_y = merge_y

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
        rects = [(r["bbox"]["x"], r["bbox"]["y"], r["bbox"]["width"], r["bbox"]["height"]) for r in ocr]
        bubbles = self.merge_rects(rects)
        groups = self.assign(rects, bubbles)

        for b in bubbles:
            x, y, w, h = b
            cv2.rectangle(img, (x,y), (x+w, y+h), self.bg_color, -1)
            ids = self.sort_reading_order(rects, groups[b])
            texts = [ocr[i]["text"] for i in ids]

            if self.layout == "flow":
                full = " ".join(" ".join(t.split()) for t in texts)
                aw, ah = w - 2*self.padding, h - 2*self.padding
                lines, s = self.wrap_and_scale(full, aw, ah)
                lh = self.line_height(s)
                yc = y + self.padding + lh
                for line in lines:
                    xc = self.align_x(line, x, w, aw, s)
                    cv2.putText(img, line, (xc, yc), self.font, s, self.text_color, self.thk)
                    yc += lh

            else:
                for i in ids:
                    text = " ".join(ocr[i]["text"].split())
                    bx, by, bw, bh = rects[i]
                    aw, ah = bw - 2*self.padding, bh - 2*self.padding
                    lines, s = self.wrap_and_scale(text, aw, ah)
                    lh = self.line_height(s)
                    yc = by + self.padding + lh
                    for line in lines:
                        xc = self.align_x(line, bx, bw, aw, s)
                        cv2.putText(img, line, (xc, yc), self.font, s, self.text_color, self.thk)
                        yc += lh

        cv2.imwrite(str(out), img)
        return str(out)
