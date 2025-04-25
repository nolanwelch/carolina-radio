from datetime import datetime
from backend.models.user import User
from ..entity_base import EntityBase
from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship


class MembershipEntity(EntityBase):
    __tablename__ = "membership"

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    user: Mapped["UserEntity"] = relationship("UserEntity")

    radio_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    radio: Mapped["RadioEntity"] = relationship("RadioEntity")

    permissions: Mapped[int] = mapped_column(Integer, default=0)

    def to_model(self) -> Membership:
        return Membership(
            id=self.id,
            user=self.user.to_model(),
            radio=self.radio.to_model(),
            permissions=self.permissions,
        )
