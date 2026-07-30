"""
caption_sync.py — pairs each Beat's caption/highlight with its timing
(start/end seconds), derived from the TTS stage's per-beat durations.
Produces data only; compositor.py draws it.
"""

from dataclasses import dataclass


@dataclass
class CaptionFrame:
    beat_index: int
    start_sec: float
    end_sec: float
    text: str
    highlighted_word: str


def build_caption_track(beats, beat_audios) -> list:
    frames = []
    t = 0.0
    audio_by_index = {a.beat_index: a for a in beat_audios}
    for beat in beats:
        dur = audio_by_index[beat.index].duration_sec
        frames.append(CaptionFrame(
            beat_index=beat.index,
            start_sec=t,
            end_sec=t + dur,
            text=beat.caption,
            highlighted_word=beat.highlight_word,
        ))
        t += dur
    return frames
