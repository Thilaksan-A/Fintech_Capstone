from celery import shared_task
from app.services.sentiment.sentiment_analysis import (
    process_crypto_sentiment_analysis,
)
from app.services.sentiment import (
    collect_reddit_crypto_discussions,
    collect_crypto_news,
    collect_youtube_crypto_comments,
)

import logging

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    name='sentiment.collect_reddit_crypto_discussions_task',
)
def collect_reddit_crypto_discussions_task(self):
    """Collect Reddit crypto discussions."""
    try:
        subreddits = ["CryptoCurrency"]
        time_range = "day"
        max_workers = 10
        collect_reddit_crypto_discussions(subreddits, time_range, max_workers)
    except Exception as exc:
        logger.error(f"Error collecting Reddit discussions: {exc}")
        raise self.retry(exc=exc, countdown=60, max_retries=3)


@shared_task(bind=True, name='sentiment.collect_crypto_youtube_comment_task')
def collect_youtube_crypto_comments_task(self):
    """Collect YouTube crypto comments."""
    try:
        video_query = "crypto|crypto news|top crypto"
        max_videos_search = 50
        max_comments_search = 100
        collect_youtube_crypto_comments(
            video_query,
            max_videos_search,
            max_comments_search,
        )
    except Exception as exc:
        logger.error(f"Error collecting YouTube comments: {exc}")
        raise self.retry(exc=exc, countdown=60, max_retries=3)


@shared_task(
    bind=True,
    name='sentiment.process_crypto_sentiment_analysis_task',
)
def process_crypto_sentiment_analysis_task(self):
    """Process crypto sentiment analysis."""
    try:
        process_crypto_sentiment_analysis(days_to_fetch=7)
    except Exception as exc:
        logger.error(f"Error processing sentiment analysis: {exc}")
        raise self.retry(exc=exc, countdown=60, max_retries=3)


@shared_task(bind=True, name='sentiment.collect_crypto_news_task')
def collect_crypto_news_task(self):
    """Collect crypto news."""
    try:
        collect_crypto_news()
    except Exception as exc:
        logger.error(f"Error collecting crypto news: {exc}")
        raise self.retry(exc=exc, countdown=60, max_retries=3)
