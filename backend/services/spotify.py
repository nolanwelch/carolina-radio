import base64
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException

from requests.adapters import HTTPAdapter, Retry

from sqlalchemy.orm import Session
from requests import Session as RequestSession
from backend.env import getenv
from backend.models.artist import Artist
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
    ):
        """Initializes a new SpotifyService.

        Args:
            session (Session): The database session to use, typically injected by FastAPI.
        """

        self._request_session = RequestSession()

        retries = Retry(
            total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504]
        )

        self._request_session.mount("https://", HTTPAdapter(max_retries=retries))

    def get_token(self, type: str):
        with open(type, "r") as token_file:
            return token_file.readline()

    def set_token(self, type: str, value: str):
        with open(type, "w") as token_file:
            token_file.write(value)

    def refresh_token(self) -> str:
        request_string = getenv("CLIENT_ID") + ":" + getenv("CLIENT_SECRET")
        encoded_bytes = base64.b64encode(request_string.encode("utf-8"))
        encoded_string = str(encoded_bytes, "utf-8")
        headers = {
            "content-type": "application/x-www-form-urlencoded",
            "Authorization": "Basic " + encoded_string,
        }

        form_data = {
            "grant_type": "refresh_token",
            "refresh_token": self.get_token("refresh"),
        }

        url = "https://accounts.spotify.com/api/token"

        response = self._request_session.post(url, data=form_data, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Error with refresh token")

        else:
            data = response.json()

            self.set_token("access", data["access_token"])
            if "refresh_token" in data:
                self.set_token("refresh", data["refresh_token"])

            self._session.commit()

    def queue_song(self, song_id: str):
        url = "https://api.spotify.com/v1/me/player/queue"
        res = self._request_session.post(
            url,
            params={"uri": f"spotify:track:{song_id}"},
            headers={"Authorization": f"Bearer {self.get_token("access")}"},
        )

        if res.status_code == 401:
            self.refresh_token()

            res = self._request_session.post(
                url,
                params={"uri": f"spotify:track:{song_id}"},
                headers={"Authorization": f"Bearer {self.get_token("access")}"},
            )
        print(res.status_code, res.text)

    def get_song(self, query: str):
        url = "https://api.spotify.com/v1/search"
        response = self._request_session.get(
            url,
            params={
                "q": query,
                "type": "track",
                "market": "US",
            },
            headers={"Authorization": f"Bearer {self.get_token("access")}"},
        )

        if response.status_code == 401:
            self.refresh_token()

            response = self._request_session.get(
                url,
                params={
                    "q": query,
                    "type": "track",
                    "market": "US",
                },
                headers={"Authorization": f"Bearer {self.get_token("access")}"},
            )

        tracks = response.json()["tracks"]["items"]

        print(tracks[0])

        return [
            Song(
                songId=t["id"],
                durationMs=t["duration_ms"] if "duration_ms" in t else -1,
                title=t["name"],
                artists=[Artist(id=0, name=a["name"]) for a in t["artists"]],
                album=t["album"]["name"],
                coverUrl=t["album"]["images"][0]["url"],
            )
            for t in tracks
        ]
