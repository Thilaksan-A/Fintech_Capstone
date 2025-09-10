from datetime import datetime
import uuid
from sqlalchemy import (
    DateTime,
    ForeignKey,
    Numeric,
    PrimaryKeyConstraint,
    String,
    func,
    select,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.extensions import db

from app.models.mixins import IdentityMixin, TimescaleMixin
from app.models.watchlist import Watchlist
from app.models.base import BaseModel


class CryptoAsset(BaseModel):
    """
    Represents a cryptocurrency asset with its metadata and market data.
    """

    symbol: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    ranking: Mapped[int] = mapped_column()
    market_data: Mapped[list["CryptoMarketData"]] = relationship(
        back_populates="asset",
    )
    # metadata
    coingecko_id: Mapped[str] = mapped_column(nullable=True)
    image: Mapped[str] = mapped_column(nullable=True)
    description: Mapped[str] = mapped_column(nullable=True)
    categories: Mapped[str] = mapped_column(nullable=True)
    homepage_url: Mapped[str] = mapped_column(nullable=True)
    subreddit_url: Mapped[str] = mapped_column(nullable=True)
    purchase_platforms: Mapped[str] = mapped_column(nullable=True)
    watchlisted_by: Mapped[list["Watchlist"]] = relationship(
        back_populates="asset",
    )
    marketcap: Mapped[float] = mapped_column(nullable=True)
    volume: Mapped[float] = mapped_column(nullable=True)


class CryptoSource(BaseModel, IdentityMixin):
    """
    Represents a source of cryptocurrency market data.
    """

    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    type: Mapped[str] = mapped_column()
    market_data: Mapped[list["CryptoMarketData"]] = relationship(
        back_populates="source",
    )


class CryptoMarketData(BaseModel, TimescaleMixin):
    """
    Represents raw market data for a cryptocurrency asset from a specific source.
    """

    symbol: Mapped[str] = mapped_column(
        ForeignKey("crypto_asset.symbol"),
        nullable=False,
    )
    source_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("crypto_source.id"),
        nullable=False,
    )
    price: Mapped[float] = mapped_column(Numeric, nullable=False)
    interval: Mapped[str] = mapped_column(
        String(8),
        nullable=False,  # e.g. '1m', '1h', '1d'
    )
    market_cap: Mapped[float] = mapped_column(Numeric, nullable=True)
    volume: Mapped[float] = mapped_column(Numeric, nullable=True)
    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    asset: Mapped["CryptoAsset"] = relationship(back_populates="market_data")
    source: Mapped["CryptoSource"] = relationship(back_populates="market_data")

    __table_args__ = (
        PrimaryKeyConstraint("symbol", "source_id", "timestamp", "interval"),
    )


class CryptoRedditData(BaseModel):
    """
    Represents raw social data obtained for a cryptocurrency from reddit.
    """

    symbol: Mapped[str] = mapped_column(
        ForeignKey("crypto_asset.symbol"),
        nullable=False,
    )
    subreddit: Mapped[str] = mapped_column()
    text: Mapped[str] = mapped_column()
    votes: Mapped[int] = mapped_column()
    confidence: Mapped[float] = mapped_column()
    timestamp: Mapped[datetime] = mapped_column()
    source_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("crypto_source.id"),
        nullable=False,
    )
    __table_args__ = (PrimaryKeyConstraint("symbol", "subreddit", "text"),)


class CryptoCoingeckoSentimentData(BaseModel):
    """
    Represents aggregated social sentiment data collected from Coingecko.
    """

    symbol: Mapped[str] = mapped_column(
        ForeignKey("crypto_asset.symbol"),
        nullable=False,
    )
    sentiment_up_percentage: Mapped[float] = mapped_column(nullable=True)
    sentiment_down_percentage: Mapped[float] = mapped_column(nullable=True)
    reddit_average_posts_48h: Mapped[float] = mapped_column(nullable=True)
    commit_count_4_weeks: Mapped[float] = mapped_column(nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (PrimaryKeyConstraint("symbol", "timestamp"),)


class CryptoSentimentAggregateData(BaseModel, TimescaleMixin):
    """
    Represents the aggregated analysis of sentiment data from various
    social media / news sources.
    """

    symbol: Mapped[str] = mapped_column(
        ForeignKey("crypto_asset.symbol"),
        nullable=False,
    )
    normalised_up_percentage: Mapped[float] = mapped_column(nullable=False)
    normalised_down_percentage: Mapped[float] = mapped_column(nullable=False)
    avg_positive_sentiment: Mapped[float] = mapped_column(nullable=False)
    avg_neutral_sentiment: Mapped[float] = mapped_column(nullable=False)
    avg_negative_sentiment: Mapped[float] = mapped_column(nullable=False)
    avg_compound_sentiment: Mapped[float] = mapped_column(nullable=False)
    earliest_post: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (PrimaryKeyConstraint("symbol", "timestamp"),)

    @classmethod
    def get_latest_sentiment_score(cls, symbol: str) -> float:
        """
        Retrieves the latest sentiment score for a given cryptocurrency symbol.
        """
        result = db.session.scalar(
            select(cls.avg_compound_sentiment)
            .where(cls.symbol == symbol)
            .order_by(cls.timestamp.desc())
            .limit(1),
        )
        return float(result) if result is not None else 0.0


class CryptoTechnicalIndicator(BaseModel):
    """
    Represents the EMA, MACD, and RSI values for a crypto asset
    calculated from Binance.
    """

    symbol: Mapped[str] = mapped_column(
        ForeignKey("crypto_asset.symbol"),
        nullable=False,
    )
    interval: Mapped[str] = mapped_column(
        String(8),
        nullable=False,
    )  # e.g. '1h', '1d'
    timestamp: Mapped[datetime] = mapped_column(nullable=False)
    ema: Mapped[float] = mapped_column(Numeric, nullable=True)
    macd: Mapped[float] = mapped_column(Numeric, nullable=True)
    rsi: Mapped[float] = mapped_column(Numeric, nullable=True)

    __table_args__ = (PrimaryKeyConstraint("symbol", "timestamp", "interval"),)

    @classmethod
    def get_recent_by_symbol(cls, symbol: str) -> "CryptoTechnicalIndicator":
        """
        Retrieves financial indicators (RSI, EMA, MACD) for a symbol
        """
        result = (
            db.session.query(cls)
            .filter(cls.symbol == symbol, cls.interval == "1h")
            .order_by(cls.timestamp.desc())
            .first()
        )

        if not result:
            raise ValueError(f"No technical indicators available for {symbol}")

        return result


class CryptoNewsData(BaseModel):
    """
    Represents raw news data obtained for a cryptocurrency.
    """

    symbol: Mapped[str] = mapped_column(
        ForeignKey("crypto_asset.symbol"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    timestamp: Mapped[datetime] = mapped_column()
    source_url: Mapped[str] = mapped_column()
    url_image: Mapped[str] = mapped_column()
    content: Mapped[str] = mapped_column()
    __table_args__ = (
        PrimaryKeyConstraint("symbol", "timestamp", "source_url"),
    )
