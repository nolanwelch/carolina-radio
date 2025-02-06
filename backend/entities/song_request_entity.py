from .entity_base import EntityBase
from sqlalchemy import DateTime, Enum, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum

from datetime import datetime


class RequestStatus(PyEnum):
    REQUESTED = "requested"
    QUEUED = "queued"
    PLAYING = "playing"
    PLAYED = "played"


class SongRequestEntity(EntityBase):
    __tablename__ = "song_request"

    id: Mapped[int] = mapped_column(primary_key=True)
    time_created: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    song_id: Mapped[int] = mapped_column(ForeignKey("song.id"), nullable=False)
    song: Mapped["Song"] = relationship("Song")

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    user: Mapped["User"] = relationship("User")

    status: Mapped[RequestStatus] = mapped_column(
        Enum(RequestStatus), default=RequestStatus.REQUESTED, nullable=False
    )

    # position in the play queue; null for unqueued songs
    queue_position: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # time that song started playing; null for songs not in queue position 0
    time_started: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
