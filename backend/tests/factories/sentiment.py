import factory
from app.models.crypto import CryptoSentimentAggregateData
from tests.factories import BaseFactory
from datetime import datetime, timezone, timedelta


class CryptoSentimentAggregateDataFactory(BaseFactory):
    class Meta:
        model = CryptoSentimentAggregateData

    symbol = factory.Faker("word", ext_word_list=['BTC', 'ETH', 'XRP', 'LTC'])
    normalised_up_percentage = factory.Faker(
        "pyfloat",
        left_digits=0,
        right_digits=4,
        positive=True,
    )
    normalised_down_percentage = factory.Faker(
        "pyfloat",
        left_digits=0,
        right_digits=4,
        positive=True,
    )
    avg_positive_sentiment = factory.Faker(
        "pyfloat",
        left_digits=0,
        right_digits=4,
        positive=True,
    )
    avg_neutral_sentiment = factory.Faker(
        "pyfloat",
        left_digits=0,
        right_digits=4,
        positive=True,
    )
    avg_negative_sentiment = factory.Faker(
        "pyfloat",
        left_digits=0,
        right_digits=4,
        positive=True,
    )
    avg_compound_sentiment = factory.Faker(
        "pyfloat",
        left_digits=0,
        right_digits=4,
    )

    earliest_post = factory.LazyFunction(
        lambda: datetime.now(timezone.utc) - timedelta(days=1),
    )
    timestamp = factory.LazyFunction(lambda: datetime.now(timezone.utc))
