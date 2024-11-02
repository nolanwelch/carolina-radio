import { CssBaseline, FormControl, FormControlLabel, FormLabel, Radio, RadioGroup } from '@mui/material';
import './App.css';
import AppTabs from './components/AppTabs';
import { createTheme, ThemeProvider, useColorScheme } from '@mui/material/styles';
import { useEffect } from 'react';
import SongPlaying from './components/SongPlaying/SongPlaying';
import MainPage from './MainPage';

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
  return (
    <ThemeProvider theme={theme}>
      <MainPage/>
    </ThemeProvider>
  );
}

export default App;