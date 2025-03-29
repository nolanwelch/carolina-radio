from datetime import datetime
from .entity_base import EntityBase
from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship


class UserSpotifySessionEntity(EntityBase):
    __tablename__ = "user_session"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_time: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    user: Mapped["User"] = relationship("User")

    access_token: Mapped[str] = mapped_column(String, nullable=False)
    refresh_token: Mapped[str] = mapped_column(String, nullable=False)
