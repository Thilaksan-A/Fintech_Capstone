import factory
from datetime import datetime, timezone
from app.models.crypto import CryptoNewsData
from tests.factories import BaseFactory


class CryptoNewsDataFactory(BaseFactory):
    class Meta:
        model = CryptoNewsData

    symbol = "BTC"
    title = "BTC going to crash again!"
    description = "The author postulates that BTC is following closely with the previous cycle and will experience a dramatic drop in price."
    content = "The author postulates that BTC is following closely with the previous cycle and will experience a dramatic drop in price."
    source_url = "https://madeup.com/btc-crash"
    url_image = "https://madeup.com/btc-crash/crash.png"
    timestamp = factory.LazyFunction(lambda: datetime.now(timezone.utc))
