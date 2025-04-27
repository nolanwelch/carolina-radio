export default interface Song {
  songId: string;
  title: string;
  artists: Array<{ name: string }>;
  album: string;
  coverUrl: string;
  durationMs: number;
  votes: number;
}
