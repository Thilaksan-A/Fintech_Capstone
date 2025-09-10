import pytest
from app.services.sentiment.youtube.youtube_parse import (
    parse_youtube_comment_info,
    parse_youtube_video_info,
)


def test_parse_youtube_video_info_valid():
    item = {
        "etag": "etag123",
        "id": {"videoId": "abc123"},
        "snippet": {
            "title": "Test Video",
            "channelTitle": "Test Channel",
            "publishedAt": "2025-07-28T12:00:00Z",
            "description": "A test video.",
            "channelId": "chan123",
        },
        "statistics": {"viewCount": "100"},
        "contentDetails": {"duration": "PT5M"},
    }
    video_info = parse_youtube_video_info(item)
    assert video_info.video_id == "abc123"
    assert video_info.title == "Test Video"
    assert video_info.channel == "Test Channel"
    assert video_info.view_count == 100
    assert video_info.duration == "PT5M"


def test_parse_youtube_video_info_missing_video_id():
    item = {
        "etag": "etag123",
        "id": {},
        "snippet": {},
        "statistics": {},
        "contentDetails": {},
    }
    assert parse_youtube_video_info(item) is None


def test_parse_youtube_comment_info_valid():
    item = {
        "id": "comment123",
        "snippet": {
            "videoId": "abc123",
            "channelId": "chan123",
            "topLevelComment": {
                "snippet": {
                    "textDisplay": "Nice video!",
                    "authorDisplayName": "Alice",
                    "likeCount": 5,
                    "publishedAt": "2025-07-28T12:00:00Z",
                    "updatedAt": "2025-07-28T12:01:00Z",
                    "authorChannelId": {"value": "authorChan123"},
                },
            },
        },
        "replies": {"totalReplyCount": 2},
    }
    comment_info = parse_youtube_comment_info(item)
    assert comment_info.comment_id == "comment123"
    assert comment_info.video_id == "abc123"
    assert comment_info.text == "Nice video!"
    assert comment_info.author == "Alice"
    assert comment_info.like_count == 5
    assert comment_info.reply_count == 2
    assert comment_info.author_channel_id == "authorChan123"


def test_parse_youtube_comment_info_missing_fields():
    item = {
        "id": "comment123",
        "snippet": {},
        "replies": {},
    }
    with pytest.raises(ValueError):
        comment_info = parse_youtube_comment_info(item)
        assert comment_info is None
