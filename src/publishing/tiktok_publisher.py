"""
tiktok_publisher.py — TikTok upload via the official Content Posting API.

IMPORTANT (v1 scope note, see README.md > "Getting API access"):
    A newly-created TikTok developer app starts in "unaudited" mode, which
    restricts direct public posting — unaudited apps can only push videos
    to the target account as a private/draft post (or the user must open
    the TikTok app to complete posting), until TikTok reviews and approves
    the app for direct public posting. Design job_runner and the README to
    treat "posted as draft, needs manual publish in-app" as the default
    successful outcome for TikTok until the app is approved — do not treat
    it as a failure.

Contract:
    def publish(video_path: str, title: str, access_token: str) -> PublishResult

    PublishResult.remote_id may be a draft/publish-id rather than a live
    public post id, depending on app audit status.
"""

from dataclasses import dataclass


@dataclass
class PublishResult:
    platform: str
    success: bool
    remote_id: str | None = None
    error: str | None = None


def publish(video_path: str, title: str, access_token: str) -> PublishResult:
    raise NotImplementedError
