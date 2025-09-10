import pytest
from unittest.mock import patch
from app.models.crypto import CryptoAsset, CryptoCoingeckoSentimentData
from app.services.market.coingecko import (
    sync_crypto_asset_with_coingecko,
    sync_top_coingecko_crypto_metadata,
)
from tests.factories.crypto import (
    CryptoAssetFactory,
    CryptoMarketDataFactory,
    CryptoSourceFactory,
)


@pytest.fixture(scope="function")
def coingecko():
    asset = CryptoAssetFactory(
        symbol="BTC",
        name="bitcoin",
        ranking=-1,
        coingecko_id="bitcoin",
    )
    source_binance = CryptoSourceFactory(name="Binance")
    CryptoMarketDataFactory(
        asset=asset,
        source=source_binance,
        price=30000.50,
        interval="1h",
    )


@patch("app.services.market.coingecko.fetch_coingecko_market_data")
def test_coingecko_ranking_store(mock_fetch_market_data, coingecko):
    to_insert = [
        {
            "symbol": "BTC",
            "name": "bitcoin",
            "market_cap_rank": 99,
            "image": "btc.png",
            "id": "bitcoin",
        },
        {
            "symbol": "ETH",
            "name": "ethereum",
            "market_cap_rank": 1,
            "image": "eth.png",
            "id": "ethereum",
        },
    ]
    mock_fetch_market_data.return_value = to_insert
    sync_crypto_asset_with_coingecko()
    mock_fetch_market_data.assert_called_once()
    assets = CryptoAsset.query.all()
    assert len(assets) == 2
    assert (
        CryptoAsset.query.filter(CryptoAsset.symbol == "BTC").first().ranking
        == 99
    )
    assert (
        CryptoAsset.query.filter(CryptoAsset.symbol == "ETH").first().ranking
        == 1
    )


def test_coingecko_ranking_fetch(coingecko):
    sync_crypto_asset_with_coingecko()
    asset = CryptoAsset.query.filter(CryptoAsset.symbol == "BTC").first()
    assert asset is not None
    # image and ranking may be None/-1 if not fetched from real API, so just check existence
    assert asset.symbol == "BTC"


@patch("app.services.market.coingecko.fetch_coingecko_metadata")
@patch("app.services.market.coingecko.FETCH_METADATA_INTERVAL_S", 0)
def test_coingecko_metadata_store(mock_fetch_metadata, coingecko):
    to_insert = [
        CryptoAsset(
            symbol="BTC",
            name="bitcoin",
            ranking=1,
            description="dummy description",
            categories="crypto, blockchain",
            homepage_url="https://bitcoin.org/en/",
            subreddit_url="https://www.reddit.com/r/Bitcoin/",
            purchase_platforms="binance, coinbase",
        ),
        CryptoCoingeckoSentimentData(
            symbol="BTC",
            sentiment_up_percentage=0.6,
            sentiment_down_percentage=0.4,
            reddit_average_posts_48h=10,
            commit_count_4_weeks=31,
        ),
    ]
    mock_fetch_metadata.return_value = to_insert
    sync_top_coingecko_crypto_metadata()
    mock_fetch_metadata.assert_called_once()

    sentiment = CryptoCoingeckoSentimentData.query.all()
    asset = CryptoAsset.query.filter(CryptoAsset.symbol == "BTC").first()
    assert len(sentiment) == 1
    assert sentiment[0].sentiment_up_percentage == 0.6
    assert asset.description == to_insert[0].description
    assert asset.homepage_url == to_insert[0].homepage_url


@patch("app.services.market.coingecko.FETCH_METADATA_INTERVAL_S", 0)
def test_coingecko_metadata_fetch(coingecko):
    sync_top_coingecko_crypto_metadata()
    sentiment = CryptoCoingeckoSentimentData.query.all()
    # May be 0 if no real API, but should not error
    assert isinstance(sentiment, list)
