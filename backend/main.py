import base64
import math
import os
import random
from dataclasses import dataclass
from urllib.parse import urlencode

import dotenv
import numpy as np
import pandas as pd
import requests
from pydantic import BaseModel
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from fastapi import FastAPI, Response, Request, HTTPException, Depends, status
from fastapi.responses import RedirectResponse, HTMLResponse
api = FastAPI()

dotenv.load_dotenv()


@dataclass
class UserVote:
    tickets: int
    uri: str

class SongRequest(BaseModel):
    datetime: str
    songId: str
    userId: str


class Song(BaseModel):
    spotifyUri: str
    lengthMs: int
    title: str
    artists: list[str]
    album: str
    coverUrl: str


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


def choose_next_song(votes: UserVote):
    df = pd.DataFrame(votes)
    df["tickets"] = df.apply(
        lambda row: get_ticket_count(
            row["votes"], row["timeSincePlayed"], row["timeInPool"]
        )
    )
    total_tickets = df["tickets"].sum()
    df["probability"] = df["tickets"] / total_tickets
    song_uri = np.random.choice(df["uri"], 1, p=df["probability"])[0]
    return str(song_uri)

@api.get("/login")
def read_root():
    state = generate_random_string(20)
    scope = "user-read-playback-state user-modify-playback-state user-read-currently-playing"

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
    return response

@api.get("/callback")
def callback(request: Request, response: Response):

    code = request.query_params["code"]
    state = request.query_params["state"]
    stored_state = request.cookies.get(os.environ.get("STATE_KEY"))

    if state == None or state != stored_state:
        raise HTTPException(status_code=400, detail="State mismatch")
    else:

        url = "https://accounts.spotify.com/api/token"
        request_string = os.environ.get("CLIENT_ID") + ":" + os.environ.get("CLIENT_SECRET")
        encoded_bytes = base64.b64encode(request_string.encode("utf-8"))
        encoded_string = str(encoded_bytes, "utf-8")
        header = {
            "content-type": "application/x-www-form-urlencoded",
            "Authorization": "Basic " + encoded_string
            }

        form_data = {
            "code": code,
            "redirect_uri": os.environ.get("REDIRECT_URI"),
            "grant_type": "authorization_code",
        }

        api_response = requests.post(url, data=form_data, headers=header)

        if api_response.status_code == 200:
            data = api_response.json()
            access_token = data["access_token"]
            refresh_token = data["refresh_token"]

            response = RedirectResponse(url=os.environ.get("URI"))
            response.set_cookie(key="accessToken", value=access_token)
            response.set_cookie(key="refreshToken", value=refresh_token)

        return response

@api.get("/refresh_token")
def refresh_token(request: Request):
    refresh_token = request.cookies.get("refreshToken")
    request_string = os.environ.get("CLIENT_ID") + ":" + os.environ.get("CLIENT_SECRET")
    encoded_bytes = base64.b64encode(request_string.encode("utf-8"))
    encoded_string = str(encoded_bytes, "utf-8")
    header = {
            "content-type": "application/x-www-form-urlencoded",
            "Authorization": "Basic " + encoded_string
            }

    form_data = {"grant_type": "refresh_token", "refresh_token": refresh_token}

    url = "https://accounts.spotify.com/api/token"

    response = requests.post(url, data=form_data, headers=header)
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


@api.post("/request/")
def create_request(request: SongRequest):
    songs_collection = db["songs"]
    song_metadata = songs_collection.find_one({"spotifyId": request.songId})
    if not song_metadata:
        data = get_song_data(request.songId)
        if data is None:
            return None
        song_data = Song(
            request.songId,
            data["durationMs"],
            data["name"],
            data["artists"],
            data["album"]["name"],
            data["album"]["images"][0]["url"],
        )
        # insert song data to songs collection
        songs_collection.insert_one(song_data)
    req_collection = db["requests"]
    req_collection.insert_one(request)


def get_song_data(song_id: str):
    url = f"https://api.spotify.com/v1/tracks/{song_id}"
    req = requests.get(url)
    if req.status_code != 200:
        return None
    data = req.json()

    data["durationMs"] = get_song_duration(song_id)

    return data


@api.get("/search/")
def get_songs(q: str):
    access_token = q.cookies.get("accessToken")

    url = "https://api.spotify.com/v1/search/"
    req = requests.get(
        url,
        params={
            "q": q,
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
            t["id"],
            get_song_duration(t["id"]),
            t["name"],
            t["artists"],
            t["album"]["name"],
            t["album"]["images"][0]["url"],
        )
        for t in tracks
    ]


async def get_current_token(request: Request):
    token = request.cookies.get("accessToken")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token is missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Optionally, add logic to verify or decode the token here
    return token


def get_song_duration(song_id: str, token: str = Depends(get_current_token)):
    url = f"https://api.spotify.com/v1/audio-features/{song_id}"
    req = requests.get(
        url,
    )
    if req.status_code != 200:
        return None
    return int(req.json()["duration_ms"])


def generate_random_string(string_length):
    possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    text = "".join(
        [
            possible[math.floor(random.random() * len(possible))]
            for i in range(string_length)
        ]
    )
    return text

def main():
    dotenv.load_dotenv()
    votes = [UserVote(1, "test"), UserVote(1, "test2"), UserVote(2, "test3")]
    # print(choose_next_song(votes))


if __name__ == "__main__":
    main()