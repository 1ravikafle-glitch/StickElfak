"""
publish_manager.py — the ONLY module job_runner talks to for publishing.
Fans out to youtube_publisher / facebook_publisher / tiktok_publisher,
one platform's failure must never block the others.

Contract:
    def publish_all(video_path: str, title: str, description: str,
                     tags: list[str], platforms: list[str],
                     credentials_dir: str) -> dict  # platform -> PublishResult

Each publisher is called in its own try/except; a per-platform failure is
recorded in the result dict, not raised. job_runner logs and surfaces the
dict as-is to the caller/CLI.
"""


def publish_all(video_path: str, title: str, description: str, tags: list,
                 platforms: list, credentials_dir: str) -> dict:
    raise NotImplementedError
