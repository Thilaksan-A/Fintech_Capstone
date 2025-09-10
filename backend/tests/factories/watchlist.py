import factory
from tests.factories import BaseFactory
from app.models.watchlist import Watchlist
from tests.factories.user import UserFactory
from tests.factories.crypto import CryptoAssetFactory


class WatchlistFactory(BaseFactory):
    class Meta:
        model = Watchlist

    user = factory.SubFactory(UserFactory)
    asset = factory.SubFactory(CryptoAssetFactory)
    user_id = factory.SelfAttribute("user.id")
    symbol = factory.SelfAttribute("asset.symbol")
