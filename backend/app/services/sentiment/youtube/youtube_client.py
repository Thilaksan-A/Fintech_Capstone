from datetime import datetime, timedelta
from typing import Generator
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError

from app.env import YOUTUBE_API_KEY
from app.schemas.youtube_schema import YoutubeCommentInfo, YoutubeVideoInfo
from app.services.sentiment.youtube.youtube_parse import (
    parse_youtube_comment_info,
    parse_youtube_video_info,
)

import logging

logger = logging.getLogger(__name__)

DEFAULT_LOOKBACK_DAYS = 2


def build_youtube_client() -> Resource | None:
    """
    Build a YouTube client.
    """

    SERVICE_NAME = "youtube"
    SERVICE_VERSION = "v3"
    try:
        youtube = build(
            SERVICE_NAME,
            SERVICE_VERSION,
            developerKey=YOUTUBE_API_KEY,
        )
        return youtube
    except Exception:
        logger.error(
            "YouTube client could not be created. Check your API key.",
        )
        return None


def search_youtube_videos(
    youtube: Resource,
    query: str,
    max_results: int,
) -> Generator[YoutubeVideoInfo, None, None]:
    """
    Search for YouTube videos by keyword using a generator.

    Yields: VideoInfo objects one at a time
    """

    logger.info(f"Searching YouTube for videos with query: {query}")
    try:
        # Handle pagination
        next_page_token = None
        videos_yielded = 0
        prev_etag = None

        while videos_yielded < max_results:
            if max_results > 50:
                logger.warning("YouTube API limits batch size to 50 results.")
            batch_size = min(
                50,
                max_results - videos_yielded,
            )  # YouTube API max is 50

            delta_day = datetime.now() - timedelta(days=DEFAULT_LOOKBACK_DAYS)

            request = youtube.search().list(
                q=query,
                part="id,snippet",
                maxResults=batch_size,
                type="video",
                pageToken=next_page_token,
                order="viewCount",
                publishedAfter=delta_day.strftime('%Y-%m-%dT%H:%M:%SZ'),
                relevanceLanguage="en",
                regionCode="US",
            )
            response = request.execute()

            if (
                next_page_token
                and prev_etag
                and response.get('etag') == prev_etag
            ):
                logger.error(
                    f"Possible pagination error: nextPageToken '{next_page_token}' "
                    f"unchanged and etag '{response.get('etag')}' matches previous "
                    f"etag '{prev_etag}'",
                )
                raise ValueError(
                    "Pagination error: nextPageToken or etag did not change",
                )

            # Process each video in the response
            items = response.get("items", [])
            for item in items:
                youtube_video_info = parse_youtube_video_info(item)
                if youtube_video_info:
                    yield youtube_video_info
                    prev_etag = youtube_video_info.etag
                    videos_yielded += 1
                else:
                    prev_etag = None
            # Check if there are more pages
            next_page_token = response.get("nextPageToken")
            if not next_page_token or videos_yielded >= max_results:
                break

        logger.info(f"Found {videos_yielded} videos for query '{query}'")

    except HttpError as e:
        if e.resp.status == 403:
            logger.warning("Quota exceeded or API key invalid.")
        else:
            logger.error(f"YouTube API error: {e}")
        return
    except Exception as e:
        logger.error(f"Error searching videos: {e}")
        return


def get_video_comments(
    youtube: Resource,
    video_id: str,
    max_results: int = 100,
) -> Generator[YoutubeCommentInfo, None, None]:
    """Yield all comments as a generator for batch processing."""
    try:

        comments_yield_num = 0
        next_page_token = None

        while comments_yield_num < max_results:  # pagination
            batch_size = min(100, max_results - comments_yield_num)

            request = youtube.commentThreads().list(
                part="snippet,replies",
                videoId=video_id,
                maxResults=batch_size,
                pageToken=next_page_token,
            )
            response = request.execute()

            for item in response.get("items", []):
                if comments_yield_num >= max_results:
                    break

                try:
                    comment_info = parse_youtube_comment_info(item)

                    # Skip channel owner comments
                    if (
                        comment_info.channel_id
                        == comment_info.author_channel_id
                    ):
                        logger.info(
                            "Skipping channel owner comment: "
                            f"{comment_info.text[:20]}",
                        )
                        continue
                    yield comment_info
                    comments_yield_num += 1
                except Exception as e:
                    logger.error(f"Error parsing comment: {e}")
                    continue

            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break

    except HttpError as e:
        if e.resp.status == 403:
            logger.warning(
                f"Comments disabled for video {video_id} or quota exceeded",
            )
        else:
            logger.error(f"YouTube API error: {e}")
        return
    except Exception as e:
        logger.error(f"Error getting comments: {e}")
        return
