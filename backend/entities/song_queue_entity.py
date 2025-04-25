from .entity_base import EntityBase
from sqlalchemy import DateTime, Enum, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum

from datetime import datetime


class SongQueueEntity(EntityBase):
    """SongQueueEntity acts as a queue ticket, created once a song is officially added to the queue"""

    __tablename__ = "song_queue"

    id: Mapped[int] = mapped_column(primary_key=True)

    song_id: Mapped[int] = mapped_column(ForeignKey("song.id"), nullable=False)
    song: Mapped["SongEntity"] = relationship("SongEntity")

    # position in the play queue
    queue_position: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # time that song started playing; null for songs not in queue position 0
    time_started: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
