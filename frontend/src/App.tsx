import { CssBaseline } from '@mui/material';
import './App.css';
import AppTabs from './components/AppTabs';
import SongPlaying from './components/SongPlaying';
import { createTheme, ThemeOptions, ThemeProvider } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    mode: 'dark',
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
      <CssBaseline />
      <SongPlaying />
      <AppTabs />
    </ThemeProvider>
  );
}

export default App;
