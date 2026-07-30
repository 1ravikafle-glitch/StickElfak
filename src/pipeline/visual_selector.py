"""
visual_selector.py — builds the labeled "inset box" for each item (A/B) the
first time it's introduced, and tracks which boxes should be visible by
each beat (cumulative — once introduced, a box stays visible, matching the
reference video's comparison layout).
"""

import os
from dataclasses import dataclass
from PIL import Image, ImageDraw, ImageFont


@dataclass
class InsetBox:
    label: str
    image_path: str


def _font(size):
    for path in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",):
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def _make_box(label: str, color: tuple, out_path: str, size=(420, 300)):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius=24,
                            fill=(255, 255, 255, 255), outline=(20, 20, 20, 255), width=4)
    draw.rounded_rectangle([0, 0, size[0] - 1, 70], radius=24,
                            fill=color)
    draw.rectangle([0, 40, size[0] - 1, 70], fill=color)  # square off bottom corners of header
    font = _font(34)
    bbox = draw.textbbox((0, 0), label.upper(), font=font)
    tw = bbox[2] - bbox[0]
    draw.text(((size[0] - tw) / 2, 15), label.upper(), font=font, fill=(255, 255, 255, 255))
    # simple body glyph so the card doesn't look empty
    draw.ellipse([size[0] / 2 - 50, 120, size[0] / 2 + 50, 220], fill=color)
    img.save(out_path)


def select_visuals(beats, item_a: str, item_b: str, out_dir: str) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    colors = {"A": (231, 111, 81, 255), "B": (38, 70, 83, 255)}
    labels = {"A": item_a or "A", "B": item_b or "B"}
    boxes = {}
    for key in ("A", "B"):
        path = os.path.join(out_dir, f"box_{key}.png")
        _make_box(labels[key], colors[key], path)
        boxes[key] = InsetBox(label=labels[key], image_path=path)

    visible_by_beat = {}
    seen = []
    for beat in beats:
        if beat.item and beat.item not in seen:
            seen.append(beat.item)
        visible_by_beat[beat.index] = list(seen)
    return {"boxes": boxes, "visible_by_beat": visible_by_beat}
