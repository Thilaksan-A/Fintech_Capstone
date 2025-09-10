from app.models.crypto import CryptoSentimentAggregateData
from tests.factories.sentiment import CryptoSentimentAggregateDataFactory
from tests.factories.crypto import CryptoAssetFactory, CryptoSourceFactory


def test_sentiment_aggregate_model():
    CryptoAssetFactory(symbol="BTC", name="bitcoin")

    CryptoSentimentAggregateDataFactory(
        symbol="BTC",
        normalised_up_percentage=0.89,
        normalised_down_percentage=0.11,
        avg_positive_sentiment=0.734,
        avg_neutral_sentiment=0.08,
        avg_negative_sentiment=0.124,
        avg_compound_sentiment=0.287,
    )

    fetched = CryptoSentimentAggregateData.query.all()
    assert len(fetched) == 1
    assert fetched[0].normalised_up_percentage == 0.89
    assert fetched[0].avg_positive_sentiment == 0.734
    assert fetched[0].avg_negative_sentiment == 0.124
    assert fetched[0].avg_compound_sentiment == 0.287
