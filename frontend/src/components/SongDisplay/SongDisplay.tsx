import { Card, CardContent, Typography } from '@mui/material';
import React, { useState } from 'react';
import styles from "./SongDisplay.module.css";

export default function SongDisplay() {
  // Declare a new state variable, which we'll call "count"  const [count, setCount] = useState(0);
  return (
    <Card className={styles.cardContent}>
      <div className={styles.albumCover}><img src={"https://narcmagazine.com/wp-content/uploads/2024/10/mxmtoon.png"} /></div>
      <div className={styles.songInfo}>
        <Typography className={styles.songTitle}>Song Title</Typography>
        <Typography className={styles.artistName}>Artist Name</Typography>
      </div>
      <Typography className={styles.songLength}>Song Length</Typography>
      <Typography className={styles.requestCount}>Request count</Typography>
    </Card>
  );
}