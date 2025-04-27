from datetime import datetime
import uuid
from pydantic import BaseModel, Field

from .song import SongModel


__authors__ = ["David Foss", "Gabrian Chua", "Nolan Welch", "Rohan Kashyap"]
__copyright__ = "Copyright 2025"
__license__ = "MIT"


class PoolEntry(BaseModel):
    entryId: str = Field(default_factory=lambda: str(uuid.uuid4()))
    position: int = -1
    song: SongModel
    startDT: datetime = datetime.fromtimestamp(0)
    votes: int
    lastPlayedDT: datetime = datetime.fromtimestamp(0)
    poolJoinDT: datetime = datetime.fromtimestamp(0)
