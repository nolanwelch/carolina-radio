import { Card, CardContent, Typography } from '@mui/material';
import React, { useState } from 'react';
import styles from "./SongDisplay.module.css";
import Song from '../../types/Song';

export default function SongDisplay(props: {song: Song}) {
  return (
    <Card className={styles.cardContent}>
      <div className={styles.albumCover}><img src={props.song.coverUrl} /></div>
      <div className={styles.songInfo}>
        <Typography className={styles.songTitle}>{props.song.title}</Typography>
        <Typography className={styles.artistName}>{props.song.artist}</Typography>
      </div>
      <Typography className={styles.songLength}>{Math.floor(props.song.lengthMs / 1000 / 60)}:{Math.floor(props.song.lengthMs / 1000 % 60)}</Typography>
      <Typography className={styles.requestCount}>Requested by {props.song.requestCount} users</Typography>
    </Card>
  );
}