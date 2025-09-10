import requests
import pandas as pd
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import select

from app.extensions import db
from app.models import (
    CryptoAsset,
    CryptoSource,
    CryptoMarketData,
    CryptoTechnicalIndicator,
)
from app.utils import convert_timestamp_to_utc
from logging import getLogger
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator

from app.services.market.constants import BINANCE_BASE_URL
from app.constants import TOP_CRYPTOCURRENCIES_LIMIT
from app.utils.decorators import transactional


logger = getLogger(__name__)


def fetch_binance_symbols() -> list[str]:
    """
    Fetches the list of trading pairs (symbols) available on the Binance exchange.
    """
    url = f"{BINANCE_BASE_URL}/api/v3/exchangeInfo?"
    response = requests.get(url)
    data = response.json()
    symbols = []

    for item in data['symbols']:
        symbols.append(item['symbol'])
    return symbols


def fetch_binance_price_history(
    symbol: str,
    interval: str = "1h",
    limit: int = 192,
) -> pd.DataFrame:
    """
    Fetches price history of crypto/usdt pair on binance in hourly
    candles for last 7 days
    """
    url = f"{BINANCE_BASE_URL}/api/v3/klines?"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    data = requests.get(url, params=params).json()

    df = pd.DataFrame(
        data,
        columns=[
            'timestamp',
            'open',
            'high',
            'low',
            'close',
            'volume',
            'close_time',
            'quote_asset_volume',
            'number_of_trades',
            'taker_buy_base',
            'taker_buy_quote',
            'ignore',
        ],
    )
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
    df.set_index('timestamp', inplace=True)
    df = df.astype(float)
    return df[['close']]


def get_binance_current_price(symbol: str) -> float:
    """
    Fetches the current price of a cryptocurrency from the Binance API.
    """
    url = f"{BINANCE_BASE_URL}/api/v3/ticker/price"
    params = {"symbol": symbol}
    response = requests.get(url, params=params)

    data = response.json()
    price = float(data['price'])
    return price


@transactional
def calculate_and_store_indicators(symbol: str, df: pd.DataFrame):
    """
    Calculates ema, rsi, and macd based of hourly close candles.
    """
    # default previous 14 periods used for calculations
    df['ema'] = EMAIndicator(close=df['close']).ema_indicator()
    df['rsi'] = RSIIndicator(close=df['close']).rsi()
    macd = MACD(close=df['close'])
    df['macd'] = macd.macd()

    ta_stmt = select(CryptoTechnicalIndicator.timestamp).where(
        (CryptoTechnicalIndicator.symbol == symbol)
        & (CryptoTechnicalIndicator.interval == "1h"),
    )
    existing_timestamps = set(db.session.scalars(ta_stmt).all())
    existing_timestamps = {
        convert_timestamp_to_utc(ts) for ts in existing_timestamps
    }

    logger.info(f"Found {len(existing_timestamps)} existing timestamps.")
    for timestamp, row in df.iterrows():
        if pd.isna(row['ema']) or pd.isna(row['rsi']) or pd.isna(row['macd']):
            continue

        norm_ts = convert_timestamp_to_utc(timestamp)
        if norm_ts in existing_timestamps:
            continue

        db.session.add(
            CryptoTechnicalIndicator(
                symbol=symbol,
                interval="1h",
                timestamp=timestamp,
                ema=Decimal(row['ema']),
                rsi=Decimal(row['rsi']),
                macd=Decimal(row['macd']),
            ),
        )
    logger.info(f"Finished storing hourly indicators for {symbol}")


def get_existing_market_timestamps(symbol: str, source_id: int) -> set:
    ts_stmt = select(CryptoMarketData.timestamp).where(
        (CryptoMarketData.symbol == symbol)
        & (CryptoMarketData.source_id == source_id)
        & (CryptoMarketData.interval == "1h"),
    )
    existing_timestamps = set(db.session.scalars(ts_stmt).all())
    return {convert_timestamp_to_utc(ts) for ts in existing_timestamps}


def store_crypto_market_data(
    symbol: str,
    source_id: int,
    df: pd.DataFrame,
    existing_timestamps: set,
) -> int:
    new_data = []
    for timestamp, row in df.iterrows():
        norm_ts = convert_timestamp_to_utc(timestamp)
        if norm_ts in existing_timestamps:
            continue

        price = Decimal(row['close'])

        market_data = CryptoMarketData(
            symbol=symbol,
            source_id=source_id,
            timestamp=timestamp,
            interval="1h",
            price=price,
            volume=None,
            market_cap=None,
            ingested_at=datetime.now(timezone.utc),
        )
        new_data.append(market_data)
    if new_data:
        db.session.add_all(new_data)
    return len(new_data)


@transactional
def process_and_store_crypto(
    coin: CryptoAsset,
    binance_symbols: set,
    source: CryptoSource,
):
    """
    Process and store cryptocurrency data to CryptoMarketData and
    CryptoTechnicalIndicator.
    """
    symbol = coin.symbol.upper()
    name = coin.name
    logger.info(f"Processing coin: {symbol} ({name})")

    binance_pair = symbol + "USDT"
    if binance_pair not in binance_symbols:
        logger.warning(f"Skipping {symbol} {name}")
        return

    df = fetch_binance_price_history(binance_pair)
    logger.info(f"Querying existing timestamps for {symbol}...")

    existing_timestamps = get_existing_market_timestamps(symbol, source.id)
    logger.info(f"Found {len(existing_timestamps)} existing timestamps.")

    inserted = store_crypto_market_data(
        symbol,
        source.id,
        df,
        existing_timestamps,
    )
    logger.info(f"Inserted {inserted} new market data rows for {symbol}")
    logger.info(f"Daily indicators saved for {symbol}")
    calculate_and_store_indicators(symbol, df)


@transactional
def sync_binance_crypto_market_information():
    """
    Executes the synchronization task for Binance crypto market information.

    Steps:
    1. Get the top cryptocurrencies from the database.
    2. Fetch the current Binance trading pairs.
    3. Get or create the Binance data source.
    4. Process each coin in the top list - store market data and calculate indicators.
    """

    top_cryptos = CryptoAsset.query.filter(
        CryptoAsset.ranking <= (TOP_CRYPTOCURRENCIES_LIMIT * 2),
    ).all()
    binance_symbols = fetch_binance_symbols()
    source = CryptoSource.get_or_create(
        name="Binance",
        defaults={"type": "exchange"},
    )

    for crypto in top_cryptos:
        process_and_store_crypto(crypto, binance_symbols, source)
