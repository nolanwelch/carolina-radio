import * as React from 'react';
import TextField from '@mui/material/TextField';
import Stack from '@mui/material/Stack';
import Autocomplete from '@mui/material/Autocomplete';
import { debounce } from '@mui/material/utils'; 
import NetworkService from '../../NetworkService';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import Song from '../../types/Song';

export default function QueueSong() {
  const [value, setValue] = React.useState<Song | null>(null);
  const [inputValue, setInputValue] = React.useState('');
  const [options, setOptions] = React.useState<readonly Song[]>([]);
  const loaded = React.useRef(false);
  const searchTimeout = React.useRef<ReturnType<typeof setTimeout>|null>();

  React.useEffect(() => {
    let active = true;

    if (inputValue === '') {
      setOptions(value ? [value] : []);
      return undefined;
    }

    if (searchTimeout != null) {
      clearTimeout(searchTimeout.current as ReturnType<typeof setTimeout>)
    }
    searchTimeout.current = setTimeout(() => {
      NetworkService.getSearchSong(inputValue).then((songs: Song[]) => {
        setOptions(songs)
      })
      searchTimeout.current = null;
    }, 500)
    

    return () => {
      active = false;
    };
  }, [value, inputValue, fetch]);

  return (
    <Autocomplete
      sx={{ width: 300 }}
      getOptionLabel={(option) =>
        typeof option === 'string' ? option : option.title
      }
      filterOptions={(x) => x}
      options={options}
      autoComplete
      includeInputInList
      filterSelectedOptions
      value={value}
      noOptionsText="No Matching Songs"
      onChange={(event: any, newValue: Song | null) => {
        setOptions(newValue ? [newValue, ...options] : options);
        setValue(newValue);
      }}
      onInputChange={(event, newInputValue) => {
        setInputValue(newInputValue);
      }}
      renderInput={(params) => (
        <TextField {...params} label="Song to Queue" fullWidth />
      )}
      renderOption={(props, option) => {
        const { key, ...optionProps } = props;

        return (
          <li key={key} {...optionProps}>
            <Grid container sx={{ alignItems: 'center' }}>
              <Grid item sx={{ width: 'calc(100% - 44px)', wordWrap: 'break-word' }}>
                <Box
                    component="span"
                    sx={{ fontWeight: 'regular' }}
                  >
                    {option.title}
                  </Box>
                <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                    {option.artists.join(", ")}
                </Typography>
              </Grid>
            </Grid>
          </li>
        );
      }}
    />
  );
}
