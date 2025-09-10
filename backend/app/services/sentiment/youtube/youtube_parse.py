import logging
from marshmallow_dataclass import class_schema
from app.schemas.youtube_schema import YoutubeCommentInfo, YoutubeVideoInfo

logger = logging.getLogger(__name__)


def parse_youtube_video_info(item: dict) -> YoutubeVideoInfo | None:
    """
    Parse a raw YouTube video item into a YoutubeVideoInfo object.
    """

    snippet = item.get("snippet", {})
    stats = item.get("statistics", {})
    details = item.get("contentDetails", {})

    videoIdObj = item.get("id", {})

    if not videoIdObj or "videoId" not in videoIdObj:
        logger.warning(f"Skipping item without videoId: {item}")
        return None

    flattened_video_item = {
        "etag": item.get("etag", ""),
        "video_id": item["id"]["videoId"],
        "title": snippet.get("title", ""),
        "channel": snippet.get("channelTitle", ""),
        "published_at": snippet.get("publishedAt", ""),
        "description": snippet.get("description", ""),
        "channel_id": snippet.get("channelId", ""),
        "view_count": int(stats.get("viewCount"))
        if stats.get("viewCount")
        else None,
        "duration": details.get("duration"),
    }

    schema = class_schema(YoutubeVideoInfo)
    try:
        video_info = schema().load(flattened_video_item)
        return video_info
    except Exception as e:
        logger.error(f"Error parsing video item: {e}")
        raise ValueError(f"Invalid video item: {item}") from e


def parse_youtube_comment_info(item: dict) -> YoutubeCommentInfo | None:
    """
    Parse a raw YouTube comment item into a YoutubeCommentInfo object.
    """

    snippet = item.get("snippet", {})
    top_level_comment = snippet.get("topLevelComment", {})
    replies = item.get("replies", {})

    flattened_comment_item = {
        "comment_id": item.get("id", ""),
        "video_id": snippet.get("videoId", ""),
        "text": top_level_comment.get("snippet", {}).get("textDisplay", ""),
        "author": top_level_comment.get("snippet", {}).get(
            "authorDisplayName",
            "",
        ),
        "like_count": int(
            top_level_comment.get("snippet", {}).get("likeCount", 0),
        ),
        "published_at": top_level_comment.get("snippet", {}).get(
            "publishedAt",
            "",
        ),
        "updated_at": top_level_comment.get("snippet", {}).get(
            "updatedAt",
            "",
        ),
        "reply_count": replies.get("totalReplyCount", 0),
        "channel_id": snippet.get("channelId", ""),
        "author_channel_id": top_level_comment.get("snippet", {})
        .get("authorChannelId", {})
        .get("value"),
        "raw_response": item,
    }

    schema = class_schema(YoutubeCommentInfo)
    try:
        comment_info = schema().load(flattened_comment_item)
        return comment_info
    except Exception as e:
        logger.error(f"Error parsing comment item: {e}")
        raise ValueError(f"Invalid comment item: {item}") from e
