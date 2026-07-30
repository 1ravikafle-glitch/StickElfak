"""
youtube_publisher.py — YouTube Shorts upload via the official YouTube Data
API v3 (resumable upload, videos.insert). OAuth2 credentials only — see
README.md > "Getting API access" for how to obtain client_secret.json and
generate a refresh token once.

Contract:
    def publish(video_path: str, title: str, description: str,
                tags: list[str], credentials_path: str) -> PublishResult

    class PublishResult:
        platform: str = "youtube"
        success: bool
        remote_id: str | None      # YouTube video ID if success
        error: str | None

Notes:
    - Shorts eligibility: vertical video, <= 3 min, and #Shorts in title or
      description helps surface it in the Shorts shelf.
    - Daily upload quota is limited on new API projects — job_runner should
      treat a quota error as retry-next-day, not a hard failure.
"""

from dataclasses import dataclass


@dataclass
class PublishResult:
    platform: str
    success: bool
    remote_id: str | None = None
    error: str | None = None


def publish(video_path: str, title: str, description: str, tags: list,
            credentials_path: str) -> PublishResult:
    raise NotImplementedError
