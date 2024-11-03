import { Box, Button, CssBaseline, FormControl, FormControlLabel, FormLabel, IconButton, Radio, RadioGroup, Typography } from '@mui/material';
import './App.css';
import AppTabs from './components/AppTabs';
import { createTheme, ThemeProvider, useColorScheme } from '@mui/material/styles';
import SongPlaying from './components/SongPlaying/SongPlaying';
import { DarkMode, Favorite, LightMode } from '@mui/icons-material';
import Song from './types/Song';
import NetworkService from './NetworkService';
import { useEffect, useRef, useState } from 'react';
import NowPlayingSong from './types/NowPlayingSong';
import styles from "./MainPage.module.css";

export default function MainPage() {
  const { mode, setMode, systemMode } = useColorScheme();
  const [queuedSongs, setQueuedSongs] = useState<Array<Song>>([]);
  const [currentSong, setCurrentSong] = useState<Song>({
    songId: "",
    title: "Nothing!",
    artists: ["Nobody"],
    album: "No Album",
    coverUrl: "https://narcmagazine.com/wp-content/uploads/2024/10/mxmtoon.png",
    durationMs: 210000,
    votes: 0
  } as Song);
  const timeoutRef = useRef<ReturnType<typeof setTimeout>>()

  function updateQueue() {
    NetworkService.getQueue().then((songs: Song[]) => setQueuedSongs(songs));
  }

  function updateNowPlaying() {
    updateQueue()
    NetworkService.getNowPlaying().then((nowPlaying: NowPlayingSong) => {
      setCurrentSong(nowPlaying);
      timeoutRef.current = setTimeout(updateNowPlaying, Math.max(500, nowPlaying.durationMs - nowPlaying.position));
      console.log("Will update in " + Math.max(500, nowPlaying.durationMs - nowPlaying.position)/1000)
    }).catch(() => {
      setCurrentSong({
        songId: "",
        title: "Nothing!",
        artists: ["Nobody"],
        album: "No Album",
        coverUrl: "https://narcmagazine.com/wp-content/uploads/2024/10/mxmtoon.png",
        durationMs: 210000,
        votes: 0
      } as Song)
    })
  }

  useEffect(() => {
    updateNowPlaying();
    window.addEventListener("pageshow", () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }

      updateNowPlaying();
    })
  }, [])

  if (!mode) {
    setMode(systemMode ?? "dark")
  }; // this should never happen unless on server

  return (
    <>
      <CssBaseline />
      <Box className={styles.panel}>
        <Typography variant="caption" className={styles.spotifyText}>Made with <Favorite sx={{ width: "16px", transform: "translate(0px, 8px)" }} /> using <img src="/spotify.png" width="16px" height="100%" style={{transform: "translate(0px, 4px)"}}/></Typography>
        {mode === "light" ?
          <IconButton onClick={() => setMode('dark')}>
            <LightMode />
          </IconButton> :
          <IconButton onClick={() => setMode('light')}>
            <DarkMode />
          </IconButton>}
      </Box>
      <Box className={styles.logo}>
        {mode === "light" ?
        <img src="/carolina-radio-light.png" style={{width: 200, height: "100%"}}></img>
        :
        <img src="/carolina-radio-dark.png" style={{width: 200, height: "100%"}}></img>
        }
      </Box>
      <Box sx={{ height: "100vh" }}>
        <Box sx={{ height: "300px", paddingTop: "30px" }}>
          <SongPlaying song={currentSong} />
        </Box>
        <Box sx={{ height: `calc(100vh - 300px)` }}>
          <AppTabs queuedSongs={queuedSongs} />
        </Box>
      </Box>
    </>
  );
}