from datetime import datetime
from backend.models.user import User
from ..entity_base import EntityBase
from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship


class RefreshTokenEntity(EntityBase):
    __tablename__ = "refresh_token"
    __table_args__ = {"schema": "auth"}

    # This is NOT the refresh token!
    # this is a code that is included inside the refresh token
    refresh_token_code: Mapped[str] = mapped_column(String, primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    user: Mapped["UserEntity"] = relationship("UserEntity")

    timestamp: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    def to_model(self) -> User:
        return User(
            id=id,
            spotify_uri=self.spotify_uri,
            song_requests=self.song_requests,
            spotify_access_token=self.spotify_access_token,
            spotify_refresh_token=self.spotify_refresh_token,
        )
