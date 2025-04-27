from pydantic import BaseModel

from ..models.user import User


__authors__ = ["David Foss"]
__copyright__ = "Copyright 2025"
__license__ = "MIT"


class Listener(BaseModel):
    id: int
    user: User
