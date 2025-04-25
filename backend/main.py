import asyncio
import base64
import random
import string
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode
import uuid

import requests
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.entities.song_entity import SongEntity
from backend.entities.song_request_entity import RequestStatus, SongRequestEntity
from backend.models.pool_entry import PoolEntry
from backend.models.song import Song
from backend.models.song_request import SongRequest
from fastapi.middleware.gzip import GZipMiddleware

from env import getenv

QUEUE_SIZE = getenv("QUEUE_SIZE")


last_start_time = datetime.now()


@asynccontextmanager
async def lifespan(api: FastAPI):
    task = asyncio.create_task(queue_updater())

    yield  # go go gadget api

    # stop the background task on shutdown
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


async def queue_updater():
    try:
        while True:
            sleep_s = await update_radio_queue()
            print("Sleeping")
            await asyncio.sleep(sleep_s)
    except asyncio.CancelledError:
        pass


async def update_radio_queue():
    pool_collection = db["songPool"]

    # handle case where queue is empty
    if pool_collection.find_one({"position": 0}) is None:
        with client.start_session() as session:
            with session.start_transaction():
                pool_collection.update_many({}, {"$set": {"position": -1}})
                entries = pool_collection.find().sort("entryId", 1).to_list()
                for i, entry in enumerate(entries[: min(len(entries), QUEUE_SIZE)]):
                    print(i)
                    e = PoolEntry.model_validate(entry)
                    pool_collection.find_one_and_update(
                        {"entryId": e.entryId}, {"$set": {"position": i + 1}}
                    )

    # pop from radio queue, move other songs up
    global last_start_time
    current_time = datetime.now()
    last_start_time = current_time
    pool_collection.find_one_and_update(
        filter={"position": 0},
        update={
            "$set": {
                "position": -1,
                "votes": 0,
                "lastPlayedDT": current_time,
            },
            "$unset": {"poolJoinDT": ""},
        },
    )
    pool_collection.update_many(
        filter={"position": {"$ne": -1}},
        update={"$inc": {"position": -1}},
    )

    print(connected_users)

    for userURI in connected_users:
        url = "https://api.spotify.com/v1/me/player/queue"
        print(get_user_by_uri(userURI).accessToken)
        print(pool_collection.find_one({"position": 2}))
        resp = request_with_retry(
            "POST",
            url,
            get_user_by_uri(userURI),
            {
                "uri": f"spotify:track:{pool_collection.find_one({'position': 2})['song']['songId']}"
            },
        )
        print(resp.status_code)

    # get maximum position in queue
    pipeline = [
        {"$match": {"position": {"$ne": -1}}},
        {"$group": {"_id": None, "max_value": {"$max": "$position"}}},
    ]
    positions = list(pool_collection.aggregate(pipeline))
    max_pos = int(positions[0]["max_value"]) if positions else 0

    # choose next song via raffle method
    data = pool_collection.find(
        {
            "position": {"$eq": -1},
            "votes": {"$gt": 0},
        }
    )
    entries = [PoolEntry.model_validate(d) for d in data]
    if entries:
        next_id = choose_next_song(entries)
        # add next song to end of queue
        pool_collection.find_one_and_update(
            filter={"songId": next_id}, update={"$set": {"position": max_pos + 1}}
        )

    # update wait time to match new top of queue
    result = pool_collection.find_one({"position": 0})
    if result is not None:
        current_song = PoolEntry.model_validate(result)
        return current_song.song.durationMs // 1000
    return 60


description = """
Welcome to the Carolina Radio RESTful Application Programming Interface.
"""

# Metadata to improve the usefulness of OpenAPI Docs /docs API Explorer
app = FastAPI(
    title="Carolina Radio API",
    version="0.1.0",
    description=description,
    openapi_tags=[],
)

# Use GZip middleware for compressing HTML responses over the network
app.add_middleware(GZipMiddleware)


origins = [
    "https://carolinaradio.tech",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class UserSession(BaseModel):
    startDT: datetime
    userUri: str
    accessToken: str = None
    refreshToken: str = None
    sessionId: str = Field(default_factory=lambda: str(uuid.uuid4()))


uri = os.environ.get("MONGO_URI")
client = MongoClient(uri, server_api=ServerApi("1"))
client.admin.command("ping")
db = client["CarolinaRadio"]


N_VOTES_BIAS = 3
TIME_SINCE_PLAYED_BIAS = 1e-3
TIME_IN_POOL_BIAS = 1e-4


def request_with_retry_using_req(
    mode: str, url: str, req: Request, params: dict = {}
) -> Response:
    try:
        ses = get_user_session(req.cookies)
    except HTTPException:
        return RedirectResponse("/login")
    return request_with_retry(mode, url, ses, params)


def _do_request(mode: str, url: str, accessToken: str, params: dict = {}) -> Response:
    print(mode, url, params, accessToken)
    return requests.request(
        mode.upper(),
        url,
        params=params,
        headers={"Authorization": f"Bearer {accessToken}"},
    )


def request_with_retry(
    mode: str, url: str, ses: UserSession, params: dict = {}
) -> Response:
    response = _do_request(mode, url, ses.accessToken, params)
    if response.status_code == 401:
        print("Refreshing token")
        refresh_token(ses)
        response = _do_request(
            mode, url, get_user_by_uri(ses.userUri).accessToken, params
        )
    if not response.ok:
        raise HTTPException(500, f"[{response.status_code}] {response.reason}")

    return response


connected_users = []


def choose_next_song(session: Session) -> SongRequestEntity | None:
    song_requests = session.query(SongRequestEntity).filter(
        SongRequestEntity.status == RequestStatus.REQUESTED
    )

    if not song_requests:
        return None

    weighted_songs = []
    current_dt = datetime.now(timezone.utc)

    for req in song_requests:
        song = req.song

        votes = song.vote_count
        time_since_played = (
            (current_dt - song.last_played).total_seconds()
            if song.last_played
            else float("inf")
        )
        time_in_pool = (current_dt - req.time_created).total_seconds()

        weight = (
            votes * N_VOTES_BIAS
            + time_since_played * TIME_SINCE_PLAYED_BIAS
            + time_in_pool * TIME_IN_POOL_BIAS
        )
        weighted_songs.append((req, weight))

    total_weight = sum(weight for _, weight in weighted_songs)
    choice = random.uniform(0, total_weight)

    cumulative_weight = 0
    for req, weight in weighted_songs:
        cumulative_weight += weight
        if cumulative_weight >= choice:
            return req

    return None


def get_user_session(session: Session, cookies: dict[str, str]) -> UserSession:
    session_id = cookies.get("sessionId")
    if session_id is not None:
        user_session = (
            session.query(UserSession)
            .filter(UserSession.session_id == session_id)
            .order_by(UserSession.start_time.desc())
            .first()
        )

        if user_session is None:
            raise HTTPException(status_code=401)

        current_dt = datetime.now(timezone.utc)
        if (current_dt - user_session.start_time).total_seconds() > (60 * 60):
            raise HTTPException(status_code=401)

        return user_session

    raise HTTPException(status_code=401)


interval_seconds = 60


def set_interval(new_int: int):
    global interval_seconds
    interval_seconds = new_int


def get_user_by_uri(session: Session, uri: str) -> UserSession:
    user = session.query(UserEntity).filter(UserEntity.spotify_uri == uri).first()
    if user is None or not user.sessions:
        raise HTTPException(404, "User not found")
    sessions = user.sessions
    sessions.sort(UserSession.start_time, reverse=True)
    return sessions[0]
