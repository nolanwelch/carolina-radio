"""Exposes authentication-related operations"""

import random
import string
from urllib.parse import urlencode
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt

from backend.models.user import User
from backend.services.user import UserService

from ..env import getenv

__authors__ = [
    "David Foss",
    "Gabrian Chua",
    "Rohan Kashyap",
    "Nolan Welch",
    "Kris Jordan",
]
__copyright__ = "Copyright 2025"
__license__ = "MIT"

api = APIRouter(prefix="/api/auth")
openapi_tags = {
    "name": "Authentication",
    "description": "Authentication related operations.",
}

_JWT_SECRET = getenv("JWT_SECRET")
_JST_ALGORITHM = "HS256"


def registered_user(
    user_service: UserService = Depends(),
    token: HTTPAuthorizationCredentials | None = Depends(HTTPBearer()),
) -> User:
    """Returns the authenticated user or raises a 401 HTTPException if the user is not authenticated."""
    if token:
        try:
            auth_info = jwt.decode(
                token.credentials, _JWT_SECRET, algorithms=[_JST_ALGORITHM]
            )
            user = user_service.get(auth_info["spotify_uri"])
            if user:
                return user
        except:
            ...
    raise HTTPException(status_code=401, detail="Unauthorized")


@api.get("/is_authenticated", response_model=bool, tags=["Authentication"])
async def get_is_authenticated(
    token: HTTPAuthorizationCredentials | None = Depends(HTTPBearer()),
):
    return token is not None


def generate_random_string(string_length: int):
    possible = string.ascii_letters + string.digits
    text = "".join(random.choices(possible, k=string_length))
    return text


@api.get("/login", tags=["Authentication"])
async def read_root():
    state = generate_random_string(20)
    scopes = [
        "user-read-private",
        "user-read-playback-state",
        "user-modify-playback-state",
        "user-read-currently-playing",
        "user-read-email",
    ]
    scope = " ".join(scopes)

    params = {
        "response_type": "code",
        "client_id": getenv("CLIENT_ID"),
        "scope": scope,
        "redirect_uri": getenv("REDIRECT_URI"),
        "state": state,
    }
    response = RedirectResponse(
        url="https://accounts.spotify.com/authorize?" + urlencode(params)
    )
    response.set_cookie(key=getenv("STATE_KEY"), value=state)
    response.set_cookie(
        "sessionId",
    )
    return response


@api.get("/oauth/spotify", include_in_schema=False)
async def callback(request: Request, response: Response, db: Session = Depends(get_db)):
    code = request.query_params["code"]
    state = request.query_params["state"]
    stored_state = request.cookies.get(getenv("STATE_KEY"))

    if state is None or state != stored_state:
        raise HTTPException(status_code=400, detail="State mismatch")
    else:
        url = "https://accounts.spotify.com/api/token"
        request_string = getenv("CLIENT_ID") + ":" + getenv("CLIENT_SECRET")
        encoded_bytes = base64.b64encode(request_string.encode("utf-8"))
        encoded_string = str(encoded_bytes, "utf-8")
        headers = {
            "content-type": "application/x-www-form-urlencoded",
            "Authorization": "Basic " + encoded_string,
        }

        form_data = {
            "code": code,
            "redirect_uri": getenv("REDIRECT_URI"),
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
            response = RedirectResponse(url=getenv("URI"))
            if data["product"] != "premium":
                return response
            if data["explicit_content"]["filter_enabled"]:
                return response
            if data["explicit_content"]["filter_locked"]:
                return response

            session = UserSession(
                userUri=data["uri"],
                accessToken=access_token,
                refreshToken=refresh_token,
            )
            db.add(session)
            db.commit()

            response.set_cookie(key="sessionId", value=session.sessionId)

        return response
