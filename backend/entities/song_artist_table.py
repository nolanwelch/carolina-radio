from sqlalchemy import ForeignKey, Integer, Table
from .entity_base import EntityBase
from sqlalchemy.orm import mapped_column


song_artist_table = Table(
    "song_artist",
    EntityBase.metadata,
    mapped_column("song_id", Integer, ForeignKey("song.id"), primary_key=True),
    mapped_column("artist_id", Integer, ForeignKey("artist.id"), primary_key=True),
)
