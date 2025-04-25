from backend.entities.workers import radio_assignment_table
from backend.models.user import User
from .entity_base import EntityBase
from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class RadioEntity(EntityBase):
    __tablename__ = "radio"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    name: Mapped[str] = mapped_column(String, unique=True)
    description: Mapped[str] = mapped_column(String)

    public: Mapped[bool] = mapped_column(Boolean)
    listen_permission: Mapped[int] = mapped_column(Integer)
    request_require_listen: Mapped[bool] = mapped_column(Boolean)

    memberships: Mapped[list["MembershipEntity"]] = relationship(
        "MembershipEntity", back_populates="radio"
    )

    listeners: Mapped[list["ListenerEntity"]] = relationship(
        "ListenerEntity", back_populates="radio"
    )

    worker: Mapped[list["WorkerEntity"]] = relationship(
        "WorkerEntity", secondary=radio_assignment_table, back_populates="radios"
    )

    def to_model(self) -> User:
        return User(
            id=self.id,
            name=self.id,
        )
