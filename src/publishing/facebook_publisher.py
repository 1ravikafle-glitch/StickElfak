"""
facebook_publisher.py — Facebook Page video upload via the Graph API
(POST /{page-id}/videos). Requires a Page Access Token (long-lived) tied
to a Facebook App with the pages_manage_posts + pages_read_engagement
permissions. See README.md > "Getting API access".

Contract:
    def publish(video_path: str, title: str, description: str,
                page_id: str, page_access_token: str) -> PublishResult

Notes:
    - Vertical video is posted as a Reel-eligible video automatically by
      Meta when aspect ratio + duration qualify; no separate "Reels" call
      needed for a Page in v1.
    - Long-lived Page tokens expire (~60 days) unless refreshed — job_runner
      should surface a clear "token expired" error rather than retry-loop.
"""

from dataclasses import dataclass


@dataclass
class PublishResult:
    platform: str
    success: bool
    remote_id: str | None = None
    error: str | None = None


def publish(video_path: str, title: str, description: str,
            page_id: str, page_access_token: str) -> PublishResult:
    raise NotImplementedError
