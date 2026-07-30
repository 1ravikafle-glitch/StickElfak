"""
job_runner.py — orchestrates script_parser -> tts_engine -> caption_sync +
visual_selector + avatar_renderer -> compositor, for one comparison-style
video job. Publishing is wired separately via publish_manager.
"""

import os
import uuid
from dataclasses import dataclass

from src.pipeline.script_parser import parse_script
from src.pipeline.tts_engine import synthesize
from src.pipeline.caption_sync import build_caption_track
from src.pipeline.visual_selector import select_visuals
from src.pipeline.avatar_renderer import render_avatar_track
from src.pipeline.compositor import render_final_video

JOBS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "jobs")


@dataclass
class JobResult:
    job_id: str
    video_path: str
    publish_results: dict = None


def run_job(topic: str, script_text: str, item_a: str = "", item_b: str = "",
            voice: str = "default") -> JobResult:
    job_id = uuid.uuid4().hex[:10]
    job_dir = os.path.join(JOBS_DIR, job_id)
    os.makedirs(job_dir, exist_ok=True)

    beats = parse_script(topic, script_text, item_a, item_b)
    if not beats:
        raise ValueError("Script produced no beats — check your script text.")

    audio_result = synthesize(beats, voice, os.path.join(job_dir, "audio"))
    caption_frames = build_caption_track(beats, audio_result.beat_audios)
    visuals = select_visuals(beats, item_a, item_b, os.path.join(job_dir, "visuals"))
    character_path = render_avatar_track(os.path.join(job_dir, "character"))

    out_path = os.path.join(job_dir, "output.mp4")
    render_final_video(beats, audio_result.beat_audios, caption_frames,
                        visuals["boxes"], visuals["visible_by_beat"],
                        character_path, job_dir, out_path)

    return JobResult(job_id=job_id, video_path=out_path)
