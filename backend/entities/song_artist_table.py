from sqlalchemy import Column, ForeignKey, Integer, Table
from .entity_base import EntityBase


song_artist_table = Table(
    "song_artist",
    EntityBase.metadata,
    Column("song_id", Integer, ForeignKey("song.id"), primary_key=True),
    Column("artist_id", Integer, ForeignKey("artist.id"), primary_key=True),
)
