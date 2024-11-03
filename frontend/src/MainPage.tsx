import { Box, Button, CssBaseline, FormControl, FormControlLabel, FormLabel, IconButton, Radio, RadioGroup } from '@mui/material';
import './App.css';
import AppTabs from './components/AppTabs';
import { createTheme, ThemeProvider, useColorScheme } from '@mui/material/styles';
import SongPlaying from './components/SongPlaying/SongPlaying';
import { DarkMode, LightMode } from '@mui/icons-material';
import Song from './types/Song';
import NetworkService from './NetworkService';
import { useEffect, useState } from 'react';
import NowPlayingSong from './types/NowPlayingSong';

export default function MainPage() {
  const { mode, setMode, systemMode } = useColorScheme();
  const [queuedSongs, setQueuedSongs] = useState<Array<Song>>([]);
  const [currentSong, setCurrentSong] = useState<Song>({
    songId: "",
    title: "Nothing!",
    artists: ["Nobody"],
    album: "No Album",
    coverUrl: "https://narcmagazine.com/wp-content/uploads/2024/10/mxmtoon.png",
    lengthMs: 210000,
    requestCount: 0
  } as Song);

  function updateQueue() {
    NetworkService.getQueue().then((songs: Song[]) => setQueuedSongs(songs));
  }

  function updateNowPlaying() {
    NetworkService.getNowPlaying().then((nowPlaying: NowPlayingSong) => {
      setCurrentSong(nowPlaying);
      setTimeout(updateNowPlaying, nowPlaying.lengthMs - nowPlaying.position);
    }).catch(() => {
      setCurrentSong({
        songId: "",
        title: "Nothing!",
        artists: ["Nobody"],
        album: "No Album",
        coverUrl: "https://narcmagazine.com/wp-content/uploads/2024/10/mxmtoon.png",
        lengthMs: 210000,
        requestCount: 0
      } as Song)
    })
  }

  useEffect(() => {
    updateQueue();
    updateNowPlaying();
  }, [])

  if (!mode) {
    setMode(systemMode ?? "dark")
  }; // this should never happen unless on server

  return (
    <>
      <CssBaseline />
      <Box sx={{ position: "fixed", top: 12, right: 12 }}>
        {mode === "light" ?
          <IconButton onClick={() => setMode('dark')}>
            <LightMode />
          </IconButton> :
          <IconButton onClick={() => setMode('light')}>
            <DarkMode />
          </IconButton>}
      </Box>
      <Box sx={{ position: "fixed", top: 12, left: 12, zIndex: -1 }}>
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