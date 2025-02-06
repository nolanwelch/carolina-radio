"""Service that manages user-related processes"""

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.entities.user_entity import UserEntity
from backend.models.user import User

from ..database import db_session

__authors__ = ["David Foss"]
__copyright__ = "Copyright 2025"
__license__ = "MIT"


class UserService:
    """UserService is the layer handling user methods."""

    def __init__(
        self,
        session: Session = Depends(db_session),
    ):
        """Initializes a new UserService.

        Args:
            session (Session): The database session to use, typically injected by FastAPI.
        """
        self._session = session

    def get(self, spotify_uri: str) -> User | None:
        """Returns the user associated with the given spotify uri"""
        user_query = select(UserEntity).where(
            UserEntity.spotify_uri == spotify_uri,
        )
        user_entity = self._session.scalars(user_query).first()

        return user_entity.to_model() if user_entity else None
