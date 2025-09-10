from dataclasses import field
from datetime import datetime
from typing import List, Optional
from marshmallow_dataclass import dataclass


@dataclass
class YoutubeVideoInfo:
    etag: str
    video_id: str
    title: str
    channel: str
    published_at: datetime
    description: str
    channel_id: str
    view_count: Optional[int] = None
    duration: Optional[str] = None


@dataclass
class YoutubeCommentInfo:
    comment_id: str
    video_id: str
    text: str
    author: str
    published_at: datetime
    updated_at: datetime
    reply_count: int
    like_count: Optional[int] = 0
    channel_id: Optional[str] = ""
    author_channel_id: Optional[str] = None
    bot_score: Optional[float] = 0.0
    crypto_mentions: List[str] = field(default_factory=list)
    raw_response: Optional[dict] = None
