"""
compositor.py — the only module that draws pixels and calls ffmpeg.
Renders one full-frame PNG per beat (background + inset boxes + caption +
character), then encodes those frames + the concatenated voiceover into a
final .mp4 with ffmpeg.
"""

import os
import subprocess
import textwrap
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
ACCENT = (47, 217, 232, 255)  # cyan, per style guide


def _font(size, bold=True):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def _make_background(out_path: str):
    img = Image.new("RGB", (W, H), (214, 220, 230))
    # subtle mottled texture using translucent ellipses (cheap, no external asset needed)
    d = ImageDraw.Draw(img, "RGBA")
    import random
    random.seed(7)
    for _ in range(140):
        x, y = random.randint(0, W), random.randint(0, H)
        r = random.randint(30, 140)
        shade = random.randint(-14, 14)
        base = 214 + shade
        d.ellipse([x - r, y - r, x + r, y + r], fill=(base, base + 6, base + 16, 22))
    img.save(out_path)


def _draw_wrapped_caption(draw, text, highlight, cy):
    font = _font(58)
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textbbox((0, 0), trial, font=font)[2] > W - 100:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    if cur:
        lines.append(cur)

    total_h = len(lines) * 72
    y = cy - total_h // 2
    for line in lines:
        words_in_line = line.split()
        widths = [draw.textbbox((0, 0), w + " ", font=font)[2] for w in words_in_line]
        line_w = sum(widths)
        x = (W - line_w) // 2
        for w, ww in zip(words_in_line, widths):
            color = ACCENT if w.strip(".,!?").upper() == highlight.upper() else (255, 255, 255, 255)
            # outline for readability
            for dx, dy in [(-3, 0), (3, 0), (0, -3), (0, 3), (-3,-3),(3,3),(-3,3),(3,-3)]:
                draw.text((x + dx, y + dy), w, font=font, fill=(0, 0, 0, 255))
            draw.text((x, y), w, font=font, fill=color)
            x += ww
        y += 72


def render_beat_frame(background_path, boxes, visible_items, caption_frame,
                       character_path, out_path):
    img = Image.open(background_path).convert("RGBA")
    draw = ImageDraw.Draw(img)

    # inset boxes across the top, left to right in order introduced
    slot_w = 480
    start_x = (W - slot_w * len(visible_items)) // 2 if visible_items else 0
    for i, key in enumerate(visible_items):
        box = boxes[key]
        box_img = Image.open(box.image_path).convert("RGBA")
        x = start_x + i * slot_w + (slot_w - box_img.width) // 2
        img.paste(box_img, (x, 90), box_img)

    _draw_wrapped_caption(draw, caption_frame.text, caption_frame.highlighted_word, cy=H // 2 - 150)

    char_img = Image.open(character_path).convert("RGBA")
    cx = (W - char_img.width) // 2
    img.paste(char_img, (cx, H // 2 + 150), char_img)

    img.convert("RGB").save(out_path)


def render_final_video(beats, beat_audios, caption_frames, boxes,
                        visible_by_beat, character_path, out_dir, out_path) -> str:
    os.makedirs(out_dir, exist_ok=True)
    frames_dir = os.path.join(out_dir, "frames")
    os.makedirs(frames_dir, exist_ok=True)

    bg_path = os.path.join(out_dir, "background.png")
    _make_background(bg_path)

    audio_by_index = {a.beat_index: a for a in beat_audios}
    concat_list = os.path.join(out_dir, "frames.txt")
    with open(concat_list, "w") as f:
        for beat, cap in zip(beats, caption_frames):
            frame_path = os.path.join(frames_dir, f"frame_{beat.index:03d}.png")
            render_beat_frame(bg_path, boxes, visible_by_beat[beat.index], cap,
                               character_path, frame_path)
            dur = audio_by_index[beat.index].duration_sec
            f.write(f"file '{frame_path}'\nduration {dur:.3f}\n")
        f.write(f"file '{frame_path}'\n")  # ffmpeg concat quirk: repeat last frame

    silent_video = os.path.join(out_dir, "video_noaudio.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list,
        "-vsync", "vfr", "-pix_fmt", "yuv420p", silent_video
    ], check=True, capture_output=True)

    # concat audio
    audio_concat_list = os.path.join(out_dir, "audio.txt")
    with open(audio_concat_list, "w") as f:
        for beat in beats:
            f.write(f"file '{audio_by_index[beat.index].wav_path}'\n")
    full_audio = os.path.join(out_dir, "full_audio.wav")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", audio_concat_list,
        full_audio
    ], check=True, capture_output=True)

    subprocess.run([
        "ffmpeg", "-y", "-i", silent_video, "-i", full_audio,
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-shortest", out_path
    ], check=True, capture_output=True)

    return out_path
