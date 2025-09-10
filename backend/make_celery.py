from app import create_app
from celery.schedules import crontab
import celery_logger  # noqa: F401

app = create_app()
celery_app = app.extensions["celery"]

# Configure the beat schedule
celery_app.conf.beat_schedule = {
    # ==============================
    # Crypto Market Tasks
    # ==============================
    # Run at 15 minutes past every hour
    'sync-binance-crypto-market-information': {
        'task': 'market.sync_binance_crypto_market_information_task',
        'schedule': crontab(minute=15, hour='*'),
    },
    # Run at 30 minutes past every 4th hour
    'sync-crypto-asset-with-coingecko': {
        'task': 'market.sync_crypto_asset_with_coingecko_task',
        'schedule': crontab(minute=30, hour='*/4'),
    },
    # Run every day at 2:45AM Australia/Sydney time
    # Requirement: Only run once per day to limit API calls
    'sync-top-coingecko-crypto-metadata': {
        'task': 'market.sync_top_coingecko_crypto_metadata_task',
        'schedule': crontab(minute=45, hour=2),
    },
    # ==============================
    # Sentiment Analysis Tasks
    # ==============================
    # Run every day at 3:15AM Australia/Sydney time
    # Requirement: Only run once per day to limit API calls
    'collect-youtube-comments': {
        'task': 'sentiment.collect_crypto_youtube_comment_task',
        'schedule': crontab(minute=15, hour=3),
    },
    # Run every day at 10:30AM Australia/Sydney time
    'collect-crypto-news': {
        'task': 'sentiment.collect_crypto_news_task',
        'schedule': crontab(minute=30, hour=10),
    },
    # Run at 45 minutes past every hour
    'collect-reddit-discussions': {
        'task': 'sentiment.collect_reddit_crypto_discussions_task',
        'schedule': crontab(minute=45, hour='*'),
    },
    # Run every day at 4:00AM Australia/Sydney time
    # Requirement: Run after the YouTube comments collection (3:15AM)
    'process-sentiment-analysis': {
        'task': 'sentiment.process_crypto_sentiment_analysis_task',
        'schedule': crontab(minute=0, hour=4),
    },
}
