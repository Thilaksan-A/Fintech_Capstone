from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.mixins import AuditTimestampMixin, IdentityMixin
from app.constants.user import InvestorType, SocialImpact, TimeScore
from sqlalchemy import JSON, String, ForeignKey, Enum as SQLEnum, Integer
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.watchlist import Watchlist

from app.models.base import BaseModel


class User(BaseModel, IdentityMixin, AuditTimestampMixin):
    """
    Represents a registered user with login credentials and related profile data.
    """

    username: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
    )
    email: Mapped[str] = mapped_column(
        String(120),
        unique=True,
        nullable=False,
    )
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    subscription_tier: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="Free",
    )

    profile: Mapped["UserProfile"] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    watchlist: Mapped["Watchlist"] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def set_password(self, raw_password: str):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password_hash, raw_password)


class UserProfile(BaseModel, IdentityMixin, AuditTimestampMixin):
    """
    Stores additional profile information and derived scores for a user.
    """

    user_id: Mapped[str] = mapped_column(
        ForeignKey("user.id"),
        unique=True,
        nullable=False,
    )
    user: Mapped["User"] = relationship(back_populates="profile")

    risk_score: Mapped[int] = mapped_column(Integer, nullable=False)
    rational_score: Mapped[int] = mapped_column(Integer, nullable=False)
    fomo_score: Mapped[int] = mapped_column(Integer, nullable=False)
    emotional_score: Mapped[int] = mapped_column(Integer, nullable=False)

    time_score: Mapped[TimeScore] = mapped_column(
        SQLEnum(TimeScore),
        nullable=True,
    )
    social_impact: Mapped[SocialImpact] = mapped_column(
        SQLEnum(SocialImpact),
        nullable=True,
    )
    investor_type: Mapped[InvestorType] = mapped_column(
        SQLEnum(InvestorType),
        nullable=True,
    )

    raw_responses: Mapped[dict] = mapped_column(JSON, nullable=True)
