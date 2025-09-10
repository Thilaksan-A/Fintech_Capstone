from app.extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class Watchlist(BaseModel):
    user_id: Mapped[str] = mapped_column(
        db.ForeignKey("user.id"),
        primary_key=True,
        nullable=False,
    )
    symbol: Mapped[str] = mapped_column(
        db.ForeignKey("crypto_asset.symbol"),
        primary_key=True,
        nullable=False,
    )
    asset: Mapped["CryptoAsset"] = relationship(  # noqa
        back_populates="watchlisted_by",
    )
    user: Mapped["User"] = relationship(back_populates="watchlist")  # noqa
