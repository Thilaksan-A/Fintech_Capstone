from tests.factories.user import UserFactory
from tests.factories.crypto import CryptoAssetFactory
from tests.factories.watchlist import WatchlistFactory

import logging

logger = logging.getLogger(__name__)


def test_add_watchlist_entry():
    """Test adding a watchlist entry."""
    user = UserFactory()
    asset = CryptoAssetFactory(symbol="BTC")

    watchlist = WatchlistFactory(user=user, asset=asset)

    assert watchlist.user_id == user.id
    assert watchlist.symbol == "BTC"
    assert watchlist.user == user


def test_user_relationship():
    """Test the relationship between watchlist and user."""
    user = UserFactory(username="testuser")
    asset = CryptoAssetFactory(symbol="ETH")

    watchlist = WatchlistFactory(user=user, asset=asset)

    assert watchlist.user.username == "testuser"
    assert watchlist.symbol == "ETH"
    assert watchlist.user_id == user.id


def test_multiple_watchlist_entries_for_user():
    """Test that a user can have multiple watchlist entries."""
    user = UserFactory()
    btc_asset = CryptoAssetFactory(symbol="BTC")
    eth_asset = CryptoAssetFactory(symbol="ETH")

    btc_watchlist = WatchlistFactory(user=user, asset=btc_asset)
    eth_watchlist = WatchlistFactory(user=user, asset=eth_asset)

    assert btc_watchlist.user_id == user.id
    assert eth_watchlist.user_id == user.id
    assert btc_watchlist.symbol == "BTC"
    assert eth_watchlist.symbol == "ETH"


def test_multiple_users_can_watch_same_asset():
    """Test that multiple users can watch the same asset."""
    user1 = UserFactory(username="user1")
    user2 = UserFactory(username="user2")
    asset = CryptoAssetFactory(symbol="BTC")

    watchlist1 = WatchlistFactory(user=user1, asset=asset)
    watchlist2 = WatchlistFactory(user=user2, asset=asset)

    assert watchlist1.symbol == "BTC"
    assert watchlist2.symbol == "BTC"
    assert watchlist1.user_id != watchlist2.user_id


def test_watchlist_string_representation():
    """Test the string representation of watchlist."""
    user = UserFactory(username="testuser")
    asset = CryptoAssetFactory(symbol="BTC")

    watchlist = WatchlistFactory(user=user, asset=asset)

    # Assuming your Watchlist model has a __repr__ or __str__ method
    watchlist_str = str(watchlist)
    assert "testuser" in watchlist_str or "BTC" in watchlist_str
