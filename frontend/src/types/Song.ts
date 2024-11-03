export default interface Song {
    spotifyUri: string,
    title: string;
    artists: Array<string>;
    album: string;
    coverUrl: string;
    lengthMs: number;
    requestCount: number;
}