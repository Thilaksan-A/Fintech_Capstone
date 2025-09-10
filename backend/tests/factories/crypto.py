import factory
import uuid
from decimal import Decimal
from datetime import datetime, timezone

from app.models.crypto import (
    CryptoAsset,
    CryptoSource,
    CryptoMarketData,
    CryptoTechnicalIndicator,
)
from tests.factories import BaseFactory


class CryptoAssetFactory(BaseFactory):
    class Meta:
        model = CryptoAsset

    symbol = factory.Faker("word", ext_word_list=['BTC', 'ETH', 'XRP', 'LTC'])
    name = factory.Faker("name")
    ranking = factory.Sequence(lambda n: n + 1)
    coingecko_id = factory.Faker("name")


class CryptoSourceFactory(BaseFactory):
    class Meta:
        model = CryptoSource

    id = factory.LazyFunction(uuid.uuid4)
    name = factory.Sequence(lambda n: f"Source{n}")
    type = factory.Iterator(["live", "aggregated"])


class CryptoMarketDataFactory(BaseFactory):
    class Meta:
        model = CryptoMarketData

    symbol = factory.SelfAttribute("asset.symbol")
    source_id = factory.SelfAttribute("source.id")
    interval = factory.Iterator(["1m", "5m", "1h", "1d"])
    ingested_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))

    asset = factory.SubFactory(CryptoAssetFactory)
    source = factory.SubFactory(CryptoSourceFactory)

    timestamp = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    price = Decimal("30000.00")
    market_cap = None
    volume = None


class CryptoTechnicalIndicatorFactory(BaseFactory):
    class Meta:
        model = CryptoTechnicalIndicator

    symbol = factory.Faker("word", ext_word_list=['BTC', 'ETH', 'XRP', 'LTC'])
    interval = factory.Iterator(["1m", "5m", "1h", "1d"])
    timestamp = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    ema = 200.0
    rsi = 50.0
    macd = 0.0
