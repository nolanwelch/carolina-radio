import QueueSong from "../QueueSong/QueueSong";
import styles from "./MyQueue.module.css";
import { Button, Link, Typography } from "@mui/material";
import { Login } from "@mui/icons-material";
import NetworkService from "../../NetworkService";
import Song from "../../types/Song";
import { useEffect, useState } from "react";
import SongDisplay from "../SongDisplay/SongDisplay";

export default function MyQueue() {
  const [requestedSongs, setRequestedSongs] = useState<Array<Song>>([]);


  return (
    <div className={styles.loggedInDisplay}>
      <QueueSong addSong={(song: Song) => {if (!requestedSongs.map((_song: Song) => _song.songId).includes(song.songId)) {setRequestedSongs([...requestedSongs, song])}}}/>
    </div>
  )
}