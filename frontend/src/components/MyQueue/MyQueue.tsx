import QueueSong from "../QueueSong/QueueSong";
import styles from "./MyQueue.module.css";
import { Button, Link, Typography } from "@mui/material";
import { Login } from "@mui/icons-material";
import NetworkService from "../../NetworkService";
import Song from "../../types/Song";
import { useEffect, useState } from "react";
import SongDisplay from "../SongDisplay/SongDisplay";

export default function MyQueue() {
  const [isSignedIn, setIsSignedIn] = useState(false);

  useEffect(() => {
    NetworkService.isLoggedIn().then((value: boolean) => setIsSignedIn(value));
  }, [])
  const [requestedSongs, setRequestedSongs] = useState<Array<Song>>([]);

  useEffect(()=> {
    if (isSignedIn) {
      NetworkService.getRequestedSongs().then((songs: Song[]) => setRequestedSongs(songs));
    }
  }, []);

  if (isSignedIn) {
    return (
      <div className={styles.loggedInDisplay}>
        <QueueSong addSong={(song: Song) => {if (!requestedSongs.map((_song: Song) => _song.songId).includes(song.songId)) {setRequestedSongs([...requestedSongs, song])}}}/>
        <Typography variant="h6">Your Requested Songs</Typography>
        <div className={styles.requestedSongsContainer}>
          {
            requestedSongs.length > 0 ? 
            requestedSongs.map((requestedSong: Song) => {
              return <SongDisplay key={requestedSong.songId} song={requestedSong} />
            })
            :
            <Typography variant="body1">You don't have any songs waiting.</Typography>
          }
        </div>
      </div>
    )
  } else {
    return (
      <div className={styles.loggedOutDisplay}>
        <Typography variant="h6">You must be logged in to add to the queue</Typography>
        <Button component={Link} href={process.env.REACT_APP_API_URL + "/login"} variant="contained" startIcon={<Login />}>
          Sign in
        </Button>
      </div>
    )
  } 
}