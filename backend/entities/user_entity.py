from .entity_base import EntityBase
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class UserEntity(EntityBase):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    spotify_uri: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    sessions: Mapped[list["UserSession"]] = relationship(
        "UserSession", back_populates="user"
    )
    song_requests: Mapped[list["SongRequest"]] = relationship(
        "SongRequest", back_populates="user"
    )
