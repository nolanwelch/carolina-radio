import React from 'react';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import { CardMedia, Typography } from '@mui/material';

function SongPlaying() {
  return (
    <Card sx={{ textAlign: "center", width: "fit-content" }}>
      <CardContent>
        <img src="/album-art-tmp.png"
          style={{ height: "100%", width: 200, textAlign: "center" }}
          alt="Album art"
        />
        <Typography variant="h6">Song Title</Typography>
        <Typography variant="body1">Artist Name</Typography>
        <Typography variant="body1">Requested by 120</Typography>
      </CardContent>
    </Card>
  )
}

export default SongPlaying;