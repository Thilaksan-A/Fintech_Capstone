from datetime import datetime

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from app.models.youtube import YoutubeComment, YoutubeCommentAnalysis
from app.extensions import db
from app.utils.decorators import transactional
from app.schemas.youtube_schema import YoutubeVideoInfo
from .youtube_client import (
    build_youtube_client,
    search_youtube_videos,
    get_video_comments,
)
from .youtube_filter import sanitise_comments

import logging
import json

logger = logging.getLogger(__name__)


def collect_youtube_crypto_comments(
    video_query: str,
    max_videos_search: int,
    max_comments_search: int,
    ranking: int = 50,
) -> None:
    """
    Run YouTube data ingestion. This function is used in cron jobs.
    """
    logger.info("YouTube data ingestion started.")

    youtube = build_youtube_client()
    if not youtube:
        return

    youtube_video_infos = search_youtube_videos(
        youtube,
        query=video_query,
        max_results=max_videos_search,
    )

    if not youtube_video_infos:
        logger.info("No videos found.")
        return

    for youtube_video_info in youtube_video_infos:
        logger.info(
            f"Processing comments for video {youtube_video_info.video_id} - "
            f"{youtube_video_info.title}",
        )

        comments = get_video_comments(
            youtube,
            video_id=youtube_video_info.video_id,
            max_results=max_comments_search,
        )
        if not comments:
            logger.info(
                f"No comments found for video {youtube_video_info.video_id}.",
            )
            continue

        filtered_comments = sanitise_comments(comments, ranking)
        if not filtered_comments:
            logger.info(
                f"No valid comments found for video {youtube_video_info.video_id}.",
            )
            continue

        logger.info(
            f"Storing {len(filtered_comments)} valid comments for "
            f"video {youtube_video_info.video_id}.",
        )

        _store_comments_and_analysis(filtered_comments, youtube_video_info)


@transactional
def _store_comments_and_analysis(
    filtered_comments: list[YoutubeComment],
    youtube_video_info: YoutubeVideoInfo,
):
    """Store comments and analysis in a separate transaction."""
    if not filtered_comments:
        return

    # Batch check for existing comments using new select syntax
    comment_ids = [comment.comment_id for comment in filtered_comments]
    existing_comment_ids = set(
        db.session.scalars(
            select(YoutubeComment.comment_id).filter(
                YoutubeComment.comment_id.in_(comment_ids),
            ),
        ).all(),
    )

    # Prepare data for new comments only
    new_comments = []
    new_analyses = []
    skipped_count = 0
    current_time = datetime.now().astimezone()

    for comment in filtered_comments:
        if comment.comment_id in existing_comment_ids:
            skipped_count += 1
            continue

        # Prepare comment data
        comment_data = {
            'comment_id': comment.comment_id,
            'video_id': comment.video_id,
            'video_title': youtube_video_info.title,
            'text_original': comment.text,
            'like_count': comment.like_count,
            'total_reply_count': comment.reply_count,
            'published_at': comment.published_at,
            'updated_at': comment.updated_at,
            'raw_response': json.dumps(comment.raw_response),
        }
        new_comments.append(comment_data)

        # Prepare analysis data for each crypto mention
        for crypto_symbol in comment.crypto_mentions:
            new_analyses.append(
                {
                    'comment_id': comment.comment_id,
                    'crypto_symbol': crypto_symbol,
                    'confidence_score': 0.0,
                    'timestamp': current_time,
                },
            )

    # Bulk insert new comments
    if new_comments:
        stmt = insert(YoutubeComment).values(new_comments)
        db.session.execute(stmt)
        logger.info(
            f"Inserted {len(new_comments)} new comments, "
            f"skipped {skipped_count} existing comments.",
        )

    # Bulk insert analyses with ON CONFLICT for TimescaleDB
    if new_analyses:
        stmt = insert(YoutubeCommentAnalysis).values(new_analyses)
        stmt = stmt.on_conflict_do_nothing(
            index_elements=['comment_id', 'crypto_symbol', 'timestamp'],
        )
        db.session.execute(stmt)
        logger.info(f"Inserted {len(new_analyses)} comment analyses.")
