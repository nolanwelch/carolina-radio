from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Table
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func


class RequestStatus(PyEnum):
    REQUESTED = "requested"
    QUEUED = "queued"
    PLAYING = "playing"
    PLAYED = "played"


class Base(DeclarativeBase):
    pass


song_artist_association = Table(
    "song_artist_association",
    Base.metadata,
    mapped_column("song_id", Integer, ForeignKey("song.id"), primary_key=True),
    mapped_column("artist_id", Integer, ForeignKey("artist.id"), primary_key=True),
)


class Song(Base):
    __tablename__ = "song"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    album: Mapped[str | None] = mapped_column(String, nullable=True)
    cover_url: Mapped[str | None] = mapped_column(String, nullable=True)
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False)

    artists: Mapped[list["Artist"]] = relationship(
        "Artist", secondary=song_artist_association, back_populates="songs"
    )

    vote_count: Mapped[int] = mapped_column(default=0, nullable=False)
    last_played: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class Artist(Base):
    __tablename__ = "artist"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    songs: Mapped[list["Song"]] = relationship(
        "Song", secondary=song_artist_association, back_populates="artists"
    )


class Album(Base):
    __tablename__ = "album"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(32))


class SongRequest(Base):
    __tablename__ = "song_request"

    id: Mapped[int] = mapped_column(primary_key=True)
    time_created: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    song_id: Mapped[int] = mapped_column(ForeignKey("song.id"), nullable=False)
    song: Mapped["Song"] = relationship("Song")

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    user: Mapped["User"] = relationship("User")

    status: Mapped[RequestStatus] = mapped_column(
        Enum(RequestStatus), default=RequestStatus.REQUESTED, nullable=False
    )

    # position in the play queue; null for unqueued songs
    queue_position: Mapped[int | None] = mapped_column(Integer, nullable=True)


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    spotify_uri: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    sessions: Mapped[list["UserSession"]] = relationship(
        "UserSession", back_populates="user"
    )
    song_requests: Mapped[list["SongRequest"]] = relationship(
        "SongRequest", back_populates="user"
    )


class UserSession(Base):
    __tablename__ = "user_session"

    id: Mapped[int] = mapped_column(primary_key=True)
    start_time: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    user: Mapped["User"] = relationship("User")

    access_token: Mapped[str] = mapped_column(String, nullable=False)
    refresh_token: Mapped[str] = mapped_column(String, nullable=False)

    # something to give the user to identify existing sessions
    session_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
