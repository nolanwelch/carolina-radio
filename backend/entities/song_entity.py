from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, Integer, String

from backend.models.song import Song

from . import song_artist_table
from .entity_base import EntityBase


class SongEntity(EntityBase):
    __tablename__ = "song"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    spotify_uri: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    album: Mapped[str | None] = mapped_column(String, nullable=True)
    cover_url: Mapped[str | None] = mapped_column(String, nullable=True)
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False)

    artists: Mapped[list["ArtistEntity"]] = relationship(
        "ArtistEntity", secondary=song_artist_table, back_populates="songs"
    )

    def to_model(self) -> Song:
        return Song(
            id=self.id,
            spotify_uri=self.spotify_uri,
            title=self.title,
            album=self.album,
            cover_url=self.cover_url,
            duration_ms=self.duration_ms,
            artists=[artist.to_model() for artist in self.artists],
        )
