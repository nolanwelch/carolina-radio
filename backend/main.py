import base64
import json
import math
import os
import random
from dataclasses import dataclass
from urllib.parse import urlencode
import uuid

import dotenv
import numpy as np
import asyncio
import pandas as pd
from fastapi_restful.tasks import repeat_every
from datetime import datetime, timedelta
import requests
from pydantic import BaseModel, Field
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from fastapi import FastAPI, Response, Request, HTTPException, Depends, status
from fastapi.responses import RedirectResponse, HTMLResponse
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

QUEUE_SIZE = 5


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
        print(pool_collection.find_one({'position': 2}))
        resp = request_with_retry("POST", url, get_user_by_uri(userURI), {
                "uri": f"spotify:track:{pool_collection.find_one({'position': 2})['song']['songId']}"})
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


api = FastAPI(lifespan=lifespan)


@api.get("/fuck")
async def fuck(_: Request):
    test = await update_radio_queue()
    print(test)


origins = [
    "https://carolinaradio.tech",
    "http://localhost:3000",
]

api.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

dotenv.load_dotenv()


class Song(BaseModel):
    songId: str
    artists: list[str]
    album: str
    title: str
    coverUrl: str
    durationMs: int


class NowPlayingSong(Song):
    position: float


class UserSession(BaseModel):
    startDT: datetime
    userUri: str
    accessToken: str = None
    refreshToken: str = None
    sessionId: str = Field(default_factory=lambda: str(uuid.uuid4()))


class SongRequest(BaseModel):
    requestDT: datetime
    song: Song
    userUri: str


class PoolEntry(BaseModel):
    entryId: str = Field(default_factory=lambda: str(uuid.uuid4()))
    position: int = -1
    song: Song
    startDT: datetime = datetime.fromtimestamp(0)
    votes: int
    lastPlayedDT: datetime = datetime.fromtimestamp(0)
    poolJoinDT: datetime = datetime.fromtimestamp(0)


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


def get_ticket_count(n_votes, time_since_played_s, time_in_pool_s):
    return (
        N_VOTES_BIAS * n_votes
        + TIME_SINCE_PLAYED_BIAS * time_since_played_s
        + TIME_IN_POOL_BIAS * time_in_pool_s
    )


def choose_next_song(entries: PoolEntry):
    curr_time = datetime.now()
    entry_tickets = []
    for entry in entries:
        last_played = entry.lastPlayedDT or curr_time
        time_since_played = (curr_time - last_played).total_seconds()
        entered_pool = entry.poolJoinDT or curr_time
        time_since_entry = (curr_time - entered_pool).total_seconds()
        entry_tickets.append(
            get_ticket_count(entry.votes, time_since_played, time_since_entry)
        )
    total_tickets = sum([e for e in entry_tickets])
    probs = [t / total_tickets for t in entry_tickets]
    ids = [e.song.songId for e in entries]
    print(ids, probs)
    song_uri = np.random.choice(ids, 1, p=probs)[0]
    return str(song_uri)


def get_user_session(cookies: dict[str, str]):
    session_id = cookies.get("sessionId")
    if session_id is not None:
        ses_collection = db["sessions"]
        result = ses_collection.find({"sessionId": session_id}).sort("startDT", -1)
        if result is None:
            raise HTTPException(status_code=401)
        session = UserSession.model_validate(list(result)[0])
        if (datetime.now() - session.startDT).total_seconds() > (60 * 60):
            raise HTTPException(status_code=401)

        return session

    raise HTTPException(status_code=401)


@api.get("/login")
async def read_root():
    state = generate_random_string(20)
    scope = "user-read-private user-read-playback-state user-modify-playback-state user-read-currently-playing user-read-email"

    params = {
        "response_type": "code",
        "client_id": os.environ.get("CLIENT_ID"),
        "scope": scope,
        "redirect_uri": os.environ.get("REDIRECT_URI"),
        "state": state,
    }
    response = RedirectResponse(
        url="https://accounts.spotify.com/authorize?" + urlencode(params)
    )
    response.set_cookie(key=os.environ.get("STATE_KEY"), value=state)
    response.set_cookie(
        "sessionId",
    )
    return response


@api.get("/callback")
async def callback(request: Request, response: Response):
    code = request.query_params["code"]
    state = request.query_params["state"]
    stored_state = request.cookies.get(os.environ.get("STATE_KEY"))

    if state is None or state != stored_state:
        raise HTTPException(status_code=400, detail="State mismatch")
    else:
        url = "https://accounts.spotify.com/api/token"
        request_string = (
            os.environ.get("CLIENT_ID") + ":" + os.environ.get("CLIENT_SECRET")
        )
        encoded_bytes = base64.b64encode(request_string.encode("utf-8"))
        encoded_string = str(encoded_bytes, "utf-8")
        headers = {
            "content-type": "application/x-www-form-urlencoded",
            "Authorization": "Basic " + encoded_string,
        }

        form_data = {
            "code": code,
            "redirect_uri": os.environ.get("REDIRECT_URI"),
            "grant_type": "authorization_code",
        }

        api_response = requests.post(url, data=form_data, headers=headers)

        if api_response.status_code == 200:
            data = api_response.json()
            access_token = data["access_token"]
            refresh_token = data["refresh_token"]

            url = "https://api.spotify.com/v1/me"
            req = requests.get(
                url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                },
            )
            if req.status_code != 200:
                raise HTTPException(req.status_code, req.reason)
            data = req.json()
            response = RedirectResponse(url=os.environ.get("URI"))
            if data["product"] != "premium":
                return response
            if data["explicit_content"]["filter_enabled"]:
                return response
            if data["explicit_content"]["filter_locked"]:
                return response

            ses_collection = db["sessions"]
            session = UserSession(
                startDT=datetime.now(),
                userUri=data["uri"],
                accessToken=access_token,
                refreshToken=refresh_token,
            )
            ses_collection.insert_one(session.model_dump())

            response.set_cookie(key="sessionId", value=session.sessionId)

        return response


@api.put("/join")
def connect(req: Request):
    try:
        ses = get_user_session(req.cookies)
        access_token = ses.accessToken
    except HTTPException:
        return RedirectResponse("/login")
    
    url = "https://api.spotify.com/v1/me/player/play"
    songs = get_queue()
    currentSong, pos_ms = now_playing()
    req = requests.put(
        url,
        json = {
            "uris": [f"spotify:track:{currentSong.songId}"],
            "position_ms": int(pos_ms)
        },
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    )
    if req.status_code != 204:
        raise HTTPException(req.status_code, req.reason)
    print(songs)
    url = "https://api.spotify.com/v1/me/player/queue"
    req = requests.post(
        url,
        params={"uri": f"spotify:track:{songs[0].songId}"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    print("test1", req.status_code, access_token)
    if req.status_code != 200:
        raise HTTPException(req.status_code, req.reason)
    req = requests.post(
        url,
        params={"uri": f"spotify:track:{songs[1].songId}"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    print("test2")
    if req.status_code != 200:
        raise HTTPException(req.status_code, req.reason)
    if ses.userUri not in connected_users:
        connected_users.append(ses.userUri)
    print(ses.userUri)
    print("------------")
    print(connected_users)
    

def refresh_token(ses: UserSession):
    request_string = os.environ.get("CLIENT_ID") + ":" + os.environ.get("CLIENT_SECRET")
    encoded_bytes = base64.b64encode(request_string.encode("utf-8"))
    encoded_string = str(encoded_bytes, "utf-8")
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "Authorization": "Basic " + encoded_string,
    }

    form_data = {"grant_type": "refresh_token", "refresh_token": refresh_token}

    url = "https://accounts.spotify.com/api/token"

    response = requests.post(url, data=form_data, headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Error with refresh token")
    else:
        data = response.json()
        new_ses = ses.model_copy()
        new_ses["accessToken"] = data["access_token"]
        new_ses = datetime.now()
        if "refresh_token" in data:
            new_ses["refreshToken"] = data["refresh_token"]

        user_collection = db["sessions"]
        user_collection.delete_many({"userUri": ses.userUri})
        user_collection.insert_one(new_ses)


@api.get("/request")
async def get_user_requests(request: Request) -> list[Song]:
    try:
        ses = get_user_session(request.cookies)

        pool_collection = db["requests"]
        queue = pool_collection.find({"userUri": {"$eq": ses.userUri}}).sort(
            "requestDT", 1
        )
        songs = [Song.model_validate(s["song"]) for s in queue]
        return songs
    except HTTPException:
        return RedirectResponse("/login")


@api.post("/request")
async def create_request(request: Request):
    try:
        ses = get_user_session(request.cookies)
    except HTTPException:
        return RedirectResponse("/login")

    data = await request.json()
    song_id = data.get("songId")
    songs_collection = db["songs"]
    song_metadata = songs_collection.find_one({"songId": song_id})
    if not song_metadata:
        song = get_song_data(song_id, ses)
        if song is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Song {song_id} not found")
        songs_collection.insert_one(song.model_dump())

    req_collection = db["requests"]
    song = Song.model_validate(songs_collection.find_one({"songId": song_id}))
    new_req = SongRequest(requestDT=datetime.now(), song=song, userUri=ses.userUri)
    req_collection.insert_one(new_req.model_dump())

    pool_collection = db["songPool"]
    with client.start_session() as session:
        with session.start_transaction():
            # get number of songs in queue
            n_queued = pool_collection.count_documents({"position": {"$ne": -1}})
            if n_queued < QUEUE_SIZE:
                # add to queue at lowest position
                new_entry = PoolEntry(
                    song=song,
                    votes=1,
                    spotifyUri=song_id,
                    poolJoinDT=datetime.now(),
                    position=n_queued,  # for N queued songs, the Nth position is empty
                )
                pool_collection.insert_one(new_entry.model_dump())
                return

    pool_song = pool_collection.find_one({"songId": song_id})
    if pool_song is None:
        new_entry = PoolEntry(
            song=song,
            votes=1,
            spotifyUri=song_id,
            poolJoinDT=datetime.now(),
            position=-1,
        )
        pool_collection.insert_one(new_entry.model_dump())
    else:
        pool_collection.find_one_and_update(
            {"song": song}, update={"votes": {"$inc": 1}}
        )


def get_song_data(song_id: str, ses: UserSession):
    url = f"https://api.spotify.com/v1/tracks/{song_id}"
    req = request_with_retry("get", url, ses)
    data = req.json()

    return Song(
        songId=song_id,
        durationMs=int(data["duration_ms"]) or -1,
        title=data["name"],
        artists=[a["name"] for a in data["artists"]],
        album=data["album"]["name"],
        coverUrl=data["album"]["images"][0]["url"],
    )


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
    
# TODO: Delete
# @api.put("/start_resume")
# async def play_song(req: Request):
#     try:
#         ses = get_user_session(req.cookies)
#         access_token = ses.accessToken
#     except HTTPException:
#         return RedirectResponse("/login")
    
#     url = "https://api.spotify.com/v1/me/player/play"
#     songs = get_queue()
#     currentSong, pos_ms = now_playing()
#     req = requests.put(
#         url,
#         json = {
#             "uris": [f"spotify:track:{currentSong.songId}"] + [f"spotify:track:{s.songId}" for s in songs[:min(len(songs), 2)]],
#             "position_ms": int(pos_ms)
#         },
#         headers={
#             "Authorization": f"Bearer {access_token}",
#             "Content-Type": "application/json"
#         }
#     )
#     if req.status_code != 204:
#         raise HTTPException(req.status_code, req.reason)
#     return req


# TODO: Delete
@api.post("/spotify_queue")
async def db_to_spot_queue(req: Request):
    try:
        ses = get_user_session(req.cookies)
        access_token = ses.accessToken
    except HTTPException:
        return RedirectResponse("/login")

    url = "https://api.spotify.com/v1/me/player/queue"
    req = requests.post(
        url,
        params={"uri": "spotify:track:05JVoLLLqyHmMYrgpOOGNx"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    if req.status_code != 204:
        raise HTTPException(req.status_code, req.reason)
    return req


def now_playing():
    global last_start_time
    pool_collection = db["songPool"]
    result = pool_collection.find_one({"position": 0})
    if result is None:
        raise HTTPException(status_code=404)
    top_song = PoolEntry.model_validate(result)

    pos_ms = (datetime.now() - last_start_time) / timedelta(milliseconds=1)
    return Song.model_validate(top_song.song), pos_ms


@api.get("/playing")
async def get_now_playing() -> NowPlayingSong:
    try:
        song, pos = now_playing()
    except HTTPException:
        return Response(status_code=404)

    

    return NowPlayingSong(songId=song.songId, artists=song.artists, album=song.album, title=song.title, coverUrl=song.coverUrl, durationMs=song.durationMs, position=pos)


def generate_random_string(string_length):
    possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    text = "".join(
        [
            possible[math.floor(random.random() * len(possible))]
            for i in range(string_length)
        ]
    )
    return text


interval_seconds = 60


def set_interval(new_int):
    global interval_seconds
    interval_seconds = new_int


# TODO: Delete
@api.post("/db_to_spot_queue")
def queue_song_for_user(req: Request):
    url = "https://api.spotify.com/v1/me/player/queue"

    res = request_with_retry_using_req(
        "post", url, req, {"uri": "spotify:track:6BJHsLiE47Sk0wQkuppqhr"}
    )

    if res.status_code == 404:
        pass  # TODO: Rohan, remove user from active user list at this point
    elif res.status_code != 204:
        raise HTTPException(req.status_code, req.reason)
    return res


def get_user_by_uri(uri: str) -> UserSession:
    ses_collection = db["sessions"]
    user = ses_collection.find_one(filter={"userUri": uri})
    if user is None:
        raise HTTPException(404, "User not found")
    return UserSession.model_validate(user)


def get_queue():
    pool_collection = db["songPool"]
    queue = pool_collection.find({"position": {"$gt": 0}}).sort("position", 1)
    songs = [Song.model_validate(s["song"]) for s in queue]
    return songs


@api.get("/queue")
async def fetch_queue() -> list[Song]:
    songs = get_queue()
    return songs