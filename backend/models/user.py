from pydantic import BaseModel

__authors__ = ["David Foss", "Gabrian Chua", "Nolan Welch", "Rohan Kashyap"]
__copyright__ = "Copyright 2025"
__license__ = "MIT"


class UserPartial(BaseModel):
    """Model that represents the user."""

    id: int
    spotify_uri: str


class User(UserPartial):
    pass
