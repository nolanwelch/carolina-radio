from datetime import datetime, timedelta
from fastapi import Depends, HTTPException

from backend.database import db_session
from sqlalchemy.orm import Session

from backend.entities.song_request_entity import SongRequestEntity
from backend.models.song import Song
from backend.models.song_request import SongRequest

__authors__ = ["David Foss", "Rohan Kashyap", "Nolan Welch", "Gabrian Chua"]
__copyright__ = "Copyright 2025"
__license__ = "MIT"


class QueueService:
    """QueueService provides the functionality for managing the song queue"""

    def __init__(
        self,
        session: Session = Depends(db_session),
    ):
        """Initializes a new QueueService.

        Args:
            session (Session): The database session to use, typically injected by FastAPI.
        """
        self._session = session

    def now_playing(self):
        result = (
            self._session.query(SongRequestEntity)
            .filter(SongRequestEntity.queue_position == 0)
            .first()
        )
        if result is None:
            raise HTTPException(status_code=404)
        top_song = result.song

        pos_ms = (datetime.now() - result.time_started) / timedelta(milliseconds=1)
        return top_song, pos_ms

    def get_queue(self, session: Session) -> list[Song]:
        play_queue = (
            session.query(SongRequestEntity)
            .filter(
                SongRequestEntity.queue_position is not None
                and SongRequestEntity.queue_position > 0
            )
            .order_by(SongRequestEntity.queue_position)
        )
        songs = [SongRequest.to_model(req.song) for req in play_queue]
        return songs
