import Song from "../../types/Song";
import QueueSong from "../QueueSong/QueueSong";

export default function SongQueue(props: {songs: Song[]}) {
  return props.songs.map(item => 
    <QueueSong />
  );
}