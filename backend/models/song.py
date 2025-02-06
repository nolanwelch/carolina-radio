from pydantic import BaseModel


__authors__ = ["David Foss", "Gabrian Chua", "Nolan Welch", "Rohan Kashyap"]
__copyright__ = "Copyright 2025"
__license__ = "MIT"


class SongModel(BaseModel):
    songId: str
    artists: list[str]
    album: str
    title: str
    coverUrl: str
    durationMs: int
