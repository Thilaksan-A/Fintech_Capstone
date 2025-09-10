from app.extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.crypto import CryptoAsset
from app.models.mixins import TimescaleMixin
from sqlalchemy import (
    Index,
    PrimaryKeyConstraint,
    String,
    Text,
    DateTime,
    JSON,
    Float,
    Integer,
    ForeignKey,
)
from datetime import datetime
from typing import Optional

from app.models.base import BaseModel


class YoutubeComment(BaseModel):
    comment_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    video_id: Mapped[str] = mapped_column(String(50), nullable=False)
    video_title: Mapped[str] = mapped_column(String(255), nullable=False)

    text_original: Mapped[str] = mapped_column(Text, nullable=False)
    like_count: Mapped[int] = mapped_column(Integer, default=0)
    total_reply_count: Mapped[int] = mapped_column(Integer, default=0)
    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    raw_response: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    analysis: Mapped[list["YoutubeCommentAnalysis"]] = relationship(
        back_populates="comment",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("idx_comment_video_published", "video_id", "published_at"),
    )


class YoutubeCommentAnalysis(BaseModel, TimescaleMixin):
    """
    Represents analysis results for a YouTube comment with crypto asset
    relations.
    """

    comment_id: Mapped[str] = mapped_column(
        ForeignKey("youtube_comment.comment_id"),
        nullable=False,
    )
    crypto_symbol: Mapped[str] = mapped_column(
        ForeignKey("crypto_asset.symbol"),
        nullable=False,
    )

    confidence_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )  # 0.0 to 1.0

    relevance_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )  # How relevant to the crypto
    quality_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )  # Comment quality (spam detection)

    analysed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=db.func.now(),
        nullable=False,
    )

    comment: Mapped["YoutubeComment"] = relationship(
        back_populates="analysis",
    )
    crypto_asset: Mapped["CryptoAsset"] = relationship()

    __table_args__ = (
        PrimaryKeyConstraint("comment_id", "crypto_symbol", "timestamp"),
        Index(
            "idx_comment_analysis_crypto_time",
            "crypto_symbol",
            "timestamp",
        ),
        Index("idx_comment_analysis_comment_time", "comment_id", "timestamp"),
    )
