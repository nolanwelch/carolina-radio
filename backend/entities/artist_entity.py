from backend.entities import song_artist_table
from backend.models.artist import Artist
from .entity_base import EntityBase
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class ArtistEntity(EntityBase):
    __tablename__ = "artist"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    songs: Mapped[list["SongEntity"]] = relationship(
        "SongEntity", secondary=song_artist_table, back_populates="artists"
    )

    def to_model(self) -> Artist:
        return Artist(
            id=self.id,
            name=self.name,
        )

    # No from_model, as new artists should never be created from the frontend
