import pytest
from app.models.crypto import (
    CryptoAsset,
    CryptoSource,
    CryptoMarketData,
    CryptoTechnicalIndicator,
)
from tests.factories.crypto import (
    CryptoAssetFactory,
    CryptoMarketDataFactory,
    CryptoSourceFactory,
    CryptoTechnicalIndicatorFactory,
)
from datetime import datetime


def test_crypto_asset_creation(session):
    asset = CryptoAssetFactory(symbol="ETH", name="Ethereum", ranking=1)

    fetched = session.query(CryptoAsset).filter_by(symbol="ETH").first()
    assert fetched is not None
    assert fetched.name == "Ethereum"
    assert fetched.ranking == 1


def test_crypto_source_creation(session):
    source = CryptoSourceFactory(name="CoinGecko", type="aggregated")

    fetched = session.query(CryptoSource).filter_by(name="CoinGecko").first()
    assert fetched is not None
    assert fetched.type == "aggregated"


def test_crypto_market_data_creation(session, subtests):
    asset = CryptoAssetFactory(symbol="BTC")
    source_binance = CryptoSourceFactory(name="Binance")

    # First data point (no market cap, no volume)
    data1 = CryptoMarketDataFactory(
        asset=asset,
        source=source_binance,
        price=30000.50,
        interval="1h",
    )

    with subtests.test("Basic Binance Market Data"):
        fetched = (
            session.query(CryptoMarketData)
            .filter_by(source_id=source_binance.id, symbol=asset.symbol)
            .first()
        )
        assert fetched is not None
        assert fetched.asset.symbol == "BTC"
        assert fetched.source.name == "Binance"
        assert float(fetched.price) == 30000.50
        assert fetched.interval == "1h"
        assert fetched.market_cap is None
        assert fetched.volume is None

    # Second data point (with market cap and volume)
    source_coingecko = CryptoSourceFactory(name="CoinGecko", type="aggregated")
    data2 = CryptoMarketDataFactory(
        asset=asset,
        source=source_coingecko,
        price=30000.50,
        interval="1h",
        market_cap=1000000000.0,
        volume=50000000.0,
    )

    with subtests.test("Aggregated CoinGecko Market Data"):
        fetched = (
            session.query(CryptoMarketData)
            .filter_by(source_id=source_coingecko.id, symbol=asset.symbol)
            .first()
        )
        assert fetched is not None
        assert fetched.asset.symbol == "BTC"
        assert fetched.source.name == "CoinGecko"
        assert float(fetched.price) == 30000.50
        assert fetched.interval == "1h"
        assert fetched.market_cap == 1000000000.0
        assert fetched.volume == 50000000.0


def test_crypto_technical_indicator_get_recent_by_symbol():
    """Test that fetch_latest_indicators returns the correct data format."""
    CryptoAssetFactory.create(symbol="BTC")

    # Create timestamps with clear ordering
    older_time = datetime(2025, 1, 1, 12, 0, 0)
    newer_time = datetime(2025, 1, 2, 12, 0, 0)

    # Create older indicator first
    older_indicator = CryptoTechnicalIndicatorFactory.create(
        symbol="BTC",
        interval="1h",
        ema=200.5,
        rsi=45.6,
        macd=0.78,
        timestamp=older_time,
    )

    # Create newer indicator second
    newer_indicator = CryptoTechnicalIndicatorFactory.create(
        symbol="BTC",
        interval="1h",
        ema=201.0,
        rsi=46.2,
        macd=0.80,
        timestamp=newer_time,
    )

    # Test the function - should return the newer indicator
    result = CryptoTechnicalIndicator.get_recent_by_symbol("BTC")

    # Compare the actual field values instead of object equality
    assert float(result.ema) == newer_indicator.ema
    assert float(result.rsi) == newer_indicator.rsi
    assert float(result.macd) == newer_indicator.macd
    assert result.timestamp == newer_indicator.timestamp

    # Test error case
    with pytest.raises(
        ValueError,
        match="No technical indicators available for NONEXISTENT",
    ):
        CryptoTechnicalIndicator.get_recent_by_symbol("NONEXISTENT")
