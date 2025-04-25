from sqlalchemy import Column, ForeignKey, Integer, Table
from ..entity_base import EntityBase


radio_assignment_table = Table(
    "radio_assignment",
    EntityBase.metadata,
    Column("radio_id", Integer, ForeignKey("radio.id"), primary_key=True),
    Column("worker_id", Integer, ForeignKey("worker.id"), primary_key=True),
)
