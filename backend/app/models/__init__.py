# Ensures models are loaded for Alembic migration detection
# and unified access across the app.

from .user import User, UserProfile
from .demo_user import DemoUser
from .crypto import (
    CryptoAsset,
    CryptoSource,
    CryptoMarketData,
    CryptoTechnicalIndicator,
    CryptoRedditData,
    CryptoCoingeckoSentimentData,
    CryptoSentimentAggregateData,
    CryptoNewsData,
)
from .youtube import YoutubeComment, YoutubeCommentAnalysis
from .watchlist import Watchlist


__all__ = [
    "User",
    "UserProfile",
    "DemoUser",
    "CryptoAsset",
    "CryptoSource",
    "CryptoMarketData",
    "CryptoNewsData",
    "CryptoTechnicalIndicator",
    "CryptoRedditData",
    "CryptoCoingeckoSentimentData",
    "CryptoSentimentAggregateData",
    "YoutubeComment",
    "YoutubeCommentAnalysis",
    "Watchlist",
]
