import { CssBaseline, FormControl, FormControlLabel, FormLabel, Radio, RadioGroup } from '@mui/material';
import './App.css';
import AppTabs from './components/AppTabs';
import { createTheme, ThemeProvider, useColorScheme } from '@mui/material/styles';
import SongPlaying from './components/SongPlaying/SongPlaying';

export default function MainPage() {
  const { mode, setMode, systemMode } = useColorScheme();

  if (!mode) {
    setMode(systemMode ?? "dark")
  }; // this should never happen unless on server

  return (
    <>
      <CssBaseline />
      <FormControl>
        <FormLabel id="demo-theme-toggle">Theme</FormLabel>
        <RadioGroup
          aria-labelledby="demo-theme-toggle"
          name="theme-toggle"
          row
          value={mode ?? "dark"}
          onChange={(event) => {
            setMode(event.target.value as 'light' | 'dark' | 'system')
          }
          }
        >
          <FormControlLabel value="system" control={<Radio />} label="System" />
          <FormControlLabel value="light" control={<Radio />} label="Light" />
          <FormControlLabel value="dark" control={<Radio />} label="Dark" />
        </RadioGroup>
      </FormControl>
      <SongPlaying />
      <AppTabs />
    </>
  );
}