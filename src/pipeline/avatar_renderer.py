"""
avatar_renderer.py — v1 implements the "static" mode only: one original,
simple stick-figure character PNG, reused across every beat, anchored at
bottom-center. Talking/lip-synced mode is left NotImplementedError — wire
in a lip-sync tool later per ARCHITECTURE.md if needed.
"""

import os
from PIL import Image, ImageDraw


def _draw_character(out_path: str, size=(360, 520)):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    accent = (38, 90, 196, 255)
    outline = (20, 20, 20, 255)

    cx = size[0] // 2
    # head
    d.ellipse([cx - 70, 10, cx + 70, 150], fill=(255, 255, 255, 255), outline=outline, width=6)
    # simple glasses
    d.rectangle([cx - 50, 70, cx - 10, 100], outline=outline, width=5)
    d.rectangle([cx + 10, 70, cx + 50, 100], outline=outline, width=5)
    d.line([cx - 10, 85, cx + 10, 85], fill=outline, width=5)
    # smile
    d.arc([cx - 25, 95, cx + 25, 125], start=20, end=160, fill=outline, width=4)
    # body (hoodie)
    d.rounded_rectangle([cx - 90, 150, cx + 90, 400], radius=40, fill=accent, outline=outline, width=6)
    # raised arm
    d.line([cx - 70, 200, cx - 110, 90], fill=outline, width=14)
    d.line([cx - 70, 200, cx - 110, 90], fill=(255, 255, 255, 255), width=6)
    # legs
    d.rectangle([cx - 60, 390, cx - 10, 470], fill=(255, 255, 255, 255), outline=outline, width=5)
    d.rectangle([cx + 10, 390, cx + 60, 470], fill=(255, 255, 255, 255), outline=outline, width=5)
    # shoes
    d.rounded_rectangle([cx - 70, 465, cx - 5, 495], radius=10, fill=accent, outline=outline, width=4)
    d.rounded_rectangle([cx + 5, 465, cx + 70, 495], radius=10, fill=accent, outline=outline, width=4)
    # laptop hint
    d.rounded_rectangle([cx - 20, 250, cx + 90, 330], radius=8, fill=(210, 210, 210, 255), outline=outline, width=4)

    img.save(out_path)


def render_avatar_track(character_asset_dir: str) -> str:
    os.makedirs(character_asset_dir, exist_ok=True)
    path = os.path.join(character_asset_dir, "static_pose.png")
    _draw_character(path)
    return path
