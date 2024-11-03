import base64
import math
import os
import random
from dataclasses import dataclass
from urllib.parse import urlencode
from uuid import uuid4

import dotenv
import numpy as np
import pandas as pd
from fastapi_restful.tasks import repeat_every
from datetime import datetime, timedelta
import requests
from pydantic import BaseModel
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from fastapi import FastAPI, Response, Request, HTTPException, Depends, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
api = FastAPI()

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


class UserSession(BaseModel):
    startDT: datetime
    userUri: str
    accessToken: str = None
    refreshToken: str = None
    sessionId: str = str(uuid4())


class SongRequest(BaseModel):
    requestDT: datetime
    song: Song
    userUri: str


class PoolEntry(BaseModel):
    position: int = None
    song: Song
    startDT: datetime = None
    votes: int
    lastPlayedDT: datetime = None
    poolJoinDT: datetime = None

def get_db():
    uri = os.environ.get("MONGO_URI")
    client = MongoClient(uri, server_api=ServerApi("1"))
    client.admin.command("ping")
    return client["CarolinaRadio"]


db = get_db()

N_VOTES_BIAS = 3
TIME_SINCE_PLAYED_BIAS = 1e-3
TIME_IN_POOL_BIAS = 1e-4


def get_ticket_count(n_votes, time_since_played_s, time_in_pool_s):
    return (
        N_VOTES_BIAS * n_votes
        + TIME_SINCE_PLAYED_BIAS * time_since_played_s
        + TIME_IN_POOL_BIAS * time_in_pool_s
    )


def choose_next_song(entries: PoolEntry):
    df = pd.DataFrame(entries)
    curr_time = datetime.now()
    df["timeSincePlayed"] = curr_time - df["lastPlayedDT"]
    df["timeInPool"] = curr_time - df["poolJoinDT"]
    df["tickets"] = df.apply(
        lambda row: get_ticket_count(
            row["votes"], row["timeSincePlayed"], row["timeInPool"]
        )
    )
    total_tickets = df["tickets"].sum()
    df["probability"] = df["tickets"] / total_tickets
    song_uri = np.random.choice(df["uri"], 1, p=df["probability"])[0]
    return str(song_uri)


def get_user_session(cookies: dict[str, str]):
    session_id = cookies.get("sessionId")
    if session_id is not None:
        ses_collection = db["sessions"]
        session = UserSession.model_validate(
            ses_collection.find_one({"sessionId": session_id})
        )
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
        request_string = os.environ.get("CLIENT_ID") + ":" + os.environ.get("CLIENT_SECRET")
        encoded_bytes = base64.b64encode(request_string.encode("utf-8"))
        encoded_string = str(encoded_bytes, "utf-8")
        headers = {
            "content-type": "application/x-www-form-urlencoded",
            "Authorization": "Basic " + encoded_string
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
                    "Content-Type": "application/json"
                }
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

def refresh_token(request: Request):
    try:
        ses = get_user_session(request.cookies)
        refresh_token = ses.refreshToken
    except HTTPException:
        return RedirectResponse("/login")
    request_string = os.environ.get("CLIENT_ID") + ":" + os.environ.get("CLIENT_SECRET")
    encoded_bytes = base64.b64encode(request_string.encode("utf-8"))
    encoded_string = str(encoded_bytes, "utf-8")
    headers = {
            "content-type": "application/x-www-form-urlencoded",
            "Authorization": "Basic " + encoded_string
            }

    form_data = {"grant_type": "refresh_token", "refresh_token": refresh_token}

    url = "https://accounts.spotify.com/api/token"

    response = requests.post(url, data=form_data, headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Error with refresh token")
    else:
        data = response.json()
        access_token = data["access_token"]
        response = HTMLResponse()
        response.set_cookie(key="accessToken",value=access_token)
        if "refresh_token" in data:
            response.set_cookie(key="refreshToken",value=data["refresh_token"])
        return response


@api.get("/request")
async def get_user_requests(request: Request) -> list[Song]:
    try:
        ses = get_user_session(request.cookies)
    
        pool_collection = db["requests"]
        queue = pool_collection.find({"userUri": {"$eq": ses.userUri}}).sort("requestDT", 1)
        songs = [Song.model_validate(s["song"]) for s in queue]
        return songs
    except HTTPException:
        return RedirectResponse("/login")

@api.post("/request")
async def create_request(request: Request):
    try:
        ses = get_user_session(request.cookies)
        access_token = ses.accessToken
    except HTTPException:
        return RedirectResponse("/login")

    data = await request.json()
    song_id = data.get("songId")
    songs_collection = db["songs"]
    song_metadata = songs_collection.find_one({"songId": song_id})
    if not song_metadata:
        song = get_song_data(song_id, access_token)
        if song is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Song {song_id} not found")
        songs_collection.insert_one(song.model_dump())

    req_collection = db["requests"]
    song = Song.model_validate(songs_collection.find_one({"songId": song_id}))
    new_req = SongRequest(requestDT=datetime.now(), song=song, userUri=ses.userUri)
    req_collection.insert_one(new_req.model_dump())

    pool_collection = db["songPool"]
    pool_song = pool_collection.find_one({"songId": song_id})
    if pool_song is None:
        new_entry = PoolEntry(
            song=song,
            votes=1,
            spotifyUri=song_id,
            poolJoinDT=datetime.now(),
        )
        pool_collection.insert_one(new_entry)
    else:
        pool_collection.find_one_and_update(
            {"song": song}, update={"votes": {"$inc": 1}}
        )


def get_song_data(song_id: str, access_token: str):
    url = f"https://api.spotify.com/v1/tracks/{song_id}"
    req = requests.get(
        url,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    if req.status_code != 200:
        return None
    data = req.json()

    return Song(
        songId=song_id,
        durationMs=get_song_duration(song_id, access_token) or -1,
        title=data["name"],
        artists=data["artists"],
        album=data["album"]["name"],
        coverUrl=data["album"]["images"][0]["url"],
    )

@api.get("/search")
async def get_songs(req: Request):
    try:
        ses = get_user_session(req.cookies)
        access_token = ses.accessToken
    except HTTPException:
        return RedirectResponse("/login")

    query = req.query_params.get("q")

    url = "https://api.spotify.com/v1/search/"
    req = requests.get(
        url,
        params={
            "q": query,
            "type": "track",
            "market": "US",
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    if req.status_code != 200:
        raise HTTPException(req.status_code, req.reason)

    tracks = req.json()["tracks"]["items"]

    return [
        Song(
            songId=t["id"],
            durationMs=get_song_duration(t["id"], access_token),
            title=t["name"],
            artists=[a["name"] for a in t["artists"]],
            album=t["album"]["name"],
            coverUrl=t["album"]["images"][0]["url"],
        )
        for t in tracks
    ]
    
@api.put("/start_resume")
async def play_song(req: Request):
    try:
        ses = get_user_session(req.cookies)
        access_token = ses.accessToken
    except HTTPException:
        return RedirectResponse("/login")
    
    url = "https://api.spotify.com/v1/me/player/play"
    req = requests.put(
        url,
        json = {
            "uris":["spotify:track:42VsgItocQwOQC3XWZ8JNA", "spotify:track:66TRwr5uJwPt15mfFkzhbi"],
            "offset": {"position": 0}
        },
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    )
    if req.status_code != 204:
        raise HTTPException(req.status_code, req.reason)
    return req

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
        params = {
            "uri": "spotify:track:05JVoLLLqyHmMYrgpOOGNx"
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    if req.status_code != 204:
        raise HTTPException(req.status_code, req.reason)
    return req

def get_song_duration(song_id: str, access_token: str):
    url = f"https://api.spotify.com/v1/audio-features/{song_id}"
    req = requests.get(
        url,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    if req.status_code != 200:
        return None
    return int(req.json()["duration_ms"])

def now_playing():
    pool_collection = db["songPool"]
    result = pool_collection.find_one({"position": 0})
    if result is None:
        raise HTTPException(status_code=404)
    top_song = PoolEntry.model_validate(result)

    pos_ms = (datetime.now() - top_song.startDT) / timedelta(milliseconds=1)
    return Song.model_validate(top_song["song"]), pos_ms


@api.get("/playing")
async def get_now_playing():
    try:
        song, pos = now_playing()
    except HTTPException:
        return Response(status_code=404)

    return Response(content={"song": song.model_dump(), "position": pos})


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


@repeat_every(seconds=lambda: interval_seconds)
def update_radio_queue():
    pool_collection = db["songPool"]

    # pop from radio queue, move other songs up
    current_time = datetime.now()
    pool_collection.find_one_and_update(
        filter={"position": 0},
        update={
            "position": None,
            "poolJoinDT": None,
            "votes": 0,
            "lastPlayedDT": current_time,
        },
    )
    pool_collection.update_many(
        filter={"position": {"$ne": None}},
        update={"$inc": {"position": -1}},
    )
    # get maximum position in queue
    pipeline = [
        {"$match": {"position": {"$ne": None}}},
        {"$group": {"_id": None, "max_value": {"$max": "$position"}}},
    ]
    positions = list(pool_collection.aggregate(pipeline))
    max_pos = int(positions[0]) if positions else 0

    # update wait time to match new top of queue
    current_song = pool_collection.find_one({"position": 0})
    set_interval(current_song["durationMs"] // 1000)

    # choose next song via raffle method
    data = pool_collection.find(
        {
            "position": {"$eq": None},
            "votes": {"$gt": 0},
        }
    )
    entries = [
        PoolEntry(
            votes=d["votes"],
            lastPlayedTimestamp=d["lastPlayedDT"],
            poolJoinTimestamp=d["poolJoinDT"],
        )
        for d in data
    ]
    next_id = choose_next_song(entries)
    # add next song to end of queue
    pool_collection.find_one_and_update(
        filter={"songId": next_id}, update={"position": max_pos}
    )


update_radio_queue()


def get_queue():
    pool_collection = db["songPool"]
    queue = pool_collection.find({"position": {"$gt": 0}}).sort("position", 1)
    songs = [Song.model_validate(s["song"]) for s in queue]
    return songs


@api.get("/queue")
async def fetch_queue() -> list[Song]:
    songs = get_queue()
    return songs