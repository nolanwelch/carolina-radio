from pydantic import BaseModel


__authors__ = ["David Foss"]
__copyright__ = "Copyright 2025"
__license__ = "MIT"


class Artist(BaseModel):
    id: int
    name: str
