import { CssBaseline, FormControl, FormControlLabel, FormLabel, Radio, RadioGroup } from '@mui/material';
import './App.css';
import AppTabs from './components/AppTabs';
import { createTheme, ThemeProvider, useColorScheme } from '@mui/material/styles';
import { useEffect } from 'react';
import SongPlaying from './components/SongPlaying/SongPlaying';

const theme = createTheme({
  colorSchemes: {
    dark: true
  },
  palette: {
    primary: {
      main: '#7BAFD4',
    },
    secondary: {
      main: '#C4D600',
    },
  },
});

function App() {
  const { mode, setMode } = useColorScheme();

  useEffect(() => {
    console.log(mode);
  }, [mode]);

  if (!mode) {
    console.log("mode was falsey! set to system");
    setMode('system');
  }; // this should never happen unless on server

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <FormControl>
        <FormLabel id="demo-theme-toggle">Theme</FormLabel>
        <RadioGroup
          aria-labelledby="demo-theme-toggle"
          name="theme-toggle"
          row
          value={mode}
          onChange={(event) =>
            setMode(event.target.value as 'system' | 'light' | 'dark')
          }
        >
          <FormControlLabel value="system" control={<Radio />} label="System" />
          <FormControlLabel value="light" control={<Radio />} label="Light" />
          <FormControlLabel value="dark" control={<Radio />} label="Dark" />
        </RadioGroup>
      </FormControl>
      <SongPlaying />
      <AppTabs />
    </ThemeProvider>
  );
}

export default App;