from typing import Self
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Integer

from backend.entities.auth.user_entity import UserEntity
from backend.entities.radio_entity import RadioEntity
from backend.models.listener import Listener
from backend.models.song import Song

from .entity_base import EntityBase


class ListenerEntity(EntityBase):
    """Represents a user that is currently listening to a radio"""

    __tablename__ = "listener"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("auth.user.id"), nullable=False)
    user: Mapped["UserEntity"] = relationship("UserEntity")

    radio_id: Mapped[int] = mapped_column(ForeignKey("radio.id"), nullable=False)
    radio: Mapped["RadioEntity"] = relationship("RadioEntity")

    def to_model(self) -> Listener:
        return Listener(
            id=self.id,
            user=self.user.to_model(),
            radio=self.radio.to_model,
        )
