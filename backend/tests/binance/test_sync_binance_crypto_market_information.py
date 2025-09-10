import factory
from app.models.crypto import CryptoAsset, CryptoSource, CryptoMarketData
from app.services.market.binance import (
    sync_binance_crypto_market_information,
)
from unittest.mock import patch
from datetime import timezone
import pandas as pd
from sqlalchemy import select

from tests.factories.crypto import CryptoAssetFactory


@patch("app.services.market.binance.fetch_binance_price_history")
@patch("app.services.market.binance.fetch_binance_symbols")
def test_fetch_and_store_inserts_data(
    mock_binance_symbols,
    mock_binance_price_history,
    db_session,
):
    stmt = select(CryptoAsset)
    assets = db_session.execute(stmt).scalars().all()
    assert len(assets) == 0

    stmt = select(CryptoMarketData).where(CryptoMarketData.symbol == "BTC")
    market_data = db_session.execute(stmt).scalars().all()
    assert len(market_data) == 0

    stmt = select(CryptoMarketData).where(CryptoMarketData.symbol == "ETH")
    market_data = db_session.execute(stmt).scalars().all()
    assert len(market_data) == 0

    CryptoAssetFactory.create_batch(
        size=2,
        symbol=factory.Iterator(["BTC", "ETH"]),
        name=factory.Iterator(["Bitcoin", "Ethereum"]),
        ranking=factory.Iterator([1, 2]),
    )

    mock_binance_symbols.return_value = ["BTCUSDT", "ETHUSDT"]
    end = pd.Timestamp.utcnow().floor('h')
    index = pd.date_range(end=end, periods=2, freq="h", tz=timezone.utc)
    mock_binance_price_history.return_value = pd.DataFrame(
        {"close": [30000.0, 31000.0]},
        index=index,
    )

    sync_binance_crypto_market_information()

    stmt = select(CryptoAsset)
    assets = db_session.execute(stmt).scalars().all()
    assert len(assets) == 2
    assert assets[0].symbol == "BTC"
    assert assets[1].symbol == "ETH"

    stmt = select(CryptoSource).where(CryptoSource.name == "Binance")
    source = db_session.execute(stmt).scalar_one_or_none()
    assert source is not None

    stmt = select(CryptoMarketData).where(CryptoMarketData.symbol == "BTC")
    market_data = db_session.execute(stmt).scalars().all()
    assert len(market_data) == 2

    stmt = select(CryptoMarketData).where(CryptoMarketData.symbol == "ETH")
    market_data = db_session.execute(stmt).scalars().all()
    assert len(market_data) == 2


@patch("app.services.market.binance.fetch_binance_price_history")
@patch("app.services.market.binance.fetch_binance_symbols")
def test_no_duplicate_market_data_insertions(
    mock_binance_symbols,
    mock_binance_price_history,
    db_session,
):
    CryptoAssetFactory.create_batch(
        size=2,
        symbol=factory.Iterator(["BTC", "ETH"]),
        name=factory.Iterator(["Bitcoin", "Ethereum"]),
        ranking=factory.Iterator([1, 2]),
    )

    mock_binance_symbols.return_value = ["BTCUSDT", "ETHUSDT"]
    end = pd.Timestamp.utcnow().floor('h')
    index = pd.date_range(end=end, periods=2, freq="h", tz=timezone.utc)
    mock_binance_price_history.return_value = pd.DataFrame(
        {"close": [30000.0, 31000.0]},
        index=index,
    )

    # First run
    sync_binance_crypto_market_information()

    stmt = select(CryptoAsset)
    assets = db_session.execute(stmt).scalars().all()
    assert len(assets) == 2
    assert assets[0].symbol == "BTC"

    stmt = select(CryptoSource).where(CryptoSource.name == "Binance")
    source = db_session.execute(stmt).scalar_one_or_none()
    assert source is not None

    stmt = select(CryptoMarketData).where(CryptoMarketData.symbol == "BTC")
    market_data = db_session.execute(stmt).scalars().all()
    assert len(market_data) == 2

    # Second run (should not insert duplicates)
    sync_binance_crypto_market_information()

    stmt = select(CryptoMarketData).where(CryptoMarketData.symbol == "BTC")
    market_data = db_session.execute(stmt).scalars().all()
    assert len(market_data) == 2, "duplicate added"

    stmt = select(CryptoMarketData).where(CryptoMarketData.symbol == "ETH")
    market_data = db_session.execute(stmt).scalars().all()
    assert len(market_data) == 2, "duplicate added"
