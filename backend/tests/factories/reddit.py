import factory
from datetime import datetime, timezone
from app.models.crypto import CryptoRedditData
from tests.factories import BaseFactory


class CryptoRedditDataFactory(BaseFactory):
    class Meta:
        model = CryptoRedditData

    symbol = "BTC"
    source_id = factory.SelfAttribute("source.id")
    subreddit = "cryptocurrency"
    text = "I hate BTC"
    votes = 0
    confidence = 1.0
    timestamp = factory.LazyFunction(lambda: datetime.now(timezone.utc))
