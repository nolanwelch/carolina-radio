import React from 'react';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import { CardMedia, Typography } from '@mui/material';
import styles from "./SongPlaying.module.css";
import Song from '../../types/Song';

function SongPlaying(props: {song: Song, className?: String}) {
  return (
    <Card className={styles.card + " " + props.className}>
      <CardContent className={styles.cardContent}>
        <img src={props.song.coverUrl}
          className={styles.albumCover}
          alt="Album art"
        />
        <div className={styles.songInformation}>
          <Typography variant="h6">{props.song.title}</Typography>
          <Typography variant="body1">{props.song.artist}</Typography>
          <Typography variant="body1">Requested by {props.song.requestCount} users</Typography>
        </div>
      </CardContent>
    </Card>
  )
}

export default SongPlaying;