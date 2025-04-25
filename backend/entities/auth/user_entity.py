from backend.entities.workers import listener_assignment_table
from backend.models.user import User
from ..entity_base import EntityBase
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class UserEntity(EntityBase):
    __tablename__ = "user"
    __table_args__ = {"schema": "auth"}

    id: Mapped[int] = mapped_column(primary_key=True)
    spotify_uri: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    song_requests: Mapped[list["SongRequest"]] = relationship(
        "SongRequest", back_populates="user"
    )

    spotify_access_token: Mapped[str] = mapped_column(String, nullable=False)
    spotify_refresh_token: Mapped[str] = mapped_column(String, nullable=False)

    memberships: Mapped[list["MembershipEntity"]] = relationship(
        "MembershipEntity", back_populates="user"
    )

    worker: Mapped[list["WorkerEntity"]] = relationship(
        "WorkerEntity", secondary=listener_assignment_table, back_populates="users"
    )

    def to_model(self) -> User:
        return User(
            id=id,
            spotify_uri=self.spotify_uri,
            song_requests=self.song_requests,
            spotify_access_token=self.spotify_access_token,
            spotify_refresh_token=self.spotify_refresh_token,
        )
