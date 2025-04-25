from datetime import datetime
from backend.entities.workers import listener_assignment_table, radio_assignment_table
from backend.models.user import User
from ..entity_base import EntityBase
from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship


class WorkerEntity(EntityBase):
    __tablename__ = "worker"

    worker_id: Mapped[int] = mapped_column(primary_key=True)

    radios: Mapped[list["RadioEntity"]] = relationship(
        "RadioEntity", secondary=radio_assignment_table, back_populates="worker"
    )

    listeners: Mapped[list["ListenerEntity"]] = relationship(
        "ListenerEntity", secondary=listener_assignment_table, back_populates="worker"
    )

    heartbeat_ts: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
