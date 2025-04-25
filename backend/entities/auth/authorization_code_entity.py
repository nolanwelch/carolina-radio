from datetime import datetime
from backend.models.user import User
from ..entity_base import EntityBase
from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column


class AuthCodeEntity(EntityBase):
    __tablename__ = "auth_code"
    __table_args__ = {"schema": "auth"}

    auth_code: Mapped[str] = mapped_column(String, primary_key=True)

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
