from pydantic import BaseModel

from backend.models.artist import Artist


__authors__ = ["David Foss", "Gabrian Chua", "Nolan Welch", "Rohan Kashyap"]
__copyright__ = "Copyright 2025"
__license__ = "MIT"


class Song(BaseModel):
    songId: str
    artists: list[Artist]
    album: str
    title: str
    coverUrl: str
    durationMs: int
