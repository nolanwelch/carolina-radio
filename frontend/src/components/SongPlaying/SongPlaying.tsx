import React from 'react';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import { CardMedia, Typography } from '@mui/material';
import styles from "./SongPlaying.module.css";

function SongPlaying() {
  return (
    <Card className={styles.card}>
      <CardContent>
        <img src="/album-art-tmp.png"
          className={styles.albumCover}
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