from http.client import HTTPException
from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy import func

from backend.api.authentication import registered_user
from backend.database import db_session
from backend.entities.song_entity import SongEntity
from backend.entities.song_request_entity import SongRequestEntity
from backend.models.song import Song
from backend.models.user import User
from backend.services.queue import QueueService

__authors__ = [
    "David Foss",
    "Gabrian Chua",
    "Rohan Kashyap",
    "Nolan Welch",
]
__copyright__ = "Copyright 2025"
__license__ = "MIT"


api = APIRouter(prefix="/api/auth")
openapi_tags = {
    "name": "Queue",
    "description": "Operations related to the song queue.",
}


@api.get("/requests")
async def get_user_requests() -> list[Song]:
    try:
        ses = get_user_session(db, request.cookies)

        requests = (
            db.query(SongRequestEntity)
            .filter(SongRequestEntity.user_id == ses.user_id)
            .order_by(SongRequestEntity.time_created)
            .all()
        )
        songs = [req.song for req in requests]
        return songs
    except HTTPException:
        return RedirectResponse("/login")


@api.post("/request")
async def create_request(
    requested_song: Song,
    user: User = Depends(registered_user),
    queue_svc: QueueService = Depends(),
    spotify_svc: SpotifyService = Depends()
):
    song = 
    song = (
        self._session.query(SongEntity)
        .filter(SongEntity.spotify_uri == requested_song.id)
        .first()
    )
    if song is None:  # song not in database, insert it
        song = get_song_data(song_id, ses)
        if song is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Song {song_id} not found")
        db.add(song)
        db.commit()

    new_req = SongRequestEntity(song=song, user=ses.user)
    db.add(new_req)
    db.commit()

    # get number of songs in queue
    n_queued = (
        db.query(func.count(SongRequestEntity.id))
        .filter(SongRequestEntity.queue_position.isnot(None))
        .scalar()
    )
    queue_pos = n_queued if n_queued < QUEUE_SIZE else None
    # add to queue at lowest position
    new_entry = SongRequestEntity(
        song=song,
        user=ses,
        queue_position=queue_pos,  # for N queued songs, the Nth position is empty
    )
    db.add(new_entry)
    db.commit()

    return Response(status_code=201)


@api.get("/search")
async def get_songs(req: Request):
    query = req.query_params.get("q")

    url = "https://api.spotify.com/v1/search"
    response = request_with_retry_using_req(
        "get",
        url,
        req,
        {
            "q": query,
            "type": "track",
            "market": "US",
        },
    )

    if response is RedirectResponse:
        return response
    tracks = response.json()["tracks"]["items"]

    return [
        Song(
            songId=t["id"],
            durationMs=t["duration_ms"] if "duration_ms" in t else -1,
            title=t["name"],
            artists=[a["name"] for a in t["artists"]],
            album=t["album"]["name"],
            coverUrl=t["album"]["images"][0]["url"],
        )
        for t in tracks
    ]


@api.get("/queue")
async def fetch_queue(queue_svc: QueueService = Depends()) -> list[Song]:
    songs = get_queue(db)
    return songs
