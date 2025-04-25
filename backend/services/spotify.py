import base64
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException

from requests.adapters import HTTPAdapter, Retry

from backend.database import db_session
from sqlalchemy.orm import Session
from requests import Session as RequestSession

from backend.entities.song_entity import SongEntity
from backend.entities.song_request_entity import SongRequestEntity
from backend.entities.auth.user_entity import UserEntity
from backend.env import getenv
from backend.models.song import Song
from backend.models.song_request import SongRequest
from backend.models.user import User

__authors__ = ["David Foss", "Rohan Kashyap", "Nolan Welch", "Gabrian Chua"]
__copyright__ = "Copyright 2025"
__license__ = "MIT"


class SpotifyService:
    """SpotifyService provides the functionality for interacting with the spotify API"""

    def __init__(
        self,
        session: Session = Depends(db_session),
    ):
        """Initializes a new SpotifyService.

        Args:
            session (Session): The database session to use, typically injected by FastAPI.
        """
        self._session = session

        self._request_session = RequestSession()

        retries = Retry(
            total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504]
        )

        self._request_session.mount("https://", HTTPAdapter(max_retries=retries))

    def get_access_token(self, user: User) -> str:
        user_entity = (
            self._session.query(UserEntity).filter(UserEntity.id == user.id).one()
        )

        return user_entity.spotify_access_token

    def refresh_token(self, user: User) -> str:
        request_string = getenv("CLIENT_ID") + ":" + getenv("CLIENT_SECRET")
        encoded_bytes = base64.b64encode(request_string.encode("utf-8"))
        encoded_string = str(encoded_bytes, "utf-8")
        headers = {
            "content-type": "application/x-www-form-urlencoded",
            "Authorization": "Basic " + encoded_string,
        }

        user_entity = (
            self._session.query(UserEntity).filter(UserEntity.id == user.id).one()
        )

        form_data = {
            "grant_type": "refresh_token",
            "refresh_token": user_entity.spotify_refresh_token,
        }

        url = "https://accounts.spotify.com/api/token"

        response = self._request_session.post(url, data=form_data, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Error with refresh token")

        else:
            data = response.json()

            user_entity.spotify_access_token = data["access_token"]
            if "refresh_token" in data:
                user_entity.spotify_refresh_token = data["refresh_token"]

            self._session.commit()

    def get_song(self, song_id: str, user: User):
        url = f"https://api.spotify.com/v1/tracks/{song_id}"

        res = self._request_session.get(
            url, headers={"Authorization": f"Bearer {user.spotify_access_token}"}
        )
        data = res.json()

        return SongEntity(
            spotify_uri="spotify://" + song_id,
            duration_ms=int(data["duration_ms"]),
            title=data["name"],
            artists=[a["name"] for a in data["artists"]],
            album=data["album"]["name"],
            cover_url=data["album"]["images"][0]["url"],
        )
