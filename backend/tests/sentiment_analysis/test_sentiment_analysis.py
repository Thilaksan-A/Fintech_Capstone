import pytest
from unittest.mock import patch
from app.models.crypto import (
    CryptoSentimentAggregateData,
    CryptoCoingeckoSentimentData,
)
from app.services.sentiment.sentiment_analysis import (
    analyse_and_store_sentiment,
    fetch_sentiment_data,
    SocialDataPoint,
)
from tests.factories.youtube import (
    YoutubeCommentFactory,
    YoutubeCommentAnalysisFactory,
)
from datetime import datetime, timedelta
from tests.factories.crypto import (
    CryptoAssetFactory,
    CryptoSourceFactory,
    CryptoMarketDataFactory,
)
from tests.factories.reddit import CryptoRedditDataFactory
from tests.factories.news import CryptoNewsDataFactory
from tests.factories.coingecko import CryptoCoingeckoSentimentDataFactory


@pytest.fixture(scope="function")
def init_sentiment(app):
    with app.app_context():
        crypto = CryptoAssetFactory(
            symbol="BTC",
            name="bitcoin",
            ranking=1,
            coingecko_id="bitcoin",
        )
        crypto2 = CryptoAssetFactory(
            symbol="ETH",
            name="ethereum",
            ranking=2,
            coingecko_id="ethereum",
        )
        source_binance = CryptoSourceFactory(name="Binance")
        CryptoMarketDataFactory(
            asset=crypto,
            source=source_binance,
        )
        CryptoMarketDataFactory(
            asset=crypto2,
            source=source_binance,
        )
        # Pre-populate youtube social data
        comment = YoutubeCommentFactory(
            comment_id="comment_1",
            text_original="Bitcoin is horrible",
            published_at=datetime.now(),
        )
        YoutubeCommentAnalysisFactory(
            comment=comment,
            crypto_asset=crypto,
            confidence_score=1,
            relevance_score=1,
            quality_score=0.8,
            analysed_at=datetime.now(),
        )
        # Pre-populate reddit social data
        reddit_source = CryptoSourceFactory(
            name="reddit",
            type="social",
        )
        CryptoRedditDataFactory(
            symbol="ETH",
            source_id=reddit_source.id,
            text="I think eth is just neat :)",
        )
        # Prepopulate news data
        CryptoNewsDataFactory(symbol="BTC")
        # Prepopulate coingecko aggregate data
        CryptoCoingeckoSentimentDataFactory(
            symbol="BTC",
        )
        CryptoCoingeckoSentimentDataFactory(
            symbol="ETH",
        )
        yield


def test_sentiment_analysis_fetch_data(init_sentiment):
    earliest = datetime.today() - timedelta(days=2)
    coingecko_aggregates, social_data = fetch_sentiment_data(earliest)
    assert len(coingecko_aggregates) == 2
    assert len(social_data) == 3


@patch("app.services.sentiment.sentiment_analysis.fetch_sentiment_data")
def test_sentiment_analysis_no_data_fetched(mock_fetch_data, init_sentiment):
    mock_fetch_data.return_value = ([], [])
    analyse_and_store_sentiment(2)
    mock_fetch_data.assert_called_once()
    sentiment_result = CryptoSentimentAggregateData.query.order_by(
        CryptoSentimentAggregateData.symbol,
    ).all()
    assert len(sentiment_result) == 0


@patch("app.services.sentiment.sentiment_analysis.fetch_sentiment_data")
def test_sentiment_analysis_analyse_data(mock_fetch_data, init_sentiment):
    mock_fetch_data.return_value = (
        [
            CryptoCoingeckoSentimentData(
                symbol="BTC",
                sentiment_up_percentage=50,
                sentiment_down_percentage=50,
                reddit_average_posts_48h=0,
                commit_count_4_weeks=1,
                timestamp=datetime.now(),
            ),
        ],
        [
            SocialDataPoint(
                symbol="BTC",
                text="I love BTC!",
                confidence=1.0,
            ),
        ],
    )
    analyse_and_store_sentiment(2)
    mock_fetch_data.assert_called_once()
    btc_sentiment = CryptoSentimentAggregateData.query.first()
    assert btc_sentiment is not None
    assert btc_sentiment.normalised_up_percentage > 0.5
    assert btc_sentiment.normalised_down_percentage < 0.5
    assert btc_sentiment.avg_positive_sentiment > 0


@patch("app.services.sentiment.sentiment_analysis.analyse_sentiment_data")
def test_sentiment_analysis_write_to_db(mock_analyse_data, init_sentiment):
    res = CryptoSentimentAggregateData(
        symbol="BTC",
        normalised_up_percentage=0.89,
        normalised_down_percentage=0.11,
        avg_positive_sentiment=0.734,
        avg_neutral_sentiment=0.08,
        avg_negative_sentiment=0.124,
        avg_compound_sentiment=0.287,
    )
    mock_analyse_data.return_value = [res]
    analyse_and_store_sentiment(2)
    mock_analyse_data.assert_called_once()
    sentiment_result = CryptoSentimentAggregateData.query.all()
    assert len(sentiment_result) == 1
    assert (
        sentiment_result[0].normalised_up_percentage
        == res.normalised_up_percentage
    )
    assert (
        sentiment_result[0].normalised_down_percentage
        == res.normalised_down_percentage
    )
    assert (
        sentiment_result[0].avg_positive_sentiment
        == res.avg_positive_sentiment
    )
    assert (
        sentiment_result[0].avg_compound_sentiment
        == res.avg_compound_sentiment
    )


def test_sentiment_analyser_end_to_end(init_sentiment):
    analyse_and_store_sentiment(2)
    sentiment_result = CryptoSentimentAggregateData.query.order_by(
        CryptoSentimentAggregateData.symbol,
    ).all()
    assert len(sentiment_result) == 2
    assert sentiment_result[0].symbol == "BTC"
    assert sentiment_result[0].normalised_up_percentage != 0
    assert sentiment_result[0].normalised_up_percentage != 0.5
    assert sentiment_result[0].normalised_down_percentage != 0
    assert sentiment_result[1].symbol == "ETH"
    assert sentiment_result[1].normalised_up_percentage != 0
    assert sentiment_result[1].normalised_up_percentage != 0.5
    assert sentiment_result[1].normalised_down_percentage != 0
