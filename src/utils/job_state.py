"""
job_state.py — tracks per-job stage completion so a crashed/interrupted run
can resume instead of re-rendering from scratch (renders are the expensive
step on resource-constrained hardware).

Contract:
    def new_job(topic: str, script_path: str) -> str        # returns job_id
    def mark_stage_done(job_id: str, stage: str, data: dict) -> None
    def get_job_status(job_id: str) -> dict

State is stored as jobs/<job_id>/state.json — plain JSON, no database.
Stages (in order): parsed, tts, captions, visuals, avatar, rendered, published
"""


def new_job(topic: str, script_path: str) -> str:
    raise NotImplementedError


def mark_stage_done(job_id: str, stage: str, data: dict) -> None:
    raise NotImplementedError


def get_job_status(job_id: str) -> dict:
    raise NotImplementedError
