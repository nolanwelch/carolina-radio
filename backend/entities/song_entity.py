from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, Integer, String
from .entity_base import EntityBase


class SongEntity(EntityBase):
    __tablename__ = "song"

    id: Mapped[int] = mapped_column(primary_key=True)
    spotify_uri: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    album: Mapped[str | None] = mapped_column(String, nullable=True)
    cover_url: Mapped[str | None] = mapped_column(String, nullable=True)
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False)

    artists: Mapped[list["Artist"]] = relationship(
        "Artist", secondary=song_artist_association, back_populates="songs"
    )

    vote_count: Mapped[int] = mapped_column(default=0, nullable=False)
    last_played: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
