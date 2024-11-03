import './App.css';
import { createTheme, ThemeProvider } from '@mui/material/styles';
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
    background: {
      paper: '#EEEEEE'
    }
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