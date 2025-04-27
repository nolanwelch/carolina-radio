from http.client import HTTPException

from pydantic import BaseModel
from backend.services.spotify import SpotifyService
from fastapi import APIRouter, Depends, Response, Request
from fastapi.responses import RedirectResponse

from backend.models.song import Song
from backend.models.user import User

__authors__ = [
    "David Foss",
    "Gabrian Chua",
    "Rohan Kashyap",
    "Nolan Welch",
]
__copyright__ = "Copyright 2025"
__license__ = "MIT"


api = APIRouter(prefix="/api/playback")
openapi_tags = {
    "name": "Queue",
    "description": "Operations related to the song queue.",
}


class SongRequest(BaseModel):
    songId: str


@api.post("/request")
async def create_request(
    song_request: SongRequest, spotify_svc: SpotifyService = Depends()
):
    spotify_svc.queue_song(song_request.songId)

    return Response(status_code=201)


class SearchQuery(BaseModel):
    query: str


@api.get("/search")
async def get_songs(query: str, spotify_svc: SpotifyService = Depends()) -> list[Song]:
    return spotify_svc.get_song(query)
