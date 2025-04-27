import { Card, Typography } from '@mui/material';
import styles from "./SongDisplay.module.css";
import Song from '../../types/Song';

export default function SongDisplay(props: {song: Song}) {
  function pad(num: number, size: number) {
    let s = num+"";
    while (s.length < size) s = "0" + s;
    return s;
  }

  return (
    <Card className={styles.cardContent}>
      <div className={styles.albumCover}><img src={props.song.coverUrl} /></div>
      <div className={styles.songInfo}>
        <Typography className={styles.songTitle}>{props.song.title}</Typography>
        <Typography className={styles.artistName}>{props.song.artists.map(artist => artist.name).join(", ")}</Typography>
      </div>
      <Typography className={styles.songLength}>{Math.floor(props.song.durationMs / 1000 / 60)}:{pad(Math.floor(props.song.durationMs / 1000 % 60), 2)}</Typography>
      {/*<Typography className={styles.requestCount}>Requested by {props.song.requestCount} users</Typography>*/}
    </Card>
  );
}