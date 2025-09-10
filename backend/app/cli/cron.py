import click
from flask.cli import with_appcontext
from app.services.market import (
    sync_crypto_asset_with_coingecko,
    sync_top_coingecko_crypto_metadata,
    sync_binance_crypto_market_information,
)
from app.services.sentiment import (
    collect_youtube_crypto_comments,
    process_crypto_sentiment_analysis,
    collect_crypto_news,
    collect_reddit_crypto_discussions,
)

import logging

logger = logging.getLogger(__name__)


@click.group()
def cron():
    """Cron job commands."""
    pass


@cron.command("ingest-market")
@with_appcontext
def sync_binance_crypto_market_information_command():
    sync_binance_crypto_market_information()


@cron.command("reddit-sentiment-ingest")
@click.option(
    "--subreddits",
    default="CryptoCurrency",
    help="Comma-separated list of subreddits to collect discussions from.",
)
@click.option(
    "--time-range",
    default="day",
    help="Time range for Reddit discussions (e.g., hour, day, week).",
)
@click.option(
    "--max-workers",
    default=10,
    help="Maximum number of concurrent workers for Reddit data collection.",
)
@with_appcontext
def collect_reddit_crypto_discussions_command(
    subreddits: str = "CryptoCurrency",
    time_range: str = "day",
    max_workers: int = 10,
):
    collect_reddit_crypto_discussions(
        subreddits=subreddits.split(","),
        time_range=time_range,
        max_workers=max_workers,
    )


@cron.command("run-sentiment-analysis")
@with_appcontext
def process_crypto_sentiment_analysis_command():
    process_crypto_sentiment_analysis()


@cron.command("sync-crypto-asset")
@with_appcontext
def sync_crypto_asset_with_coingecko_command():
    sync_crypto_asset_with_coingecko()


# ** Only run once per day to limit API calls!!! **
@cron.command("sync-top-coingecko-crypto-metadata")
@with_appcontext
def sync_top_coingecko_crypto_metadata_command():
    sync_top_coingecko_crypto_metadata()


@cron.command("ingest-news-data")
@with_appcontext
def collect_crypto_news_command():
    collect_crypto_news()


@cron.command("collect-crypto-youtube-comments")
@click.option(
    "--video-query",
    prompt="Video query",
    help="Search query for YouTube videos.",
)
@click.option(
    "--max-videos-search",
    default=5,
    help="Maximum number of videos to fetch.",
)
@click.option(
    "--max-comments-search",
    default=100,
    help="Maximum number of comments to fetch per video.",
)
@click.option(
    "--top-ranking-crypto",
    default=50,
    help="Top ranking for crypto assets.",
)
@with_appcontext
def collect_crypto_youtube_comments_command(
    video_query: str,
    max_videos_search: int,
    max_comments_search: int,
    top_ranking_crypto: int = 50,
):
    """Run YouTube data ingestion."""
    logger.info(
        "YouTube data ingestion started with: ["
        f"query: \"{video_query}\", "
        f"max_videos_search: {max_videos_search}, "
        f"max_comments_search: {max_comments_search}, "
        f"top_ranking_crypto: {top_ranking_crypto}]",
    )
    collect_youtube_crypto_comments(
        video_query,
        max_videos_search=max_videos_search,
        max_comments_search=max_comments_search,
        ranking=top_ranking_crypto,
    )
