from sqlalchemy import Column, ForeignKey, Integer, Table
from ..entity_base import EntityBase


listener_assignment_table = Table(
    "listener_assignment",
    EntityBase.metadata,
    Column("listener_id", Integer, ForeignKey("listener.id"), primary_key=True),
    Column("worker_id", Integer, ForeignKey("worker.id"), primary_key=True),
)
