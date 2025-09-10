import factory
from app.models.crypto import CryptoTechnicalIndicator
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
def test_technical_indicators_insert_and_no_duplicates(
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
    index = pd.date_range(end=end, periods=50, freq="h", tz=timezone.utc)

    close_prices = []
    start_price = 30000.0
    for i in range(50):
        price = start_price + i * 50
        close_prices.append(price)

    mock_binance_price_history.return_value = pd.DataFrame(
        {"close": close_prices},
        index=index,
    )

    sync_binance_crypto_market_information()

    stmt_btc = select(CryptoTechnicalIndicator).where(
        CryptoTechnicalIndicator.symbol == "BTC",
    )
    btc_ta = db_session.execute(stmt_btc).scalars().all()
    assert len(btc_ta) > 0, "No technical indicators inserted for BTC"

    stmt_eth = select(CryptoTechnicalIndicator).where(
        CryptoTechnicalIndicator.symbol == "ETH",
    )
    eth_ta = db_session.execute(stmt_eth).scalars().all()
    assert len(eth_ta) > 0, "No technical indicators inserted for ETH"

    # Run again to check for duplicates
    sync_binance_crypto_market_information()

    btc_tech_dup = db_session.execute(stmt_btc).scalars().all()
    eth_tech_dup = db_session.execute(stmt_eth).scalars().all()

    assert len(btc_tech_dup) == len(
        btc_ta,
    ), "Duplicate technical indicators added for BTC"
    assert len(eth_tech_dup) == len(
        eth_ta,
    ), "Duplicate technical indicators added for ETH"
