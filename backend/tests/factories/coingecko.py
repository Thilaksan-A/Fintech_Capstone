import factory
from datetime import datetime, timezone
from app.models.crypto import CryptoCoingeckoSentimentData
from tests.factories import BaseFactory


class CryptoCoingeckoSentimentDataFactory(BaseFactory):
    class Meta:
        model = CryptoCoingeckoSentimentData

    symbol = "BTC"
    sentiment_up_percentage = 60
    sentiment_down_percentage = 40
    reddit_average_posts_48h = 29
    commit_count_4_weeks = 12
    timestamp = factory.LazyFunction(lambda: datetime.now(timezone.utc))
