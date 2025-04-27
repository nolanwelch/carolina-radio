from pydantic import BaseModel

from ..models.listener import Listener
from ..models.user import User


__authors__ = ["David Foss"]
__copyright__ = "Copyright 2025"
__license__ = "MIT"


class Radio(BaseModel):
    id: int
    name: str

    public: bool
    listen_permission: int
    request_require_listen: bool

    members: list[User]

    listeners: list[Listener]
