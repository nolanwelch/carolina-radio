from .entity_base import EntityBase
from sqlalchemy import DateTime, Enum, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum

from datetime import datetime


class RequestStatus(PyEnum):
    REQUESTED = "requested"
    QUEUED = "queued"


class SongRequestEntity(EntityBase):
    __tablename__ = "song_request"

    id: Mapped[int] = mapped_column(primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    radio_id: Mapped[int] = mapped_column(ForeignKey("radio.id"), nullable=False)
    radio: Mapped["RadioEntity"] = relationship("RadioEntity")

    song_id: Mapped[int] = mapped_column(ForeignKey("song.id"), nullable=False)
    song: Mapped["SongEntity"] = relationship("SongEntity")

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["UserEntity"] = relationship("UserEntity")

    status: Mapped[RequestStatus] = mapped_column(
        Enum(RequestStatus), default=RequestStatus.REQUESTED, nullable=False
    )
