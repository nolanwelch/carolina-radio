@api.get("/playing")
async def get_now_playing(db: Session = Depends(get_db)) -> SongRequestModel | None:
    now_playing = (
        db.query(SongRequestEntity)
        .filter(SongRequestEntity.queue_position == 0)
        .first()
    )

    if not now_playing:
        return None

    pos_ms = (datetime.now(timezone.utc) - now_playing.time_started).total_seconds()
    pos_ms *= 1000

    song = now_playing.song
    return {
        "songId": song.spotify_uri,
        "artists": [a.name for a in song.artists],
        "album": song.album,
        "coverUrl": song.cover_url,
        "durationMs": song.duration_ms,
        "position": pos_ms,
    }


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
        json={
            "uris": [f"spotify:track:{currentSong.songId}"],
            "position_ms": int(pos_ms),
        },
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
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
