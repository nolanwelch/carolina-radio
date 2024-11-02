import { Box, Button, CssBaseline, FormControl, FormControlLabel, FormLabel, IconButton, Radio, RadioGroup } from '@mui/material';
import './App.css';
import AppTabs from './components/AppTabs';
import { createTheme, ThemeProvider, useColorScheme } from '@mui/material/styles';
import SongPlaying from './components/SongPlaying/SongPlaying';
import { DarkMode, LightMode } from '@mui/icons-material';
import Song from './types/Song';

export default function MainPage() {
  const { mode, setMode, systemMode } = useColorScheme();

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
      <SongPlaying song={{
        title: "Example Song",
        artist: "Example Artist", 
        album: "Example Album",
        coverUrl: "https://narcmagazine.com/wp-content/uploads/2024/10/mxmtoon.png",
        lengthMs: 210000,
        requestCount: 15
      } as Song}/>
      <AppTabs />
    </>
  );
}